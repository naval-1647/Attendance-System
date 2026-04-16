"""Main FastAPI application setup."""
import logging
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

import routes

# Configure logging (Render safe)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# ✅ Simple FastAPI app (NO lifespan)
app = FastAPI(
    title="Face Recognition Attendance System",
    description="API for managing employee attendance using face recognition",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(routes.router, tags=["Attendance"])


# Root
@app.get("/")
async def root():
    return {
        "message": "Welcome to Face Recognition Attendance System",
        "docs": "/docs",
        "camera_ui": "/camera",
        "upload_ui": "/upload"
    }


# Frontend Pages
@app.get("/upload")
async def file_upload_ui():
    return FileResponse("file_upload.html")


@app.get("/camera")
async def camera_ui():
    return FileResponse("camera_capture.html")


@app.get("/attendance-report")
async def attendance_report_ui():
    return FileResponse("attendance_report.html")