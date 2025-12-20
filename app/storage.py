"""
Storage module for managing issues and notes persistently using JSON files.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class Storage:
    """
    A storage class for managing issues and notes persistently using JSON files.
    
    This class provides methods to create, read, update, and delete issues and notes,
    with data persisted to JSON files on disk.
    """
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the Storage instance.
        
        Args:
            data_dir: Directory path where JSON files will be stored.
                     Defaults to "data".
        """
        self.data_dir = Path(data_dir)
        self.issues_file = self.data_dir / "issues.json"
        self.notes_file = self.data_dir / "notes.json"
        
        # Create data directory if it doesn't exist
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize JSON files if they don't exist
        self._initialize_files()
    
    def _initialize_files(self) -> None:
        """Initialize JSON files with empty structures if they don't exist."""
        if not self.issues_file.exists():
            self._write_json(self.issues_file, {})
        
        if not self.notes_file.exists():
            self._write_json(self.notes_file, {})
    
    def _read_json(self, file_path: Path) -> Dict[str, Any]:
        """
        Read and parse a JSON file.
        
        Args:
            file_path: Path to the JSON file.
            
        Returns:
            Dictionary containing the parsed JSON data.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _write_json(self, file_path: Path, data: Dict[str, Any]) -> None:
        """
        Write data to a JSON file.
        
        Args:
            file_path: Path to the JSON file.
            data: Dictionary to write as JSON.
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    # ==================== Issues Methods ====================
    
    def create_issue(
        self,
        issue_id: str,
        title: str,
        description: str,
        severity: str = "info",
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new issue.
        
        Args:
            issue_id: Unique identifier for the issue.
            title: Title of the issue.
            description: Detailed description of the issue.
            severity: Severity level (e.g., "info", "warning", "error"). Defaults to "info".
            tags: List of tags associated with the issue.
            metadata: Additional metadata as a dictionary.
            
        Returns:
            The created issue dictionary.
        """
        issues = self._read_json(self.issues_file)
        
        issue = {
            "id": issue_id,
            "title": title,
            "description": description,
            "severity": severity,
            "tags": tags or [],
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        issues[issue_id] = issue
        self._write_json(self.issues_file, issues)
        
        return issue
    
    def get_issue(self, issue_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an issue by ID.
        
        Args:
            issue_id: The ID of the issue to retrieve.
            
        Returns:
            The issue dictionary, or None if not found.
        """
        issues = self._read_json(self.issues_file)
        return issues.get(issue_id)
    
    def get_all_issues(self) -> Dict[str, Dict[str, Any]]:
        """
        Retrieve all issues.
        
        Returns:
            Dictionary of all issues, keyed by issue ID.
        """
        return self._read_json(self.issues_file)
    
    def update_issue(self, issue_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Update an existing issue with new data.
        
        Args:
            issue_id: The ID of the issue to update.
            **kwargs: Fields to update (title, description, severity, tags, metadata, etc.).
            
        Returns:
            The updated issue dictionary, or None if issue not found.
        """
        issues = self._read_json(self.issues_file)
        
        if issue_id not in issues:
            return None
        
        issue = issues[issue_id]
        
        # Update allowed fields
        for key, value in kwargs.items():
            if key not in ["id", "created_at"]:  # Prevent overwriting id and creation time
                issue[key] = value
        
        issue["updated_at"] = datetime.utcnow().isoformat()
        issues[issue_id] = issue
        self._write_json(self.issues_file, issues)
        
        return issue
    
    def delete_issue(self, issue_id: str) -> bool:
        """
        Delete an issue by ID.
        
        Args:
            issue_id: The ID of the issue to delete.
            
        Returns:
            True if the issue was deleted, False if not found.
        """
        issues = self._read_json(self.issues_file)
        
        if issue_id not in issues:
            return False
        
        del issues[issue_id]
        self._write_json(self.issues_file, issues)
        
        return True
    
    def get_issues_by_severity(self, severity: str) -> Dict[str, Dict[str, Any]]:
        """
        Retrieve all issues with a specific severity level.
        
        Args:
            severity: The severity level to filter by.
            
        Returns:
            Dictionary of issues matching the severity, keyed by issue ID.
        """
        issues = self._read_json(self.issues_file)
        return {
            issue_id: issue
            for issue_id, issue in issues.items()
            if issue.get("severity") == severity
        }
    
    def get_issues_by_tag(self, tag: str) -> Dict[str, Dict[str, Any]]:
        """
        Retrieve all issues with a specific tag.
        
        Args:
            tag: The tag to filter by.
            
        Returns:
            Dictionary of issues containing the tag, keyed by issue ID.
        """
        issues = self._read_json(self.issues_file)
        return {
            issue_id: issue
            for issue_id, issue in issues.items()
            if tag in issue.get("tags", [])
        }
    
    # ==================== Notes Methods ====================
    
    def create_note(
        self,
        note_id: str,
        content: str,
        issue_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new note.
        
        Args:
            note_id: Unique identifier for the note.
            content: The content of the note.
            issue_id: Optional ID of the associated issue.
            metadata: Additional metadata as a dictionary.
            
        Returns:
            The created note dictionary.
        """
        notes = self._read_json(self.notes_file)
        
        note = {
            "id": note_id,
            "content": content,
            "issue_id": issue_id,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        notes[note_id] = note
        self._write_json(self.notes_file, notes)
        
        return note
    
    def get_note(self, note_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a note by ID.
        
        Args:
            note_id: The ID of the note to retrieve.
            
        Returns:
            The note dictionary, or None if not found.
        """
        notes = self._read_json(self.notes_file)
        return notes.get(note_id)
    
    def get_all_notes(self) -> Dict[str, Dict[str, Any]]:
        """
        Retrieve all notes.
        
        Returns:
            Dictionary of all notes, keyed by note ID.
        """
        return self._read_json(self.notes_file)
    
    def update_note(self, note_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Update an existing note with new data.
        
        Args:
            note_id: The ID of the note to update.
            **kwargs: Fields to update (content, issue_id, metadata, etc.).
            
        Returns:
            The updated note dictionary, or None if note not found.
        """
        notes = self._read_json(self.notes_file)
        
        if note_id not in notes:
            return None
        
        note = notes[note_id]
        
        # Update allowed fields
        for key, value in kwargs.items():
            if key not in ["id", "created_at"]:  # Prevent overwriting id and creation time
                note[key] = value
        
        note["updated_at"] = datetime.utcnow().isoformat()
        notes[note_id] = note
        self._write_json(self.notes_file, notes)
        
        return note
    
    def delete_note(self, note_id: str) -> bool:
        """
        Delete a note by ID.
        
        Args:
            note_id: The ID of the note to delete.
            
        Returns:
            True if the note was deleted, False if not found.
        """
        notes = self._read_json(self.notes_file)
        
        if note_id not in notes:
            return False
        
        del notes[note_id]
        self._write_json(self.notes_file, notes)
        
        return True
    
    def get_notes_by_issue(self, issue_id: str) -> Dict[str, Dict[str, Any]]:
        """
        Retrieve all notes associated with a specific issue.
        
        Args:
            issue_id: The ID of the issue.
            
        Returns:
            Dictionary of notes for the issue, keyed by note ID.
        """
        notes = self._read_json(self.notes_file)
        return {
            note_id: note
            for note_id, note in notes.items()
            if note.get("issue_id") == issue_id
        }
    
    # ==================== Utility Methods ====================
    
    def export_to_json(self, file_path: str) -> None:
        """
        Export all issues and notes to a JSON file.
        
        Args:
            file_path: Path where the export file will be saved.
        """
        export_data = {
            "issues": self._read_json(self.issues_file),
            "notes": self._read_json(self.notes_file),
            "exported_at": datetime.utcnow().isoformat()
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    def import_from_json(self, file_path: str, overwrite: bool = False) -> None:
        """
        Import issues and notes from a JSON file.
        
        Args:
            file_path: Path to the JSON file to import.
            overwrite: If True, replace existing data. If False, merge with existing data.
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            import_data = json.load(f)
        
        if overwrite:
            self._write_json(self.issues_file, import_data.get("issues", {}))
            self._write_json(self.notes_file, import_data.get("notes", {}))
        else:
            # Merge with existing data
            existing_issues = self._read_json(self.issues_file)
            existing_issues.update(import_data.get("issues", {}))
            self._write_json(self.issues_file, existing_issues)
            
            existing_notes = self._read_json(self.notes_file)
            existing_notes.update(import_data.get("notes", {}))
            self._write_json(self.notes_file, existing_notes)
    
    def clear_all(self) -> None:
        """Clear all issues and notes."""
        self._write_json(self.issues_file, {})
        self._write_json(self.notes_file, {})
