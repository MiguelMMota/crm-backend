"""
AI pipeline configuration.
Handles switching between OpenAI APIs and local models.
"""
from django.conf import settings


class AIConfig:
    """Configuration for AI services"""

    USE_OPENAI = settings.USE_OPENAI_APIS
    OPENAI_API_KEY = settings.OPENAI_API_KEY

    # Face recognition settings
    FACE_RECOGNITION_MODEL = 'hog'  # or 'cnn' for better accuracy but slower
    FACE_EMBEDDING_DIMENSIONS = 128

    # Voice recognition settings
    VOICE_EMBEDDING_DIMENSIONS = 512

    # Transcription settings
    if USE_OPENAI:
        TRANSCRIPTION_MODEL = 'whisper-1'  # OpenAI Whisper API
    else:
        TRANSCRIPTION_MODEL = 'base'  # Local Whisper model: tiny, base, small, medium, large

    # LLM settings for note extraction
    if USE_OPENAI:
        LLM_MODEL = 'gpt-4o'
        LLM_TEMPERATURE = 0.3
    else:
        LLM_MODEL = 'llama2'  # Or other local model
        LLM_TEMPERATURE = 0.3

    # Face matching threshold (cosine similarity)
    FACE_MATCH_THRESHOLD = 0.6

    # Voice matching threshold
    VOICE_MATCH_THRESHOLD = 0.7
