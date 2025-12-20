"""
API Package for Home Assistant Log Analysis Dashboard.

This package contains all API routers for the dashboard including:
- Issues management (issues.py)
- Integration management (integrations.py)
- Statistics and aggregations (statistics.py)
"""

from fastapi import APIRouter

# Import routers from submodules
from .issues import router as issues_router
from .integrations import router as integrations_router
from .statistics import router as statistics_router

# Create main API router
api_router = APIRouter(prefix="/api")

# Include all sub-routers
api_router.include_router(issues_router)
api_router.include_router(integrations_router)
api_router.include_router(statistics_router)

__all__ = ["api_router", "issues_router", "integrations_router", "statistics_router"]
