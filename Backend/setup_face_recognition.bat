@echo off
echo ========================================
echo Face Recognition Setup Script
echo ========================================
echo.
echo This will create a Python 3.11 environment with face_recognition
echo.
pause

echo.
echo Step 1: Checking Python versions...
py --list

echo.
echo Step 2: Creating new virtual environment with Python 3.11...
py -3.11 -m venv venv311

echo.
echo Step 3: Activating environment...
call venv311\Scripts\activate.bat

echo.
echo Step 4: Installing dependencies...
pip install --upgrade pip
pip install cmake
pip install dlib==19.24.1
pip install face-recognition
pip install fastapi uvicorn motor Pillow numpy python-dotenv apscheduler python-multipart httpx pytest pytest-asyncio

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo To start the server:
echo   cd venv311\Scripts\activate
echo   uvicorn main:app --reload
echo.
echo Then visit: http://localhost:8000/upload
echo.
pause
