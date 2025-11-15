"""
Face recognition module for matching faces against stored signatures.
"""
import numpy as np
from scipy.spatial.distance import cosine
from .config import AIConfig


def match_face(user_id, face_embedding):
    """
    Match a face embedding against stored face signatures.

    Args:
        user_id: ID of the user
        face_embedding: 128-dimensional face embedding array

    Returns:
        Relationship object if match found, None otherwise
    """
    from apps.signatures.models import FaceSignature
    from apps.relationships.models import Relationship

    # Get all face signatures for this user's relationships
    signatures = FaceSignature.objects.filter(
        relationship__user_id=user_id
    ).select_related('relationship')

    best_match = None
    best_similarity = 0

    for signature in signatures:
        # Convert stored embedding to numpy array
        stored_embedding = np.array(signature.embedding)

        # Calculate cosine similarity (1 - cosine distance)
        similarity = 1 - cosine(face_embedding, stored_embedding)

        if similarity > best_similarity and similarity >= AIConfig.FACE_MATCH_THRESHOLD:
            best_similarity = similarity
            best_match = signature.relationship

    return best_match


def create_face_signature(relationship, face_embedding, image_path=None):
    """
    Create a new face signature for a relationship.

    Args:
        relationship: Relationship object
        face_embedding: 128-dimensional face embedding array
        image_path: Optional path to source image

    Returns:
        FaceSignature object
    """
    from apps.signatures.models import FaceSignature

    signature = FaceSignature.objects.create(
        relationship=relationship,
        embedding=face_embedding.tolist(),
        image_path=image_path,
        confidence_score=1.0
    )

    return signature


def update_face_signature(relationship, new_embedding):
    """
    Update or add a new face signature for a relationship.
    This helps improve recognition over time.

    Args:
        relationship: Relationship object
        new_embedding: New face embedding to add

    Returns:
        FaceSignature object
    """
    from apps.signatures.models import FaceSignature

    # Check if we already have a very similar signature
    existing_signatures = FaceSignature.objects.filter(relationship=relationship)

    for sig in existing_signatures:
        stored_embedding = np.array(sig.embedding)
        similarity = 1 - cosine(new_embedding, stored_embedding)

        # If very similar, don't create duplicate
        if similarity > 0.95:
            return sig

    # Create new signature (multiple signatures per person improve accuracy)
    return create_face_signature(relationship, new_embedding)
