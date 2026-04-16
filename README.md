# Face Recognition Attendance System

A full-stack attendance system with face recognition, built using a Python FastAPI backend and a React/Tailwind frontend.

## Project Structure

- `Backend/` - Python backend with FastAPI, MongoDB integration, face recognition, and attendance logging.
- `Frontend/` - Frontend UI served via Node.js and Tailwind CSS.
- `.gitignore` - Excludes temporary files, environment files, virtual environments, and dependency directories.
- `screenshots/` - Recommended location for application screenshots.

## Features

- Register employee face using webcam capture
- Mark attendance with face verification
- View attendance report with check-in/check-out data
- Export attendance records as CSV
- API documentation available via backend

## Requirements

- Python 3.10+ for backend
- Node.js 18+ for frontend
- MongoDB Atlas or local MongoDB instance
- `npm` for frontend dependency installation

## Backend Setup

1. Open a terminal in `Backend/`
2. Create and activate the virtual environment:
   - Windows:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file in `Backend/` with values like:
   ```env
   MONGODB_URL=mongodb+srv://<username>:<password>@cluster0.example.mongodb.net/
   MONGODB_DB_NAME=attendance_system
   ```
5. Run the backend:
   ```bash
   uvicorn main:app --reload
   ```
6. Open the backend API docs at:
   ```
   http://localhost:8000/docs
   ```

## Frontend Setup

1. Open a terminal in `Frontend/`
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the frontend server:
   ```bash
   npm start
   ```
4. Open the frontend in your browser:
   ```
   http://localhost:3000
   ```

## Environment Variables

The backend reads configuration from `Backend/config.py` and supports the following environment values:

- `MONGODB_URL` - MongoDB connection string
- `MONGODB_DB_NAME` - Database name for attendance data
- `SKIP_FACE_DETECTION` - Set to `true` to bypass face detection during testing
- `SKIP_DUPLICATE_CHECK` - Set to `true` to bypass duplicate face checking during registration

## Troubleshooting

- If the backend fails to connect to MongoDB, verify network access and the `MONGODB_URL` settings.
- If the frontend does not load, confirm that `Frontend/node_modules/` exists and `npm install` completed successfully.
- If face recognition fallback is enabled, the system will use OpenCV when `face_recognition` is not available.

## Screenshots

The following screenshots are intended to be included in the `screenshots/` folder:

- `screenshots/home.png` - Main landing page of the attendance system
- `screenshots/register.png` - Employee registration screen with webcam capture
- `screenshots/attendance.png` - Mark attendance screen with captured image
- `screenshots/report.png` - Attendance report and statistics view

### Example image markdown

```md
![Home Screen](screenshots/home.png)
![Register Employee](screenshots/register.png)
![Mark Attendance](screenshots/attendance.png)
![Attendance Report](screenshots/report.png)
```

## Notes

- Keep `Backend/.env` private and do not commit it to source control.
- The existing `.gitignore` already excludes `Backend/venv/`, `Frontend/node_modules/`, and env files.

---

The `screenshots/` folder has been created and is ready for your screenshot image attachments.