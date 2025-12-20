"""
FastAPI router for integration management endpoints.

This module provides REST API endpoints for managing Home Assistant integrations:
- List all integrations with issue counts
- Get specific integration details
- Get all issues for an integration
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

# Initialize router
router = APIRouter(prefix="/integrations", tags=["integrations"])


# ============================================================================
# Pydantic Models
# ============================================================================

class IntegrationSummary(BaseModel):
    """Summary information about an integration."""
    
    name: str = Field(..., description="Integration name")
    display_name: str = Field(..., description="Human-readable integration name")
    issue_count: int = Field(default=0, ge=0, description="Total number of issues")
    critical_count: int = Field(default=0, ge=0, description="Number of critical issues")
    warning_count: int = Field(default=0, ge=0, description="Number of warning issues")
    info_count: int = Field(default=0, ge=0, description="Number of info issues")
    last_issue_date: Optional[datetime] = Field(None, description="Date of most recent issue")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "homeassistant.components.zwave",
                "display_name": "Z-Wave",
                "issue_count": 15,
                "critical_count": 2,
                "warning_count": 10,
                "info_count": 3,
                "last_issue_date": "2025-12-20T17:53:36Z"
            }
        }


class IntegrationDetail(BaseModel):
    """Detailed information about an integration."""
    
    name: str = Field(..., description="Integration name")
    display_name: str = Field(..., description="Human-readable integration name")
    description: Optional[str] = Field(None, description="Integration description")
    version: Optional[str] = Field(None, description="Integration version")
    issue_count: int = Field(default=0, ge=0, description="Total number of issues")
    critical_count: int = Field(default=0, ge=0, description="Number of critical issues")
    warning_count: int = Field(default=0, ge=0, description="Number of warning issues")
    info_count: int = Field(default=0, ge=0, description="Number of info issues")
    resolved_count: int = Field(default=0, ge=0, description="Number of resolved issues")
    first_issue_date: Optional[datetime] = Field(None, description="Date of first issue")
    last_issue_date: Optional[datetime] = Field(None, description="Date of most recent issue")
    documentation_url: Optional[str] = Field(None, description="Link to integration documentation")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "homeassistant.components.zwave",
                "display_name": "Z-Wave",
                "description": "Support for Z-Wave devices",
                "version": "2023.12.0",
                "issue_count": 15,
                "critical_count": 2,
                "warning_count": 10,
                "info_count": 3,
                "resolved_count": 5,
                "first_issue_date": "2025-12-01T10:00:00Z",
                "last_issue_date": "2025-12-20T17:53:36Z",
                "documentation_url": "https://www.home-assistant.io/integrations/zwave/"
            }
        }


class IntegrationIssue(BaseModel):
    """Issue associated with an integration."""
    
    id: str = Field(..., description="Unique issue identifier")
    title: str = Field(..., description="Issue title")
    description: str = Field(default="", description="Issue description")
    severity: str = Field(..., description="Issue severity level")
    status: str = Field(..., description="Issue status")
    created_at: datetime = Field(..., description="Issue creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "issue-001",
                "title": "Z-Wave device timeout",
                "description": "Device failed to respond within timeout period",
                "severity": "warning",
                "status": "open",
                "created_at": "2025-12-20T10:00:00Z",
                "updated_at": "2025-12-20T17:53:36Z"
            }
        }


class IntegrationListResponse(BaseModel):
    """Response model for listing integrations."""
    
    total: int = Field(..., ge=0, description="Total number of integrations")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Number of items per page")
    items: List[IntegrationSummary] = Field(..., description="List of integrations")


class IntegrationIssueListResponse(BaseModel):
    """Response model for listing integration issues."""
    
    integration_name: str = Field(..., description="Integration name")
    total: int = Field(..., ge=0, description="Total number of issues")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Number of items per page")
    items: List[IntegrationIssue] = Field(..., description="List of issues")


# ============================================================================
# Endpoints
# ============================================================================

@router.get("", response_model=IntegrationListResponse, summary="List all integrations")
async def list_integrations(
    skip: int = Query(0, ge=0, description="Number of items to skip for pagination"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of items to return"),
    sort_by: str = Query("issue_count", regex="^(name|issue_count|last_issue_date)$", 
                        description="Field to sort by"),
    order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    has_issues: Optional[bool] = Query(None, description="Filter integrations with/without issues"),
) -> IntegrationListResponse:
    """
    Retrieve a paginated list of all integrations with issue counts.
    
    Query Parameters:
    - skip: Number of items to skip (for pagination, default: 0)
    - limit: Maximum number of items to return (default: 20, max: 100)
    - sort_by: Field to sort by (name, issue_count, last_issue_date)
    - order: Sort order (asc, desc)
    - has_issues: Filter to show only integrations with/without issues
    
    Returns:
    - Paginated list of integrations with issue counts and metadata
    """
    # TODO: Implement database query with filters and sorting
    # This is a placeholder implementation
    
    # Mock data for demonstration
    mock_integrations = []
    
    return IntegrationListResponse(
        total=len(mock_integrations),
        page=skip // limit + 1,
        page_size=limit,
        items=mock_integrations
    )


@router.get("/{integration_name}", response_model=IntegrationDetail, 
           summary="Get integration details")
async def get_integration(integration_name: str) -> IntegrationDetail:
    """
    Retrieve detailed information about a specific integration.
    
    Path Parameters:
    - integration_name: Name of the integration (e.g., 'homeassistant.components.zwave')
    
    Returns:
    - Detailed integration information including issue counts and metadata
    
    Raises:
    - 404: Integration not found
    """
    # TODO: Implement database query by integration name
    # This is a placeholder implementation
    
    # Return 404 for now since we don't have data
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Integration '{integration_name}' not found"
    )


@router.get("/{integration_name}/issues", response_model=IntegrationIssueListResponse,
           summary="Get all issues for an integration")
async def get_integration_issues(
    integration_name: str,
    skip: int = Query(0, ge=0, description="Number of items to skip for pagination"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of items to return"),
    severity: Optional[str] = Query(None, description="Filter by severity level"),
    status: Optional[str] = Query(None, description="Filter by issue status"),
    sort_by: str = Query("created_at", regex="^(created_at|updated_at|severity)$",
                        description="Field to sort by"),
    order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
) -> IntegrationIssueListResponse:
    """
    Retrieve all issues associated with a specific integration.
    
    Path Parameters:
    - integration_name: Name of the integration
    
    Query Parameters:
    - skip: Number of items to skip (for pagination, default: 0)
    - limit: Maximum number of items to return (default: 20, max: 100)
    - severity: Filter by severity level (low, medium, high, critical)
    - status: Filter by issue status (open, in_progress, resolved, closed)
    - sort_by: Field to sort by (created_at, updated_at, severity)
    - order: Sort order (asc, desc)
    
    Returns:
    - Paginated list of issues for the integration
    
    Raises:
    - 404: Integration not found
    """
    # TODO: Implement database query for integration issues with filters
    # This is a placeholder implementation
    
    # Verify integration exists first
    # For now, return empty list
    mock_issues = []
    
    return IntegrationIssueListResponse(
        integration_name=integration_name,
        total=len(mock_issues),
        page=skip // limit + 1,
        page_size=limit,
        items=mock_issues
    )


@router.get("/{integration_name}/statistics", summary="Get integration statistics")
async def get_integration_statistics(integration_name: str):
    """
    Get detailed statistics for a specific integration.
    
    Path Parameters:
    - integration_name: Name of the integration
    
    Returns:
    - Statistical data including issue trends, severity distribution, etc.
    
    Raises:
    - 404: Integration not found
    """
    # TODO: Implement statistics calculation
    # This is a placeholder implementation
    
    return {
        "integration_name": integration_name,
        "total_issues": 0,
        "severity_distribution": {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        },
        "status_distribution": {
            "open": 0,
            "in_progress": 0,
            "resolved": 0,
            "closed": 0
        },
        "issue_trend": {
            "labels": [],
            "data": []
        }
    }
