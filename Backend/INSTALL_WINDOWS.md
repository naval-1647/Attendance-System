# Installation Guide for Windows

The face-recognition library requires dlib, which can be tricky to install on Windows. Here are the solutions:

## Solution 1: Using Conda (Recommended for Windows)

```bash
# Create virtual environment with conda
conda create -n attendance python=3.10
conda activate attendance

# Install from conda-forge (includes pre-built dlib)
conda install -c conda-forge face-recognition

# Install remaining packages
pip install -r requirements.txt
```

## Solution 2: Using Pre-built Wheels

1. Download pre-built dlib wheel from: https://github.com/ageitgey/face_recognition/issues/175
2. Install it first:
   ```bash
   pip install dlib‑X.X.X‑cpXX‑cpXX‑win_amd64.whl
   ```
3. Then install requirements:
   ```bash
   pip install -r requirements.txt
   ```

## Solution 3: Using WSL2 (Windows Subsystem for Linux)

On WSL2, use standard Linux installation:
```bash
# Inside WSL2 Ubuntu
pip install -r requirements.txt
```

## Solution 4: Docker

Use Docker to bypass Windows installation issues:
```bash
docker build -t attendance-system .
docker run -p 8000:8000 attendance-system
```

## Quick Test

After installation, verify everything works:

```bash
python -c "import face_recognition; print('✓ face_recognition installed')"
python -c "import motor; print('✓ motor installed')"
python -c "import fastapi; print('✓ fastapi installed')"
python main.py
```

Then access: http://localhost:8000/health
