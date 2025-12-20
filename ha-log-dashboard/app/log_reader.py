"""
Log reader module for accessing Home Assistant logs from systemd journal.

This module provides functionality to read and parse Home Assistant logs
from the systemd journal instead of traditional log files.
"""

import json
import logging
import re
import subprocess
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class JournalReader:
    """
    A class for reading Home Assistant logs from systemd journal.
    
    This class provides methods to query the systemd journal for Home Assistant
    logs and parse them into structured data.
    """
    
    def __init__(self, unit_name: str = "home-assistant"):
        """
        Initialize the JournalReader.
        
        Args:
            unit_name: The systemd unit name to filter logs for.
                      Defaults to "home-assistant".
        """
        self.unit_name = unit_name
        self._verify_journalctl()
    
    def _verify_journalctl(self) -> None:
        """
        Verify that journalctl is available on the system.
        
        Raises:
            RuntimeError: If journalctl is not available or not accessible.
        """
        try:
            result = subprocess.run(
                ["journalctl", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                raise RuntimeError("journalctl is not accessible")
            logger.info("journalctl is available and accessible")
        except FileNotFoundError:
            raise RuntimeError("journalctl command not found on system")
        except subprocess.TimeoutExpired:
            raise RuntimeError("journalctl verification timed out")
    
    def read_logs(
        self,
        limit: int = 100,
        offset: int = 0,
        level: Optional[str] = None,
        service: Optional[str] = None,
        since: Optional[str] = None,
        until: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Read logs from the systemd journal.
        
        Args:
            limit: Maximum number of log entries to return.
            offset: Number of entries to skip (for pagination).
            level: Filter by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
            service: Filter by service/component name.
            since: Start time for log entries (e.g., "2025-01-01", "1 hour ago").
            until: End time for log entries.
            
        Returns:
            List of log entries as dictionaries.
            
        Note:
            For large offsets, this method fetches (limit + offset) entries and slices
            in memory. For better performance with large offsets, consider implementing
            cursor-based pagination using journalctl's --after-cursor option.
        """
        try:
            # Build journalctl command with limit for efficiency
            # Note: journalctl doesn't support offset directly, so we fetch limit+offset entries
            # and slice in memory. For very large offsets, consider cursor-based pagination.
            fetch_count = limit + offset
            
            cmd = ["journalctl", "-u", self.unit_name, "-o", "json", "--no-pager", "-n", str(fetch_count)]
            
            # Add time range filters
            if since:
                cmd.extend(["--since", since])
            if until:
                cmd.extend(["--until", until])
            
            # Add priority filter based on log level
            if level:
                priority = self._level_to_priority(level)
                if priority is not None:
                    cmd.extend(["-p", str(priority)])
            
            # Execute journalctl
            logger.info(f"Executing journalctl command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.error(f"journalctl failed: {result.stderr}")
                return []
            
            # Parse JSON output
            logs = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    parsed_log = self._parse_journal_entry(entry, service)
                    if parsed_log:
                        logs.append(parsed_log)
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse journal entry: {e}")
                    continue
            
            # Apply offset to skip entries (in-memory pagination)
            return logs[offset:offset + limit]
            
        except subprocess.TimeoutExpired:
            logger.error("journalctl command timed out")
            return []
        except Exception as e:
            logger.error(f"Error reading logs from journal: {e}")
            return []
    
    def _level_to_priority(self, level: str) -> Optional[int]:
        """
        Convert log level string to systemd journal priority.
        
        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
            
        Returns:
            Integer priority value for journalctl, or None if invalid.
        """
        level_map = {
            "DEBUG": 7,      # debug
            "INFO": 6,       # info
            "WARNING": 4,    # warning
            "ERROR": 3,      # err
            "CRITICAL": 2    # crit
        }
        return level_map.get(level.upper())
    
    def _parse_journal_entry(
        self,
        entry: Dict[str, Any],
        service_filter: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Parse a systemd journal entry into a structured log entry.
        
        Args:
            entry: Raw journal entry from journalctl JSON output.
            service_filter: Optional service name to filter by.
            
        Returns:
            Parsed log entry dictionary, or None if entry should be filtered out.
        """
        try:
            # Extract message
            message = entry.get("MESSAGE", "")
            
            # Try to parse Home Assistant log format
            # Format: YYYY-MM-DD HH:MM:SS LEVEL (component) message
            log_pattern = r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+(\w+)\s+\(([^)]+)\)\s+(.*)'
            match = re.match(log_pattern, message)
            
            if match:
                timestamp_str, level, component, log_message = match.groups()
                
                # Apply service filter if specified
                if service_filter and service_filter.lower() not in component.lower():
                    return None
                
                # Parse timestamp
                try:
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    # Ensure timezone awareness (assume UTC for HA logs)
                    timestamp = timestamp.replace(tzinfo=timezone.utc)
                except ValueError:
                    timestamp = self._parse_journal_timestamp(entry)
                
                return {
                    "id": entry.get("__CURSOR", ""),
                    "timestamp": timestamp.isoformat(),
                    "level": level,
                    "service": component,
                    "message": log_message,
                    "unit": entry.get("_SYSTEMD_UNIT", ""),
                    "pid": entry.get("_PID", ""),
                    "hostname": entry.get("_HOSTNAME", "")
                }
            else:
                # Fallback: use journal entry fields directly
                timestamp = self._parse_journal_timestamp(entry)
                
                # Parse priority safely with fallback
                try:
                    priority = int(entry.get("PRIORITY", "6"))
                except (ValueError, TypeError):
                    priority = 6  # Default to INFO level
                    
                level = self._priority_to_level(priority)
                
                return {
                    "id": entry.get("__CURSOR", ""),
                    "timestamp": timestamp.isoformat(),
                    "level": level,
                    "service": entry.get("SYSLOG_IDENTIFIER", "unknown"),
                    "message": message,
                    "unit": entry.get("_SYSTEMD_UNIT", ""),
                    "pid": entry.get("_PID", ""),
                    "hostname": entry.get("_HOSTNAME", "")
                }
                
        except Exception as e:
            logger.warning(f"Failed to parse journal entry: {e}")
            return None
    
    def _parse_journal_timestamp(self, entry: Dict[str, Any]) -> datetime:
        """
        Parse timestamp from journal entry.
        
        Args:
            entry: Journal entry dictionary.
            
        Returns:
            Parsed datetime object.
        """
        # Try __REALTIME_TIMESTAMP first (microseconds since epoch)
        if "__REALTIME_TIMESTAMP" in entry:
            timestamp_us = int(entry["__REALTIME_TIMESTAMP"])
            return datetime.fromtimestamp(timestamp_us / 1000000, tz=timezone.utc)
        
        # Fallback to current time
        return datetime.now(timezone.utc)
    
    def _priority_to_level(self, priority: int) -> str:
        """
        Convert systemd journal priority to log level string.
        
        Args:
            priority: Integer priority value.
            
        Returns:
            Log level string.
        """
        if priority <= 2:
            return "CRITICAL"
        elif priority == 3:
            return "ERROR"
        elif priority == 4:
            return "WARNING"
        elif priority <= 6:
            return "INFO"
        else:
            return "DEBUG"
    
    def get_log_statistics(self, max_logs: int = 10000) -> Dict[str, Any]:
        """
        Get statistics about logs in the journal.
        
        Args:
            max_logs: Maximum number of logs to analyze for statistics.
                     Default is 10000 to balance accuracy with performance.
        
        Returns:
            Dictionary containing log statistics.
        """
        try:
            # Get recent logs with a reasonable limit for statistics
            all_logs = self.read_logs(limit=max_logs)
            
            stats = {
                "total_logs": len(all_logs),
                "by_level": {
                    "DEBUG": 0,
                    "INFO": 0,
                    "WARNING": 0,
                    "ERROR": 0,
                    "CRITICAL": 0
                },
                "by_service": {},
                "time_range": {
                    "start": None,
                    "end": None
                }
            }
            
            # Count by level and service
            for log in all_logs:
                level = log.get("level", "INFO")
                service = log.get("service", "unknown")
                
                if level in stats["by_level"]:
                    stats["by_level"][level] += 1
                
                if service not in stats["by_service"]:
                    stats["by_service"][service] = 0
                stats["by_service"][service] += 1
            
            # Get time range
            if all_logs:
                timestamps = [log["timestamp"] for log in all_logs]
                stats["time_range"]["start"] = min(timestamps)
                stats["time_range"]["end"] = max(timestamps)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting log statistics: {e}")
            return {
                "total_logs": 0,
                "by_level": {},
                "by_service": {},
                "time_range": {"start": None, "end": None}
            }
    
    def get_log_by_id(self, log_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific log entry by its cursor ID.
        
        Args:
            log_id: The journal cursor ID of the log entry.
            
        Returns:
            Log entry dictionary, or None if not found.
        """
        try:
            # Use journalctl with cursor to get specific entry
            cmd = [
                "journalctl",
                "-u", self.unit_name,
                "-o", "json",
                "--no-pager",
                "--cursor", log_id,
                "-n", "1"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return None
            
            # Parse the single entry
            for line in result.stdout.strip().split('\n'):
                if line:
                    entry = json.loads(line)
                    return self._parse_journal_entry(entry)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting log by ID: {e}")
            return None
