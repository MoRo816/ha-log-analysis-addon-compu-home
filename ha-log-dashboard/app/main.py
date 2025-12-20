"""
FastAPI application for Home Assistant Log Analysis Dashboard.

This module implements the main FastAPI application for analyzing,
visualizing, and managing Home Assistant logs.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse

# Import API routers
from .api import api_router

# Import log reader
from .log_reader import JournalReader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Global journal reader instance
journal_reader = None


# Lifespan event handlers
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage FastAPI application lifespan events.
    
    Handles startup and shutdown tasks.
    """
    global journal_reader
    
    # Startup
    logger.info("Starting Home Assistant Log Analysis Dashboard")
    
    # Initialize journal reader
    try:
        journal_reader = JournalReader(unit_name="home-assistant")
        logger.info("Journal reader initialized successfully")
    except RuntimeError as e:
        logger.warning(f"Failed to initialize journal reader: {e}")
        logger.warning("Log reading functionality will be limited")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Home Assistant Log Analysis Dashboard")


# Create FastAPI application instance
app = FastAPI(
    title="Home Assistant Log Analysis Dashboard",
    description="A comprehensive dashboard for analyzing Home Assistant logs",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define static files directory
STATIC_DIR = Path(__file__).parent.parent / "static"
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

# Mount static files if directory exists
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    logger.info(f"Static files mounted from {STATIC_DIR}")

# Include API routers
app.include_router(api_router)
logger.info("API routers registered")


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring application status.
    
    Returns:
        dict: Status information
    """
    return {
        "status": "healthy",
        "service": "ha-log-dashboard"
    }


# Root endpoint
@app.get("/", response_class=HTMLResponse, tags=["Dashboard"])
async def root():
    """
    Root endpoint that serves the main dashboard page.
    
    Returns:
        str: HTML content for the dashboard
    """
    index_file = TEMPLATES_DIR / "index.html"
    
    if index_file.exists():
        with open(index_file, "r") as f:
            return f.read()
    
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Home Assistant Log Analysis Dashboard</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f5f5f5;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                h1 {
                    color: #333;
                    margin-bottom: 20px;
                }
                .info-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin-top: 20px;
                }
                .info-card {
                    background-color: #f9f9f9;
                    border-left: 4px solid #007bff;
                    padding: 15px;
                    border-radius: 4px;
                }
                .info-card h3 {
                    margin-top: 0;
                    color: #007bff;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🏠 Home Assistant Log Analysis Dashboard</h1>
                <p>Welcome to the Home Assistant Log Analysis Dashboard!</p>
                
                <div class="info-grid">
                    <div class="info-card">
                        <h3>📊 Dashboard</h3>
                        <p>Analyze and visualize your Home Assistant logs with powerful analytics tools.</p>
                    </div>
                    <div class="info-card">
                        <h3>🔍 Log Search</h3>
                        <p>Search and filter logs by service, entity, or keyword.</p>
                    </div>
                    <div class="info-card">
                        <h3>📈 Statistics</h3>
                        <p>View detailed statistics about your Home Assistant logs.</p>
                    </div>
                </div>
            </div>
        </body>
    </html>
    """


# API endpoints for logs
@app.get("/api/logs", tags=["Logs"])
async def get_logs(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    level: str = Query(None),
    service: str = Query(None),
    since: str = Query(None),
    until: str = Query(None),
):
    """
    Get Home Assistant logs with optional filtering.
    
    Args:
        limit: Number of logs to return (1-1000, default: 100)
        offset: Number of logs to skip (default: 0)
        level: Filter by log level (INFO, WARNING, ERROR, DEBUG)
        service: Filter by service name
        since: Start time for logs (e.g., "2025-01-01", "1 hour ago")
        until: End time for logs
        
    Returns:
        dict: Paginated logs with metadata
    """
    try:
        logger.info(f"Fetching logs: limit={limit}, offset={offset}, level={level}, service={service}")
        
        if journal_reader is None:
            logger.warning("Journal reader not available")
            return {
                "success": False,
                "error": "Journal reader not available. systemd journal may not be accessible.",
                "count": 0,
                "limit": limit,
                "offset": offset,
                "logs": [],
                "filters": {
                    "level": level,
                    "service": service,
                    "since": since,
                    "until": until
                }
            }
        
        # Read logs from systemd journal
        logs = journal_reader.read_logs(
            limit=limit,
            offset=offset,
            level=level,
            service=service,
            since=since,
            until=until
        )
        
        return {
            "success": True,
            "count": len(logs),
            "limit": limit,
            "offset": offset,
            "logs": logs,
            "filters": {
                "level": level,
                "service": service,
                "since": since,
                "until": until
            }
        }
    except Exception as e:
        logger.error(f"Error fetching logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/logs/stats", tags=["Logs"])
async def get_log_statistics():
    """
    Get statistics about Home Assistant logs.
    
    Returns:
        dict: Log statistics including counts by level and service
    """
    try:
        logger.info("Fetching log statistics")
        
        if journal_reader is None:
            logger.warning("Journal reader not available")
            return {
                "success": False,
                "error": "Journal reader not available",
                "total_logs": 0,
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
        
        # Get statistics from journal
        stats = journal_reader.get_log_statistics()
        stats["success"] = True
        
        return stats
    except Exception as e:
        logger.error(f"Error fetching log statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/logs/{log_id}", tags=["Logs"])
async def get_log_detail(log_id: str):
    """
    Get detailed information about a specific log entry.
    
    Args:
        log_id: The ID (cursor) of the log entry from systemd journal
        
    Returns:
        dict: Detailed log information
    """
    try:
        logger.info(f"Fetching log detail for ID: {log_id}")
        
        if journal_reader is None:
            raise HTTPException(
                status_code=503,
                detail="Journal reader not available"
            )
        
        # Get log entry from journal
        log_entry = journal_reader.get_log_by_id(log_id)
        
        if log_entry is None:
            raise HTTPException(status_code=404, detail="Log not found")
        
        return {
            "success": True,
            "log": log_entry
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching log detail: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# API endpoints for analysis
@app.post("/api/analysis/run", tags=["Analysis"])
async def run_analysis(analysis_type: str = Query(...)):
    """
    Run a log analysis on Home Assistant logs.
    
    Args:
        analysis_type: Type of analysis to run (e.g., 'errors', 'patterns', 'performance')
        
    Returns:
        dict: Analysis results
    """
    try:
        # TODO: Implement analysis logic
        logger.info(f"Running analysis: {analysis_type}")
        
        return {
            "success": True,
            "analysis_type": analysis_type,
            "results": {},
            "timestamp": None
        }
    except Exception as e:
        logger.error(f"Error running analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# API endpoints for configuration
@app.get("/api/config", tags=["Configuration"])
async def get_configuration():
    """
    Get current dashboard configuration.
    
    Returns:
        dict: Configuration settings
    """
    try:
        logger.info("Fetching configuration")
        
        return {
            "success": True,
            "version": "1.0.0",
            "features": {
                "log_analysis": True,
                "statistics": True,
                "search": True
            }
        }
    except Exception as e:
        logger.error(f"Error fetching configuration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with formatted response."""
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions with formatted response."""
    logger.error(f"Unhandled Exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "status_code": 500
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
