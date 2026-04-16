# Setup & Installation Guide

## Prerequisites

- Python 3.8+
- MongoDB Atlas account (connection string provided)
- pip or conda package manager
- Git (for cloning if needed)

---

## Installation Options

### Option 1: Docker (Easiest - No Installation Issues)

If you have Docker installed, this is the simplest approach:

```bash
# Navigate to Backend directory
cd Backend

# Build and run
docker-compose up --build

# API will be available at http://localhost:8000
# Access docs at http://localhost:8000/docs
```

**Stop the container:**
```bash
docker-compose down
```

---

### Option 2: Conda (Recommended for Windows)

Conda handles the complex dlib dependency better on Windows:

```bash
# Create conda environment
conda create -n attendance python=3.10
conda activate attendance

# Install face-recognition from conda-forge (has pre-built dlib)
conda install -c conda-forge face-recognition

# Install other dependencies
pip install -r requirements.txt

# Run application
python main.py
```

---

### Option 3: venv (Standard - May Need Extra Setup on Windows)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# If face-recognition installation fails on Windows, see Option 4
```

---

### Option 4: WSL2 (Windows Subsystem for Linux)

```bash
# Inside WSL2 Ubuntu terminal
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

---

## Troubleshooting Installation

### Problem: "Failed to build wheel for face-recognition" on Windows

**Root Cause:** dlib requires C++ compiler and dependencies not available on Windows

**Solution A - Use Conda:**
```bash
conda create -n attendance python=3.10
conda activate attendance
conda install -c conda-forge face-recognition
pip install -r requirements.txt
```

**Solution B - Use Docker:**
```bash
docker-compose up --build
```

**Solution C - Use WSL2:**
All Linux tools are available in WSL2, so installation works smoothly.

**Solution D - Pre-built Wheels:**
1. Download pre-built dlib wheel from: https://github.com/ageitgey/face_recognition/issues/175
2. Install it: `pip install dlib-XX.XX-cpXX-cpXX-win_amd64.whl`
3. Then: `pip install -r requirements.txt`

---

### Problem: "KeyError: '__version__'" for Pillow

This is a Python 3.13+ compatibility issue. Solutions:

1. **Use Python 3.10 or 3.11** (Recommended):
   ```bash
   # With conda:
   conda create -n attendance python=3.10
   conda activate attendance
   ```

2. **Use Docker** - Already uses Python 3.10

3. **Update requirements** - Change Pillow version:
   ```bash
   pip install Pillow>=10.0.0
   ```

---

### Problem: MongoDB Connection Error

**Error:** "Failed to connect to MongoDB"

**Solutions:**

1. **Check connection string in .env:**
   ```
   MONGODB_URL=mongodb+srv://naval_jha:32rBEXkdijf7Eez7@cluster0.hqbexhk.mongodb.net/
   ```

2. **Verify network connection:**
   ```bash
   ping mongodb-atlas
   ```

3. **Check MongoDB Atlas:**
   - Log in to MongoDB Atlas
   - Check cluster is running
   - Verify IP whitelist includes your IP

4. **Test connection:**
   ```bash
   python -c "from motor.motor_asyncio import AsyncClient; print('Motor installed')"
   ```

---

## Quick Start After Installation

### 1. Create .env file
```bash
cp .env.example .env
```

The MongoDB credentials are already filled in.

### 2. Run the Application

**With Python:**
```bash
python main.py
```

**With Docker:**
```bash
docker-compose up
```

### 3. Test the API

**Health Check:**
```bash
curl http://localhost:8000/health
```

**API Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Verify Installation

Run this to check all dependencies:

```bash
python -c "
import sys
packages = [
    ('fastapi', 'FastAPI'),
    ('uvicorn', 'Uvicorn'),
    ('motor', 'Motor'),
    ('pydantic', 'Pydantic'),
    ('face_recognition', 'Face Recognition'),
    ('PIL', 'Pillow'),
    ('apscheduler', 'APScheduler'),
    ('numpy', 'NumPy')
]

print('Checking dependencies...')
all_ok = True
for module, name in packages:
    try:
        __import__(module)
        print(f'✓ {name}')
    except ImportError:
        print(f'✗ {name} - MISSING')
        all_ok = False

print()
print('✓ All dependencies installed!' if all_ok else '✗ Some dependencies missing')
sys.exit(0 if all_ok else 1)
"
```

---

## Running Tests

```bash
# With pytest
pytest test_attendance.py -v

# Specific test
pytest test_attendance.py::TestHealthEndpoint::test_health_check -v
```

---

## Configuration

Edit `config.py` to customize:

```python
# Auto-logout threshold (hours)
AUTO_LOGOUT_HOURS = 9

# Check frequency (minutes)
CHECK_INTERVAL_MINUTES = 30

# Face matching tolerance (0.6 is standard)
FACE_MATCH_TOLERANCE = 0.6

# MongoDB
MONGODB_URL = "mongodb+srv://..."
MONGODB_DB_NAME = "attendance_system"

# Server
HOST = "0.0.0.0"
PORT = 8000
DEBUG = True
```

---

## Project Structure

```
Backend/
├── main.py                      # FastAPI app
├── config.py                    # Configuration
├── models.py                    # Request/response models
├── database.py                  # MongoDB operations
├── face_recognition_helper.py   # Face detection
├── scheduler.py                 # Background tasks
├── routes.py                    # API endpoints
├── requirements.txt             # Dependencies
├── .env.example                 # Environment template
├── .env                         # Environment (create from example)
├── Dockerfile                   # Docker image
├── docker-compose.yml           # Docker compose
├── test_attendance.py           # Tests
├── INSTALL_WINDOWS.md           # Windows setup
├── QUICKSTART.md               # 5-min guide
└── README.md                    # Full docs
```

---

## Next Steps

1. **Choose installation method** (Docker / Conda / venv)
2. **Follow the chosen method** above
3. **Create .env file**: `cp .env.example .env`
4. **Run application**: `python main.py` or `docker-compose up`
5. **Access docs**: http://localhost:8000/docs
6. **Test with** `/health` endpoint

---

## Support

| Issue | Solution |
|-------|----------|
| dlib won't install on Windows | Use Conda, Docker, or WSL2 |
| Pillow error on Python 3.13+ | Use Python 3.10/3.11 |
| MongoDB connection fails | Check IP whitelist in MongoDB Atlas |
| Port 8000 in use | Change PORT in config.py |
| Permission denied on Linux | Use `sudo` or add user to docker group |

---

## Recommended Setup

For **quickest working setup**:
1. Use **Docker** if you have it installed
2. Use **Conda** on Windows
3. Use **venv** on Linux/Mac

This avoids the dlib compilation issues that plague Windows users.
