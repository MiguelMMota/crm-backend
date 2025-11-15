"""
Video processing module for extracting faces from video frames.
"""
import io
import numpy as np
from PIL import Image
import face_recognition
from .config import AIConfig


def extract_faces_from_frame(image_bytes):
    """
    Extract faces from a video frame.

    Args:
        image_bytes: Bytes of the image (PNG, JPEG, etc.)

    Returns:
        List of dicts with face locations and embeddings
    """
    try:
        # Load image from bytes
        image = Image.open(io.BytesIO(image_bytes))
        image_array = np.array(image)

        # Detect faces
        face_locations = face_recognition.face_locations(
            image_array,
            model=AIConfig.FACE_RECOGNITION_MODEL
        )

        # Generate face embeddings
        face_encodings = face_recognition.face_encodings(
            image_array,
            face_locations
        )

        # Prepare results
        faces = []
        for location, encoding in zip(face_locations, face_encodings):
            faces.append({
                'location': location,  # (top, right, bottom, left)
                'embedding': encoding,  # 128-dimensional vector
                'confidence': 1.0  # face_recognition doesn't provide confidence scores
            })

        return faces

    except Exception as e:
        print(f"Error extracting faces: {e}")
        return []


def extract_frame_from_video(video_bytes, frame_number=0):
    """
    Extract a specific frame from video bytes.
    Note: For PoC, we'll receive individual frames from the extension.
    This function is for future use if we receive video files.

    Args:
        video_bytes: Video file bytes
        frame_number: Frame number to extract (0-indexed)

    Returns:
        Image bytes (PNG format)
    """
    # This would use cv2 or similar library
    # For now, we'll assume the extension sends individual frames
    pass
