# Attendance System - Quick Start Guide

## Getting Started in 5 Minutes

### 1. Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
```

### 2. Configure MongoDB
Edit `.env` with your MongoDB credentials:
```
MONGODB_URL=mongodb+srv://<username>:<password>@cluster0.example.mongodb.net/
MONGODB_DB_NAME=attendance_system
```

### 3. Run Server
```bash
python main.py
```

### 4. Access API
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## Usage Examples

### Register Employee
```bash
curl -X POST http://localhost:8000/register \
  -F "name=John Doe" \
  -F "email=john@company.com" \
  -F "image=@photo.jpg"
```

Response:
```json
{
  "user_id": "507f1f77bcf86cd799439011",
  "name": "John Doe",
  "email": "john@company.com"
}
```

### Record Attendance (Check-in)
```bash
curl -X POST http://localhost:8000/face-attendance \
  -F "image=@photo.jpg"
```

Response (First entry of day):
```json
{
  "user_id": "507f1f77bcf86cd799439011",
  "name": "John Doe",
  "attendance_type": "LOGIN",
  "check_in": "2026-04-13T09:30:00",
  "check_out": null,
  "date": "2026-04-13",
  "status": "full_day",
  "message": "Welcome John Doe! Logged in successfully."
}
```

### Record Attendance (Check-out)
Same endpoint, second photo on same day:
```bash
curl -X POST http://localhost:8000/face-attendance \
  -F "image=@photo.jpg"
```

Response (Second entry of day):
```json
{
  "user_id": "507f1f77bcf86cd799439011",
  "name": "John Doe",
  "attendance_type": "LOGOUT",
  "check_in": "2026-04-13T09:30:00",
  "check_out": "2026-04-13T18:30:00",
  "date": "2026-04-13",
  "status": "full_day",
  "message": "Goodbye John Doe! Logged out successfully."
}
```

### Get Attendance History
```bash
curl http://localhost:8000/attendance/507f1f77bcf86cd799439011?limit=10
```

Response:
```json
[
  {
    "user_id": "507f1f77bcf86cd799439011",
    "name": "John Doe",
    "date": "2026-04-13",
    "check_in": "2026-04-13T09:30:00",
    "check_out": "2026-04-13T18:30:00",
    "status": "full_day",
    "auto_logout": false
  }
]
```

---

## Smart Logic Examples

### Scenario 1: Normal Day
- 09:30 AM - Employee scans face → **LOGIN** recorded
- 06:30 PM - Employee scans face → **LOGOUT** recorded
- Status: `full_day`

### Scenario 2: Half Day (Late Entry)
- 02:00 PM - Employee scans face (no morning entry) → **HALF-DAY** recorded
- Status: `half_day`

### Scenario 3: Forgot to Logout
- 09:30 AM - Employee scans face → LOGIN
- 6+ hours later - System auto-logouts
- Status: `full_day`, `auto_logout: true`

---

## Key Features

✅ **Face Recognition**: Secure, contactless attendance  
✅ **Smart Attendance Logic**: Automatic check-in/out detection  
✅ **Auto-logout**: Prevents missed logouts (9-hour threshold)  
✅ **Attendance History**: Full audit trail  
✅ **Error Handling**: Clear error messages  
✅ **Async Performance**: Non-blocking operations  
✅ **MongoDB**: Scalable cloud storage  
✅ **API Documentation**: Interactive Swagger UI  

---

## Configuration

Edit `config.py` to customize:

```python
# Auto-logout after 9 hours
AUTO_LOGOUT_HOURS = 9

# Check every 30 minutes
CHECK_INTERVAL_MINUTES = 30

# Face matching tolerance (0.6 is standard)
FACE_MATCH_TOLERANCE = 0.6

# Recognition model: "hog" (fast) or "cnn" (accurate)
FACE_ENCODING_MODEL = "hog"
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Face not detected | Improve lighting, ensure face is visible |
| Wrong person recognized | Lower `FACE_MATCH_TOLERANCE` in config |
| MongoDB connection error | Check `.env` credentials and network |
| Port 8000 in use | Change `PORT` in config.py |
| face_recognition fails | Install required system dependencies |

---

## Project Files

| File | Purpose |
|------|---------|
| `main.py` | FastAPI app setup and startup/shutdown |
| `config.py` | Configuration and constants |
| `models.py` | Request/response Pydantic models |
| `database.py` | MongoDB async operations |
| `face_recognition_helper.py` | Face detection and matching |
| `scheduler.py` | Background auto-logout scheduler |
| `routes.py` | API endpoints |
| `requirements.txt` | Python dependencies |
| `.env` | Environment variables (create from .env.example) |

---

## Next Steps

1. Install dependencies: `pip install -r requirements.txt`
2. Configure `.env` with MongoDB credentials
3. Run `python main.py`
4. Test with: `curl http://localhost:8000/health`
5. Register employees via `/register` endpoint
6. Use `/face-attendance` for attendance tracking
7. Check history with `/attendance/{user_id}`

---

## API Reference

See full documentation at: http://localhost:8000/docs

**Main Endpoints:**
- `POST /register` - Register employee
- `POST /face-attendance` - Record attendance
- `GET /attendance/{user_id}` - Get history
- `GET /employees` - List all employees
- `GET /health` - Health check
