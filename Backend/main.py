"""Main FastAPI application setup."""
import logging
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

import config
import database
import routes
from scheduler import init_scheduler, stop_scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("attendance_system.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Startup
    logger.info("Starting Attendance System...")
    try:
        await database.connect_db()
        await database.create_indexes()
        await init_scheduler()
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down Attendance System...")
    try:
        stop_scheduler()
        await database.disconnect_db()
        logger.info("Application shut down successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")


# Create FastAPI app
app = FastAPI(
    title="Face Recognition Attendance System",
    description="API for managing employee attendance using face recognition",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(routes.router, tags=["Attendance"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Face Recognition Attendance System",
        "version": "1.0.0",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json",
        "upload_ui_url": "/upload",
        "camera_ui_url": "/camera",
        "report_ui_url": "/attendance-report"
    }


@app.get("/upload")
async def file_upload_ui():
    """Serve the file upload UI page."""
    return FileResponse("file_upload.html")


@app.get("/camera")
async def camera_ui():
    """Serve the camera capture UI page."""
    return FileResponse("camera_capture.html")


@app.get("/attendance-report")
async def attendance_report_ui():
    """Serve the attendance report UI page."""
    return FileResponse("attendance_report.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level="info"
    )
