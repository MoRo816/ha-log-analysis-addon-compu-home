"""
Data models for HA Log Analysis Dashboard.

This module contains Pydantic models for representing issues, integrations,
statistics, and filtering options in the Home Assistant log analysis system.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class IssueStatus(str, Enum):
    """Enumeration of possible issue statuses."""

    NEW = "NEW"
    INVESTIGATING = "INVESTIGATING"
    IGNORED = "IGNORED"
    RESOLVED = "RESOLVED"


class IssueSeverity(str, Enum):
    """Enumeration of possible issue severity levels."""

    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"


class Integration(BaseModel):
    """Model representing a Home Assistant integration."""

    name: str = Field(..., description="Name of the integration")
    issue_count: int = Field(default=0, description="Number of issues related to this integration")


class Issue(BaseModel):
    """Model representing a detected issue in Home Assistant logs."""

    id: str = Field(..., description="Unique identifier for the issue")
    title: str = Field(..., description="Brief title of the issue")
    description: str = Field(..., description="Detailed description of the issue")
    integration: str = Field(..., description="Name of the integration related to this issue")
    status: IssueStatus = Field(default=IssueStatus.NEW, description="Current status of the issue")
    severity: IssueSeverity = Field(..., description="Severity level of the issue")
    first_detected: datetime = Field(..., description="Timestamp when the issue was first detected")
    last_seen: datetime = Field(..., description="Timestamp when the issue was last seen")
    count: int = Field(default=1, description="Number of times this issue has occurred")
    recommendation: Optional[str] = Field(default=None, description="Recommended action to resolve the issue")
    notes: Optional[str] = Field(default=None, description="Additional notes about the issue")
    tags: List[str] = Field(default_factory=list, description="Tags for categorizing the issue")


class Statistics(BaseModel):
    """Model representing aggregated statistics about detected issues."""

    total_issues: int = Field(default=0, description="Total number of issues detected")
    critical_count: int = Field(default=0, description="Number of critical severity issues")
    warning_count: int = Field(default=0, description="Number of warning severity issues")
    info_count: int = Field(default=0, description="Number of info severity issues")
    resolved_count: int = Field(default=0, description="Number of resolved issues")
    by_integration: Dict[str, int] = Field(
        default_factory=dict,
        description="Count of issues grouped by integration name",
    )
    by_status: Dict[str, int] = Field(
        default_factory=dict,
        description="Count of issues grouped by status",
    )
    by_severity: Dict[str, int] = Field(
        default_factory=dict,
        description="Count of issues grouped by severity level",
    )


class IssueFilter(BaseModel):
    """Model for filtering and searching issues."""

    integration: Optional[str] = Field(default=None, description="Filter by integration name")
    status: Optional[IssueStatus] = Field(default=None, description="Filter by issue status")
    severity: Optional[IssueSeverity] = Field(default=None, description="Filter by severity level")
    search: Optional[str] = Field(default=None, description="Full-text search query")
    date_start: Optional[datetime] = Field(default=None, description="Filter issues detected after this date")
    date_end: Optional[datetime] = Field(default=None, description="Filter issues detected before this date")
