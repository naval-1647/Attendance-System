"""Configuration and constants for the attendance system."""
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "attendance_system")

# Database collections
EMPLOYEES_COLLECTION = "employees"
ATTENDANCE_COLLECTION = "attendance"

# Face Recognition Settings
FACE_ENCODING_MODEL = "hog"  # or "cnn" for better accuracy but slower
FACE_MATCH_TOLERANCE = 0.6  # 0.6 is standard, lower = more strict
FACE_COMPARISON_DISTANCE = 0.5  # Euclidean distance threshold

# Development Settings
SKIP_FACE_DETECTION = os.getenv("SKIP_FACE_DETECTION", "false").lower() == "true"  # For testing without face detection
SKIP_DUPLICATE_CHECK = os.getenv("SKIP_DUPLICATE_CHECK", "false").lower() == "true"  # For testing multiple registrations

# Auto Logout Settings
AUTO_LOGOUT_HOURS = 9  # Auto logout after 9 hours
CHECK_INTERVAL_MINUTES = 30  # Check every 30 minutes for auto-logout

# Server Settings
HOST = "0.0.0.0"
PORT = 8000
DEBUG = True
