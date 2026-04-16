"""API routes for attendance system."""
import logging
import base64
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, status
from datetime import datetime
from typing import List, Optional

import models
import database
from face_recognition_helper import FaceRecognitionHelper
import config

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/register", response_model=models.EmployeeResponse, status_code=201)
async def register_employee(
    name: str = Form(...),
    designation: str = Form(...),
    email: Optional[str] = Form(None),
    image: UploadFile = File(...)
):
    """
    Register a new employee with image for face recognition.

    - **name**: Employee name
    - **designation**: Employee designation/job title
    - **email**: Optional email
    - **image**: Image file with employee's face (upload via file chooser)
    """
    try:
        # Validate form fields
        logger.info(f"Registration request: name='{name}', designation='{designation}', email='{email}', file={image.filename}")
        
        if not name or not name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee name is required and cannot be empty"
            )
        
        if not designation or not designation.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Designation is required and cannot be empty"
            )

        # Read image content
        image_content = await image.read()
        
        if not image_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image file is empty"
            )

        # Validate image
        if not FaceRecognitionHelper.is_valid_image(image_content):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image file format. Please upload a valid image (JPG, PNG, etc.)"
            )

        # Check if face recognition is available
        if not FaceRecognitionHelper.is_face_recognition_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Face recognition service is not available. Please install the face-recognition library. See INSTALL_WINDOWS.md for installation instructions."
            )

        # Detect and encode face
        face_detected, face_encoding = FaceRecognitionHelper.detect_and_encode_face(image_content)

        if not face_detected or not face_encoding:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No face detected in the image. Please provide a clear image with a face."
            )

        # Check if face is already registered (skip in development mode)
        if not getattr(config, 'SKIP_DUPLICATE_CHECK', False):
            existing_employee = await database.EmployeeDB.check_face_already_registered(
                face_encoding, config.FACE_MATCH_TOLERANCE
            )

            if existing_employee:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Face already registered for employee: {existing_employee['name']} ({existing_employee['designation']})"
                )

        # Create employee in database
        employee = await database.EmployeeDB.create_employee(
            name=name.strip(),
            face_encodings=face_encoding,
            email=email.strip() if email else None,
            designation=designation.strip()
        )

        logger.info(f"Employee registered: {employee['user_id']} - {name} - {designation}")

        return models.EmployeeResponse(
            user_id=employee["user_id"],
            name=employee["name"],
            designation=employee.get("designation"),
            email=employee.get("email")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering employee: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering employee: {str(e)}"
        )


@router.post("/face-attendance", response_model=models.AttendanceResponse)
async def face_attendance(image: UploadFile = File(...)):
    """
    Record attendance using face recognition.

    - **image**: Image file for face detection and matching (upload via file chooser)
    """
    try:
        logger.info(f"Attendance request with file: {image.filename}")
        
        # Read image content
        image_content = await image.read()
        
        if not image_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image file is empty"
            )

        # Validate image
        if not FaceRecognitionHelper.is_valid_image(image_content):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image file format. Please upload JPG or PNG."
            )

        # Check if face recognition is available
        if not FaceRecognitionHelper.is_face_recognition_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Face recognition service is not available. Please install the face-recognition library. See INSTALL_WINDOWS.md for installation instructions."
            )

        # Detect and encode face
        face_detected, current_face_encoding = FaceRecognitionHelper.detect_and_encode_face(image_content)

        if not face_detected or not current_face_encoding:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No face detected in the image. Please ensure your face is clearly visible."
            )

        # Get all employees for comparison
        employees = await database.EmployeeDB.get_all_employees()

        if not employees:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No employees registered in the system"
            )

        logger.info(f"Comparing against {len(employees)} registered employees")

        # Find matching employee
        matched_employee = FaceRecognitionHelper.find_matching_employee(
            current_face_encoding,
            employees,
            tolerance=config.FACE_MATCH_TOLERANCE
        )

        if not matched_employee:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Face not recognized. Please register first or try again."
            )

        user_id = matched_employee["user_id"]
        name = matched_employee["name"]
        designation = matched_employee.get("designation", "N/A")

        logger.info(f"Face matched for user: {user_id} - {name}")

        # Convert image to base64 for storing
        image_base64 = base64.b64encode(image_content).decode('utf-8')

        # Check today's attendance
        today_attendance = await database.AttendanceDB.get_today_attendance(user_id)
        today_date = datetime.now().strftime("%Y-%m-%d")

        attendance_type = None
        new_record = None
        message = ""

        if not today_attendance:
            # First entry of the day - LOGIN
            new_record = await database.AttendanceDB.create_attendance(user_id, name, designation, "LOGIN", image_base64)
            attendance_type = "LOGIN"
            message = f"Welcome {name}! Logged in successfully."
            logger.info(f"Check-in recorded for {user_id}")

        elif today_attendance.get("check_out"):
            # Already checked out - prevent multiple attendance
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already checked out for today. Your attendance is complete."
            )

        else:
            # Already checked in, no check-out yet - LOGOUT
            new_record = await database.AttendanceDB.update_attendance_logout(user_id, image_base64)
            attendance_type = "LOGOUT"
            message = f"Goodbye {name}! Logged out successfully."
            logger.info(f"Check-out recorded for {user_id}")

        if not new_record:
            raise Exception("Failed to record attendance")

        return models.AttendanceResponse(
            user_id=user_id,
            name=name,
            attendance_type=attendance_type,
            check_in=new_record.get("check_in"),
            check_out=new_record.get("check_out"),
            date=today_date,
            status=new_record.get("status", "full_day"),
            message=message
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in face attendance: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing attendance: {str(e)}"
        )


