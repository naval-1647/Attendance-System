"""Pydantic models for request/response validation."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class EmployeeRegister(BaseModel):
    """Model for employee registration."""
    name: str = Field(..., min_length=1, max_length=100)
    designation: str = Field(..., min_length=1, max_length=100)
    email: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "designation": "Software Engineer",
                "email": "john@example.com"
            }
        }


class FaceAttendanceRequest(BaseModel):
    """Model for face attendance (check-in/out)."""
    pass

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Upload image file for face recognition"
            }
        }


class AttendanceResponse(BaseModel):
    """Model for attendance response."""
    user_id: str
    name: str
    attendance_type: str  # "LOGIN" or "LOGOUT" or "HALF_DAY"
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    date: str  # YYYY-MM-DD format
    status: str  # "full_day", "half_day"
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123abc",
                "name": "John Doe",
                "attendance_type": "LOGIN",
                "check_in": "2026-04-13T09:30:00",
                "check_out": None,
                "date": "2026-04-13",
                "status": "full_day",
                "message": "Logged in successfully"
            }
        }


class EmployeeResponse(BaseModel):
    """Model for employee response."""
    user_id: str
    name: str
    designation: Optional[str] = None
    email: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123abc",
                "name": "John Doe",
                "designation": "Software Engineer",
                "email": "john@example.com"
            }
        }


class AttendanceRecordResponse(BaseModel):
    """Model for attendance history."""
    user_id: str
    name: str
    date: str
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    status: str
    auto_logout: bool

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "123abc",
                "name": "John Doe",
                "date": "2026-04-13",
                "check_in": "2026-04-13T09:30:00",
                "check_out": "2026-04-13T18:30:00",
                "status": "full_day",
                "auto_logout": False
            }
        }


class ErrorResponse(BaseModel):
    """Model for error response."""
    error: str
    message: str
    status_code: int

    class Config:
        json_schema_extra = {
            "example": {
                "error": "FACE_NOT_DETECTED",
                "message": "No face detected in the image",
                "status_code": 400
            }
        }
