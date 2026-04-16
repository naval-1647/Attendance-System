"""Database operations for MongoDB."""
import logging
from datetime import datetime, timedelta
from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from bson.objectid import ObjectId
import config

logger = logging.getLogger(__name__)

# Global database instance
db: Optional[AsyncIOMotorDatabase] = None


async def connect_db():
    """Connect to MongoDB and initialize database."""
    global db
    try:
        client = AsyncIOMotorClient(config.MONGODB_URL)
        # Test connection
        await client.admin.command('ping')
        db = client[config.MONGODB_DB_NAME]
        logger.info("Connected to MongoDB successfully")
        return db
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise


async def disconnect_db():
    """Disconnect from MongoDB."""
    global db
    if db is not None:
        db.client.close()
        logger.info("Disconnected from MongoDB")


async def create_indexes():
    """Create indexes for better query performance."""
    if db is None:
        return

    try:
        # Employee indexes
        employees_col = db[config.EMPLOYEES_COLLECTION]
        await employees_col.create_index("email", sparse=True)
        await employees_col.create_index("user_id", unique=True)

        # Attendance indexes
        attendance_col = db[config.ATTENDANCE_COLLECTION]
        await attendance_col.create_index("user_id")
        await attendance_col.create_index("date")
        await attendance_col.create_index([("user_id", 1), ("date", 1)], unique=True)
        await attendance_col.create_index("created_at")

        logger.info("Indexes created successfully")
    except Exception as e:
        logger.error(f"Failed to create indexes: {str(e)}")