@router.get("/attendance/{user_id}", response_model=List[models.AttendanceRecordResponse])
async def get_attendance_history(user_id: str, limit: int = 30):
    """
    Get attendance history for a user.

    - **user_id**: Employee user ID
    - **limit**: Number of records to fetch (default: 30)
    """
    try:
        # Verify user exists
        employee = await database.EmployeeDB.get_employee_by_id(user_id)
        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee with ID {user_id} not found"
            )

        # Get attendance records
        records = await database.AttendanceDB.get_attendance_by_user(user_id, limit)

        if not records:
            return []

        response = []
        for record in records:
            response.append(models.AttendanceRecordResponse(
                user_id=record.get("user_id"),
                name=record.get("name"),
                date=record.get("date"),
                check_in=record.get("check_in"),
                check_out=record.get("check_out"),
                status=record.get("status", "full_day"),
                auto_logout=record.get("auto_logout", False)
            ))

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching attendance history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching attendance history"
        )


@router.get("/employees/{user_id}", response_model=models.EmployeeResponse)
async def get_employee(user_id: str):
    """Get employee details."""
    try:
        employee = await database.EmployeeDB.get_employee_by_id(user_id)

        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Employee with ID {user_id} not found"
            )

        return models.EmployeeResponse(
            user_id=employee["user_id"],
            name=employee["name"],
            designation=employee.get("designation"),
            email=employee.get("email")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching employee: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching employee details"
        )


@router.get("/attendance-by-date/{date_str}")
async def get_attendance_by_date(date_str: str):
    """
    Get all attendance records for a specific date.
    
    - **date_str**: Date in format YYYY-MM-DD (e.g., 2026-04-16)
    """
    try:
        # Validate date format
        from datetime import datetime as dt
        try:
            selected_date = dt.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Please use YYYY-MM-DD (e.g., 2026-04-16)"
            )

        logger.info(f"Fetching attendance for date: {selected_date}")

        # Get all attendance records for the date
        records = await database.AttendanceDB.get_attendance_by_date(selected_date)

        if not records:
            return {
                "date": selected_date,
                "total_records": 0,
                "records": []
            }

        response_records = []
        for record in records:
            # Debug info
            has_image = bool(record.get("check_in_image"))
            image_size = len(record.get("check_in_image", "")) if has_image else 0
            logger.info(f"Employee {record.get('name')}: has_image={has_image}, image_size={image_size}")
            
            response_records.append({
                "user_id": record.get("user_id"),
                "name": record.get("name"),
                "designation": record.get("designation", "N/A"),
                "date": record.get("date"),
                "check_in": record.get("check_in"),
                "check_out": record.get("check_out"),
                "check_in_image": record.get("check_in_image"),  # Base64 image
                "check_out_image": record.get("check_out_image"),  # Base64 image
                "status": record.get("status", "full_day"),
                "auto_logout": record.get("auto_logout", False)
            })

        return {
            "date": selected_date,
            "total_records": len(response_records),
            "records": response_records
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching attendance by date: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching attendance: {str(e)}"
        )


@router.get("/debug-attendance/{date_str}")
async def debug_attendance(date_str: str):
    """Debug endpoint - check raw database records."""
    try:
        from datetime import datetime as dt
        selected_date = dt.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
        
        records = await database.AttendanceDB.get_attendance_by_date(selected_date)
        
        debug_info = []
        for record in records:
            debug_info.append({
                "name": record.get("name"),
                "has_check_in_image": "check_in_image" in record,
                "check_in_image_type": type(record.get("check_in_image")).__name__,
                "check_in_image_length": len(record.get("check_in_image", "")) if record.get("check_in_image") else 0,
                "check_in_image_preview": record.get("check_in_image", "")[:100] if record.get("check_in_image") else None
            })
        
        return {
            "total_records": len(records),
            "debug_info": debug_info
        }
    except Exception as e:
        logger.error(f"Debug error: {str(e)}", exc_info=True)
        return {"error": str(e)}


@router.get("/employees")
async def get_all_employees():
    """Get all registered employees."""
    try:
        employees = await database.EmployeeDB.get_all_employees()

        response = []
        for emp in employees:
            response.append(models.EmployeeResponse(
                user_id=emp["user_id"],
                name=emp["name"],
                designation=emp.get("designation"),
                email=emp.get("email")
            ))

        return response

    except Exception as e:
        logger.error(f"Error fetching employees: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching employees"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

