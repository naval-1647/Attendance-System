"""Face recognition utilities using face_recognition library or OpenCV fallback."""
import logging
import numpy as np
from typing import List, Optional, Tuple
from PIL import Image
import io
import base64

import config

logger = logging.getLogger(__name__)

# Try to import face_recognition, make it optional
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
    logger.info("face_recognition library loaded successfully")
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    logger.warning("face_recognition library not available. Using OpenCV fallback.")

# Try to import OpenCV for fallback face detection
try:
    import cv2
    OPENCV_AVAILABLE = True
    logger.info("OpenCV library loaded successfully")
except ImportError:
    OPENCV_AVAILABLE = False
    logger.warning("OpenCV library not available. Face detection will be disabled.")


class FaceRecognitionHelper:
    """Helper class for face recognition operations."""

    @staticmethod
    def is_face_recognition_available() -> bool:
        """Check if any face recognition library is available or if detection is skipped."""
        # If face detection is skipped in development mode, consider it available
        if hasattr(config, 'SKIP_FACE_DETECTION') and config.SKIP_FACE_DETECTION:
            return True
        return FACE_RECOGNITION_AVAILABLE or OPENCV_AVAILABLE

    @staticmethod
    def _detect_faces_opencv(image_bytes: bytes) -> List[Tuple[int, int, int, int]]:
        """Detect faces using OpenCV Haar cascades."""
        if not OPENCV_AVAILABLE:
            return []
            
        try:
            # Convert bytes to numpy array
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                logger.warning("Failed to decode image with OpenCV")
                return []
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Load Haar cascade classifier
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # Detect faces with more lenient parameters
            faces = face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1, 
                minNeighbors=3,  # Reduced from 5 to 3 for more sensitivity
                minSize=(20, 20),  # Reduced from 30x30
                maxSize=(300, 300)
            )
            
            logger.info(f"OpenCV detected {len(faces)} faces")
            
            # Convert to (top, right, bottom, left) format like face_recognition
            face_locations = []
            for (x, y, w, h) in faces:
                face_locations.append((y, x + w, y + h, x))
                logger.debug(f"Face location: {face_locations[-1]}")
            
            return face_locations
            
        except Exception as e:
            logger.error(f"Error detecting faces with OpenCV: {str(e)}")
            return []

    @staticmethod
    def _get_face_encoding_opencv(image_bytes: bytes, face_location: Tuple[int, int, int, int]) -> Optional[List[float]]:
        """Get face encoding using OpenCV from a consistent face crop."""
        if not OPENCV_AVAILABLE:
            return None
            
        try:
            # Load image
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return None
            
            # Extract face region and guard against bad crop
            top, right, bottom, left = face_location
            top = max(0, top)
            left = max(0, left)
            bottom = min(img.shape[0], bottom)
            right = min(img.shape[1], right)
            face_img = img[top:bottom, left:right]
            
            if face_img.size == 0:
                return None
            
            # Convert to grayscale and resize for consistent encoding
            gray_face = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
            resized_face = cv2.resize(gray_face, (64, 64))
            
            # Normalize pixel values and create 128-d encoding from averaged blocks
            flattened = resized_face.flatten().astype(np.float32) / 255.0
            block_size = len(flattened) // 128
            encoding = [float(np.mean(flattened[i * block_size:(i + 1) * block_size])) for i in range(128)]
            
            # Pad/truncate to exactly 128 dimensions
            if len(encoding) < 128:
                encoding.extend([0.0] * (128 - len(encoding)))
            encoding = encoding[:128]
            
            # Normalize vector to unit length for stable comparison
            encoding_array = np.array(encoding, dtype=np.float32)
            norm = np.linalg.norm(encoding_array)
            if norm > 0:
                encoding = (encoding_array / norm).tolist()
            else:
                encoding = encoding_array.tolist()
            
            logger.debug("Generated stable face encoding using OpenCV image crop")
            return encoding
            
        except Exception as e:
            logger.error(f"Error encoding face with OpenCV: {str(e)}")
            return None

    @staticmethod
    def encode_image_to_face_encodings(image_file_content: bytes) -> Optional[List[float]]:
        """
        Convert uploaded image to face encodings.
        Uses face_recognition if available, otherwise falls back to OpenCV.

        Args:
            image_file_content: Bytes content of the image file

        Returns:
            List of face encodings (128-dimensional numpy array converted to list)
        """
        if FACE_RECOGNITION_AVAILABLE:
            # Use face_recognition library
            try:
                # Load image from bytes
                image = face_recognition.load_image_file(io.BytesIO(image_file_content))

                # Find face locations in the image
                face_locations = face_recognition.face_locations(image)

                if not face_locations:
                    logger.warning("No face detected in the provided image")
                    return None

                # Get face encoding for the first face found
                face_encodings = face_recognition.face_encodings(image, face_locations)

                if face_encodings:
                    # Convert numpy array to list for JSON serialization
                    encoding = face_encodings[0].tolist()
                    logger.info("Face encoding generated successfully")
                    return encoding
                else:
                    logger.warning("Could not generate face encoding")
                    return None

            except Exception as e:
                logger.error(f"Error with face_recognition: {str(e)}")
                # Fall back to OpenCV if face_recognition fails
                if OPENCV_AVAILABLE:
                    logger.info("Falling back to OpenCV face detection")
                else:
                    return None
        
        if OPENCV_AVAILABLE:
            # Use OpenCV fallback
            try:
                face_locations = FaceRecognitionHelper._detect_faces_opencv(image_file_content)
                
                if not face_locations:
                    logger.warning("No face detected in the provided image (OpenCV)")
                    return None
                
                # Get encoding for first face
                encoding = FaceRecognitionHelper._get_face_encoding_opencv(image_file_content, face_locations[0])
                if encoding:
                    logger.info("Face encoding generated successfully (OpenCV)")
                    return encoding
                else:
                    logger.warning("Could not generate face encoding (OpenCV)")
                    return None
                
            except Exception as e:
                logger.error(f"Error with OpenCV fallback: {str(e)}")
                return None
        
        # No face detection library available
        logger.error("No face detection library available")
        return None

    @staticmethod
    def detect_and_encode_face(image_file_content: bytes) -> Tuple[bool, Optional[List[float]]]:
        """
        Detect face in image and return encoding.
        Uses face_recognition if available, otherwise falls back to OpenCV.

        Returns:
            Tuple of (face_detected: bool, encoding: List[float] or None)
        """
        # Check for development mode skip
        if hasattr(config, 'SKIP_FACE_DETECTION') and config.SKIP_FACE_DETECTION:
            logger.warning("Face detection skipped in development mode")
            # Return a fixed mock encoding for testing duplicate detection
            mock_encoding = [0.12345] * 128  # Fixed encoding for all registrations in dev mode
            return True, mock_encoding
        
        if FACE_RECOGNITION_AVAILABLE:
            # Use face_recognition library
            try:
                image = face_recognition.load_image_file(io.BytesIO(image_file_content))
                face_locations = face_recognition.face_locations(image)

                if not face_locations:
                    return False, None

                face_encodings = face_recognition.face_encodings(image, face_locations)
                if face_encodings:
                    return True, face_encodings[0].tolist()
                return False, None

            except Exception as e:
                logger.error(f"Error with face_recognition: {str(e)}")
                # Fall back to OpenCV if face_recognition fails
                if OPENCV_AVAILABLE:
                    logger.info("Falling back to OpenCV face detection")
                else:
                    return False, None
        
        if OPENCV_AVAILABLE:
            # Use OpenCV fallback
            try:
                face_locations = FaceRecognitionHelper._detect_faces_opencv(image_file_content)
                
                if not face_locations:
                    return False, None
                
                # Get encoding for first face
                encoding = FaceRecognitionHelper._get_face_encoding_opencv(image_file_content, face_locations[0])
                if encoding:
                    return True, encoding
                return False, None
                
            except Exception as e:
                logger.error(f"Error with OpenCV fallback: {str(e)}")
                return False, None
        
        # No face detection library available
        logger.error("No face detection library available")
        return False, None

    @staticmethod
    def compare_faces(
        known_face_encoding: List[float],
        unknown_face_encoding: List[float],
        tolerance: float = 0.6
    ) -> bool:
        """
        Compare two face encodings.

        Args:
            known_face_encoding: Stored face encoding
            unknown_face_encoding: Face encoding from current image
            tolerance: Tolerance level (lower = stricter matching)

        Returns:
            True if faces match, False otherwise
        """
        # If face detection is skipped (development mode), use simple comparison for mock encodings
        if hasattr(config, 'SKIP_FACE_DETECTION') and config.SKIP_FACE_DETECTION:
            # For mock encodings, consider them matching if they're identical
            return known_face_encoding == unknown_face_encoding
        
        if not FACE_RECOGNITION_AVAILABLE:
            if OPENCV_AVAILABLE:
                try:
                    known_encoding = np.array(known_face_encoding, dtype=np.float32)
                    unknown_encoding = np.array(unknown_face_encoding, dtype=np.float32)
                    known_norm = np.linalg.norm(known_encoding)
                    unknown_norm = np.linalg.norm(unknown_encoding)
                    if known_norm == 0 or unknown_norm == 0:
                        return False
                    known_encoding /= known_norm
                    unknown_encoding /= unknown_norm
                    similarity = float(np.dot(known_encoding, unknown_encoding))
                    logger.debug(f"OpenCV cosine similarity: {similarity}")
                    return similarity >= 0.90
                except Exception as e:
                    logger.error(f"Error comparing OpenCV encodings: {str(e)}")
                    return False
            return False
            
        try:
            # Convert lists to numpy arrays
            known_encoding = np.array(known_face_encoding)
            unknown_encoding = np.array(unknown_face_encoding)

            # Calculate face distance
            face_distance = np.linalg.norm(known_encoding - unknown_encoding)

            # Check if distance is within tolerance
            return face_distance <= tolerance

        except Exception as e:
            logger.error(f"Error comparing faces: {str(e)}")
            return False

    @staticmethod
    def find_matching_employee(
        current_face_encoding: List[float],
        employees: List[dict],
        tolerance: float = 0.6,
        for_duplicate_check: bool = False
    ) -> Optional[dict]:
        """
        Find matching employee from the current face encoding.

        Args:
            current_face_encoding: Current image face encoding
            employees: List of employee records with face encodings
            tolerance: Matching tolerance
            for_duplicate_check: If True, allows matching in development mode

        Returns:
            Matching employee dict or None
        """
        # If face detection is skipped (development mode) and not for duplicate check, return None
        if hasattr(config, 'SKIP_FACE_DETECTION') and config.SKIP_FACE_DETECTION and not for_duplicate_check:
            logger.warning("Face matching disabled in development mode")
            return None
            
        if not employees or not current_face_encoding:
            return None

        if not FACE_RECOGNITION_AVAILABLE and not OPENCV_AVAILABLE:
            logger.error("No suitable face recognition library is installed")
            return None

        best_match = None
        best_distance = tolerance

        try:
            # For duplicate checking in development mode, use simple list comparison
            if hasattr(config, 'SKIP_FACE_DETECTION') and config.SKIP_FACE_DETECTION and for_duplicate_check:
                for employee in employees:
                    if not employee.get("face_encodings"):
                        continue
                    # Compare encodings directly
                    if FaceRecognitionHelper.compare_faces(current_face_encoding, employee["face_encodings"]):
                        return employee
                return None

            # For OpenCV without face_recognition, use exact matching
            if not FACE_RECOGNITION_AVAILABLE and OPENCV_AVAILABLE:
                best_similarity = 0.0
            best_employee = None
            for employee in employees:
                if not employee.get("face_encodings"):
                    continue
                try:
                    known_encoding = employee["face_encodings"]
                    similarity = float(np.dot(
                        np.array(known_encoding, dtype=np.float32) / np.linalg.norm(np.array(known_encoding, dtype=np.float32)),
                        np.array(current_face_encoding, dtype=np.float32) / np.linalg.norm(np.array(current_face_encoding, dtype=np.float32))
                    ))
                except Exception:
                    similarity = 0.0
                logger.debug(f"OpenCV similarity for employee {employee.get('user_id')}: {similarity}")
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_employee = employee

            if best_employee and best_similarity >= 0.90:
                logger.info(f"Face matched to employee: {best_employee.get('user_id')} with similarity {best_similarity}")
                return best_employee

            logger.info(f"No matching employee found with OpenCV. Best similarity: {best_similarity}")
            return None

            current_encoding = np.array(current_face_encoding)

            for employee in employees:
                if not employee.get("face_encodings"):
                    continue

                # Compare with stored encoding
                stored_encoding = np.array(employee["face_encodings"])
                face_distance = np.linalg.norm(current_encoding - stored_encoding)

                # Update best match if this is closer
                if face_distance < best_distance:
                    best_distance = face_distance
                    best_match = employee

            if best_match:
                logger.info(f"Face matched to employee: {best_match.get('user_id')}")
            else:
                logger.warning("No matching face found in database")

            return best_match

        except Exception as e:
            logger.error(f"Error finding matching employee: {str(e)}")
            return None

    @staticmethod
    def is_valid_image(image_file_content: bytes) -> bool:
        """Validate if the file is a valid image."""
        try:
            image = Image.open(io.BytesIO(image_file_content))
            image.verify()
            return True
        except Exception as e:
            logger.error(f"Invalid image file: {str(e)}")
            return False

    @staticmethod
    def convert_base64_to_bytes(base64_string: str) -> Optional[bytes]:
        """Convert base64 string to bytes."""
        try:
            return base64.b64decode(base64_string)
        except Exception as e:
            logger.error(f"Error decoding base64: {str(e)}")
            return None

    @staticmethod
    def get_image_dimensions(image_file_content: bytes) -> Optional[Tuple[int, int]]:
        """Get image dimensions (width, height)."""
        try:
            image = Image.open(io.BytesIO(image_file_content))
            return image.size
        except Exception as e:
            logger.error(f"Error getting image dimensions: {str(e)}")
            return None