class EmployeeDB:
    """Database operations for employees."""

    @staticmethod
    async def create_employee(name: str, face_encodings: List[float], email: Optional[str] = None, designation: Optional[str] = None) -> dict:
        """Create a new employee with face encoding."""
        if db is None:
            raise Exception("Database not connected")

        employee = {
            "user_id": str(ObjectId()),
            "name": name,
            "email": email,
            "designation": designation,
            "face_encodings": face_encodings,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        employees_col = db[config.EMPLOYEES_COLLECTION]
        result = await employees_col.insert_one(employee)
        employee["_id"] = result.inserted_id
        logger.info(f"Employee created: {employee['user_id']}")
        return employee

    @staticmethod
    async def check_face_already_registered(face_encoding: List[float], tolerance: float = 0.6) -> Optional[dict]:
        """Check if a face is already registered in the system."""
        if db is None:
            raise Exception("Database not connected")

        employees_col = db[config.EMPLOYEES_COLLECTION]
        employees = await employees_col.find({}).to_list(length=None)
        
        logger.info(f"Checking {len(employees)} employees for duplicate face")

        if not employees:
            logger.info("No employees found in database")
            return None

        # Use face recognition helper to find matching employee
        from face_recognition_helper import FaceRecognitionHelper
        matching_employee = FaceRecognitionHelper.find_matching_employee(
            face_encoding, employees, tolerance, for_duplicate_check=True
        )
        
        if matching_employee:
            logger.info(f"Found matching employee: {matching_employee['user_id']}")
        else:
            logger.info("No matching employee found")

        return matching_employee

    @staticmethod
    async def get_employee_by_id(user_id: str) -> Optional[dict]:
        """Get employee by user_id."""
        if db is None:
            raise Exception("Database not connected")

        employees_col = db[config.EMPLOYEES_COLLECTION]
        employee = await employees_col.find_one({"user_id": user_id})
        return employee

    @staticmethod
    async def get_all_employees() -> List[dict]:
        """Get all employees with their face encodings."""
        if db is None:
            raise Exception("Database not connected")

        employees_col = db[config.EMPLOYEES_COLLECTION]
        employees = await employees_col.find({}).to_list(None)
        return employees

    @staticmethod
    async def update_employee_face_encoding(user_id: str, face_encodings: List[float]) -> Optional[dict]:
        """Update employee face encoding."""
        if db is None:
            raise Exception("Database not connected")

        employees_col = db[config.EMPLOYEES_COLLECTION]
        result = await employees_col.update_one(
            {"user_id": user_id},
            {"$set": {"face_encodings": face_encodings, "updated_at": datetime.utcnow()}}
        )
        if result.matched_count > 0:
            return await EmployeeDB.get_employee_by_id(user_id)
        return None


class AttendanceDB:
    """Database operations for attendance records."""

    @staticmethod
    async def get_today_attendance(user_id: str) -> Optional[dict]:
        """Get attendance record for today."""
        if db is None:
            raise Exception("Database not connected")

        today = datetime.now().strftime("%Y-%m-%d")
        attendance_col = db[config.ATTENDANCE_COLLECTION]
        record = await attendance_col.find_one({
            "user_id": user_id,
            "date": today
        })
        return record

    @staticmethod
    async def create_attendance(user_id: str, name: str, designation: str = "N/A", attendance_type: str = "LOGIN", image_data: Optional[str] = None) -> dict:
        """Create new attendance record (check-in)."""
        if db is None:
            raise Exception("Database not connected")

        today = datetime.now().strftime("%Y-%m-%d")
        now = datetime.now()

        attendance = {
            "user_id": user_id,
            "name": name,
            "designation": designation,
            "date": today,
            "check_in": now,
            "check_out": None,
            "check_in_image": image_data,  # Base64 encoded image
            "check_out_image": None,
            "status": "full_day",
            "auto_logout": False,
            "created_at": now,
            "updated_at": now
        }

        attendance_col = db[config.ATTENDANCE_COLLECTION]
        result = await attendance_col.insert_one(attendance)
        attendance["_id"] = result.inserted_id
        logger.info(f"Attendance created for {user_id}")
        return attendance

    @staticmethod
    async def update_attendance_logout(user_id: str, image_data: Optional[str] = None) -> Optional[dict]:
        """Update attendance record with check-out time."""
        if db is None:
            raise Exception("Database not connected")

        today = datetime.now().strftime("%Y-%m-%d")
        now = datetime.now()

        update_data = {
            "check_out": now,
            "status": "full_day",
            "auto_logout": False,
            "updated_at": now
        }
        
        if image_data:
            update_data["check_out_image"] = image_data

        attendance_col = db[config.ATTENDANCE_COLLECTION]
        result = await attendance_col.update_one(
            {"user_id": user_id, "date": today},
            {"$set": update_data}
        )

        if result.matched_count > 0:
            return await AttendanceDB.get_today_attendance(user_id)
        return None

    @staticmethod
    async def mark_half_day(user_id: str, name: str) -> dict:
        """Mark attendance as half day (logout without login)."""
        if db is None:
            raise Exception("Database not connected")

        today = datetime.now().strftime("%Y-%m-%d")
        now = datetime.now()

        attendance = {
            "user_id": user_id,
            "name": name,
            "date": today,
            "check_in": None,
            "check_out": now,
            "status": "half_day",
            "auto_logout": False,
            "created_at": now,
            "updated_at": now
        }

        attendance_col = db[config.ATTENDANCE_COLLECTION]
        result = await attendance_col.insert_one(attendance)
        attendance["_id"] = result.inserted_id
        logger.info(f"Half day marked for {user_id}")
        return attendance

    @staticmethod
    async def auto_logout_user(user_id: str) -> Optional[dict]:
        """Auto logout user after 9 hours."""
        if db is None:
            raise Exception("Database not connected")

        today = datetime.now().strftime("%Y-%m-%d")
        now = datetime.now()

        attendance_col = db[config.ATTENDANCE_COLLECTION]
        record = await attendance_col.find_one({
            "user_id": user_id,
            "date": today,
            "check_out": None
        })

        if record and record["check_in"]:
            check_in_time = record["check_in"]
            if isinstance(check_in_time, str):
                check_in_time = datetime.fromisoformat(check_in_time)

            elapsed = now - check_in_time
            if elapsed >= timedelta(hours=config.AUTO_LOGOUT_HOURS):
                result = await attendance_col.update_one(
                    {"_id": record["_id"]},
                    {
                        "$set": {
                            "check_out": now,
                            "auto_logout": True,
                            "updated_at": now
                        }
                    }
                )
                if result.modified_count > 0:
                    logger.info(f"Auto logout executed for {user_id}")
                    return await AttendanceDB.get_today_attendance(user_id)

        return None

    @staticmethod
    async def get_attendance_by_user(user_id: str, limit: int = 30) -> List[dict]:
        """Get attendance history for a user."""
        if db is None:
            raise Exception("Database not connected")

        attendance_col = db[config.ATTENDANCE_COLLECTION]
        records = await attendance_col.find({"user_id": user_id}).sort("date", -1).limit(limit).to_list(None)
        return records

    @staticmethod
    async def get_attendance_by_date_range(user_id: str, start_date: str, end_date: str) -> List[dict]:
        """Get attendance records within a date range."""
        if db is None:
            raise Exception("Database not connected")

        attendance_col = db[config.ATTENDANCE_COLLECTION]
        records = await attendance_col.find({
            "user_id": user_id,
            "date": {"$gte": start_date, "$lte": end_date}
        }).sort("date", -1).to_list(None)
        return records

    @staticmethod
    async def get_attendance_by_date(date_str: str) -> List[dict]:
        """Get all attendance records for a specific date."""
        if db is None:
            raise Exception("Database not connected")

        attendance_col = db[config.ATTENDANCE_COLLECTION]
        records = await attendance_col.find({
            "date": date_str
        }).sort("check_in", -1).to_list(None)
        return records

    @staticmethod
    async def get_pending_auto_logout() -> List[dict]:
        """Get records that need auto logout check."""
        if db is None:
            raise Exception("Database not connected")

        today = datetime.now().strftime("%Y-%m-%d")
        attendance_col = db[config.ATTENDANCE_COLLECTION]

        # Find records from today that are still checked in
        records = await attendance_col.find({
            "date": today,
            "check_out": None,
            "check_in": {"$exists": True}
        }).to_list(None)
        return records
