"""Test cases for the attendance system."""
import pytest
import asyncio
from fastapi.testclient import TestClient
from pathlib import Path
import base64
import io
from PIL import Image
import numpy as np

from main import app
import database
from face_recognition_helper import FaceRecognitionHelper


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
async def setup_db():
    """Setup database connection."""
    await database.connect_db()
    yield
    await database.disconnect_db()


def create_test_image() -> bytes:
    """Create a simple test image."""
    # Create a dummy image
    img = Image.new('RGB', (300, 300), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes.getvalue()


class TestFaceRecognition:
    """Test face recognition utilities."""

    def test_valid_image(self):
        """Test image validation."""
        img_bytes = create_test_image()
        assert FaceRecognitionHelper.is_valid_image(img_bytes) is True

    def test_invalid_image(self):
        """Test invalid image detection."""
        invalid_bytes = b"not an image"
        assert FaceRecognitionHelper.is_valid_image(invalid_bytes) is False

    def test_get_image_dimensions(self):
        """Test image dimension extraction."""
        img_bytes = create_test_image()
        dimensions = FaceRecognitionHelper.get_image_dimensions(img_bytes)
        assert dimensions == (300, 300)


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Test health check returns OK."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestEmployeeRegistration:
    """Test employee registration."""

    def test_register_with_invalid_image(self, client):
        """Test registration with invalid image."""
        invalid_image = b"not an image"
        files = {"image": ("test.jpg", invalid_image, "image/jpeg")}
        data = {"name": "John Doe", "email": "john@test.com"}

        response = client.post("/register", files=files, data=data)
        assert response.status_code == 400

    def test_register_employee_success(self, client):
        """Test successful employee registration.

        Note: This will fail without real face image.
        Use actual employee photo for real testing.
        """
        # This test requires a real face image
        # For demonstration, it shows the API structure
        pass


class TestAttendanceRecording:
    """Test attendance recording."""

    def test_face_attendance_no_face_detected(self, client):
        """Test attendance with no face detected."""
        invalid_image = b"not an image"
        files = {"image": ("test.jpg", invalid_image, "image/jpeg")}

        response = client.post("/face-attendance", files=files)
        assert response.status_code == 400

    def test_face_attendance_not_registered(self, client):
        """Test attendance for unregistered employee.

        Note: This test requires proper setup of MongoDB
        and a valid employee face image.
        """
        # This test requires a valid face image and registered employee
        pass


class TestAttendanceHistory:
    """Test attendance history retrieval."""

    def test_get_attendance_invalid_user(self, client):
        """Test getting attendance for non-existent user."""
        response = client.get("/attendance/invalid_user_id")
        assert response.status_code == 404

    def test_get_attendance_with_limit(self, client):
        """Test attendance history with limit parameter."""
        # This test requires a registered user
        pass


class TestEmployeeList:
    """Test employee listing."""

    def test_get_all_employees(self, client):
        """Test getting all employees."""
        response = client.get("/employees")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


# Integration Tests (requires real setup)
class TestIntegration:
    """Integration tests with real database."""

    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test complete workflow: register -> attendance -> history."""
        await database.connect_db()

        try:
            # Note: These tests require real face images
            # This is a template for the complete workflow

            # 1. Register employee
            # 2. Record check-in
            # 3. Record check-out
            # 4. Verify attendance history

            pass
        finally:
            await database.disconnect_db()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
