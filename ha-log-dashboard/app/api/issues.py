"""
FastAPI router for issue management endpoints.

This module provides REST API endpoints for managing issues including:
- Listing all issues with filtering and pagination
- Creating new issues
- Retrieving individual issues
- Updating issue details
- Deleting issues
- Updating issue status
- Adding notes to issues
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

# Initialize router
router = APIRouter(prefix="/issues", tags=["issues"])


# ============================================================================
# Pydantic Models
# ============================================================================

class IssueNote(BaseModel):
    """Model for notes attached to issues."""
    id: str = Field(..., description="Unique identifier for the note")
    content: str = Field(..., description="Content of the note")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when note was created")
    author: str = Field(..., description="Author of the note")


class IssueCreate(BaseModel):
    """Model for creating a new issue."""
    title: str = Field(..., min_length=1, max_length=255, description="Issue title")
    description: str = Field(default="", description="Detailed description of the issue")
    severity: str = Field(default="medium", pattern="^(low|medium|high|critical)$", description="Issue severity level")
    category: str = Field(default="", description="Issue category or component")
    source: str = Field(default="", description="Source of the issue (e.g., log file, user report)")


class IssueUpdate(BaseModel):
    """Model for updating an existing issue."""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Issue title")
    description: Optional[str] = Field(None, description="Detailed description of the issue")
    severity: Optional[str] = Field(None, pattern="^(low|medium|high|critical)$", description="Issue severity level")
    category: Optional[str] = Field(None, description="Issue category or component")
    source: Optional[str] = Field(None, description="Source of the issue")


class IssueStatusUpdate(BaseModel):
    """Model for updating issue status."""
    status: str = Field(..., pattern="^(open|in_progress|resolved|closed|reopened)$", description="New status for the issue")
    reason: Optional[str] = Field(None, description="Reason for status change")


class NoteCreate(BaseModel):
    """Model for creating a note on an issue."""
    content: str = Field(..., min_length=1, description="Content of the note")
    author: str = Field(..., description="Author of the note")


class Issue(BaseModel):
    """Complete issue model."""
    id: str = Field(..., description="Unique identifier for the issue")
    title: str = Field(..., description="Issue title")
    description: str = Field(default="", description="Detailed description of the issue")
    severity: str = Field(default="medium", description="Issue severity level")
    category: str = Field(default="", description="Issue category or component")
    source: str = Field(default="", description="Source of the issue")
    status: str = Field(default="open", description="Current status of the issue")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when issue was created")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when issue was last updated")
    notes: List[IssueNote] = Field(default_factory=list, description="List of notes attached to the issue")
    assignee: Optional[str] = Field(None, description="User assigned to resolve this issue")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "issue-001",
                "title": "Home Assistant service restart failures",
                "description": "Service occasionally fails to restart properly",
                "severity": "high",
                "category": "services",
                "source": "log_analysis",
                "status": "in_progress",
                "created_at": "2025-12-20T17:51:36Z",
                "updated_at": "2025-12-20T17:51:36Z",
                "notes": [],
                "assignee": "admin"
            }
        }


class IssueListResponse(BaseModel):
    """Response model for listing issues."""
    total: int = Field(..., description="Total number of issues")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    items: List[Issue] = Field(..., description="List of issues")


# ============================================================================
# Endpoints
# ============================================================================

@router.get("", response_model=IssueListResponse, summary="List all issues")
async def list_issues(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of items to return"),
    status: Optional[str] = Query(None, description="Filter by status (open, in_progress, resolved, closed, reopened)"),
    severity: Optional[str] = Query(None, description="Filter by severity (low, medium, high, critical)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search in title and description"),
) -> IssueListResponse:
    """
    Retrieve a paginated list of all issues with optional filtering.
    
    Query Parameters:
    - skip: Number of items to skip (for pagination)
    - limit: Maximum number of items to return (default: 20, max: 100)
    - status: Filter by issue status
    - severity: Filter by severity level
    - category: Filter by category
    - search: Search string to filter by title/description
    
    Returns:
    - List of issues matching the criteria with pagination metadata
    """
    # TODO: Implement database query with filters
    # This is a placeholder implementation
    return IssueListResponse(
        total=0,
        page=skip // limit + 1,
        page_size=limit,
        items=[]
    )


@router.post("", response_model=Issue, status_code=status.HTTP_201_CREATED, summary="Create a new issue")
async def create_issue(issue_data: IssueCreate) -> Issue:
    """
    Create a new issue.
    
    Request Body:
    - title: Issue title (required)
    - description: Detailed description
    - severity: low, medium, high, critical
    - category: Issue category
    - source: Source of the issue
    
    Returns:
    - Created issue with assigned ID
    """
    # TODO: Implement database insert
    # This is a placeholder implementation
    new_issue = Issue(
        id="issue-001",
        title=issue_data.title,
        description=issue_data.description,
        severity=issue_data.severity,
        category=issue_data.category,
        source=issue_data.source,
        status="open",
        notes=[]
    )
    return new_issue


@router.get("/{issue_id}", response_model=Issue, summary="Get issue details")
async def get_issue(issue_id: str) -> Issue:
    """
    Retrieve detailed information about a specific issue.
    
    Path Parameters:
    - issue_id: Unique identifier of the issue
    
    Returns:
    - Issue details including all notes and metadata
    
    Raises:
    - 404: Issue not found
    """
    # TODO: Implement database query by ID
    # This is a placeholder implementation
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Issue with ID '{issue_id}' not found"
    )


@router.put("/{issue_id}", response_model=Issue, summary="Update issue details")
async def update_issue(
    issue_id: str,
    update_data: IssueUpdate
) -> Issue:
    """
    Update an existing issue's details.
    
    Path Parameters:
    - issue_id: Unique identifier of the issue
    
    Request Body:
    - title: New issue title (optional)
    - description: New description (optional)
    - severity: New severity level (optional)
    - category: New category (optional)
    - source: New source (optional)
    
    Returns:
    - Updated issue
    
    Raises:
    - 404: Issue not found
    """
    # TODO: Implement database update
    # This is a placeholder implementation
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Issue with ID '{issue_id}' not found"
    )


@router.delete("/{issue_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete an issue")
async def delete_issue(issue_id: str) -> None:
    """
    Delete an issue and all associated data.
    
    Path Parameters:
    - issue_id: Unique identifier of the issue
    
    Raises:
    - 404: Issue not found
    """
    # TODO: Implement database delete
    # This is a placeholder implementation
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Issue with ID '{issue_id}' not found"
    )


@router.patch("/{issue_id}/status", response_model=Issue, summary="Update issue status")
async def update_issue_status(
    issue_id: str,
    status_update: IssueStatusUpdate
) -> Issue:
    """
    Update the status of an issue.
    
    Path Parameters:
    - issue_id: Unique identifier of the issue
    
    Request Body:
    - status: New status (open, in_progress, resolved, closed, reopened)
    - reason: Optional reason for the status change
    
    Returns:
    - Updated issue with new status
    
    Raises:
    - 404: Issue not found
    - 400: Invalid status transition
    """
    # TODO: Implement status update with validation
    # This is a placeholder implementation
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Issue with ID '{issue_id}' not found"
    )


@router.post("/{issue_id}/notes", response_model=IssueNote, status_code=status.HTTP_201_CREATED, summary="Add a note to an issue")
async def add_issue_note(
    issue_id: str,
    note_data: NoteCreate
) -> IssueNote:
    """
    Add a note or comment to an issue.
    
    Path Parameters:
    - issue_id: Unique identifier of the issue
    
    Request Body:
    - content: Content of the note (required)
    - author: Author of the note (required)
    
    Returns:
    - Created note with metadata
    
    Raises:
    - 404: Issue not found
    """
    # TODO: Implement note creation and attachment
    # This is a placeholder implementation
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Issue with ID '{issue_id}' not found"
    )


@router.get("/{issue_id}/notes", response_model=List[IssueNote], summary="Get all notes for an issue")
async def get_issue_notes(issue_id: str) -> List[IssueNote]:
    """
    Retrieve all notes attached to an issue.
    
    Path Parameters:
    - issue_id: Unique identifier of the issue
    
    Returns:
    - List of notes with metadata
    
    Raises:
    - 404: Issue not found
    """
    # TODO: Implement note retrieval
    # This is a placeholder implementation
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Issue with ID '{issue_id}' not found"
    )
