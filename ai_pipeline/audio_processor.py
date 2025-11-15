"""
Audio processing module for transcription.
"""
import io
import tempfile
from .config import AIConfig


def transcribe_audio(audio_bytes):
    """
    Transcribe audio to text using Whisper (OpenAI API or local).

    Args:
        audio_bytes: Audio data in bytes (WAV, MP3, etc.)

    Returns:
        Transcription text
    """
    try:
        if AIConfig.USE_OPENAI:
            return transcribe_with_openai(audio_bytes)
        else:
            return transcribe_with_local_whisper(audio_bytes)
    except Exception as e:
        print(f"Transcription error: {e}")
        return ""


def transcribe_with_openai(audio_bytes):
    """
    Transcribe audio using OpenAI Whisper API.

    Args:
        audio_bytes: Audio data in bytes

    Returns:
        Transcription text
    """
    import openai
    from openai import OpenAI

    client = OpenAI(api_key=AIConfig.OPENAI_API_KEY)

    # Save audio to temporary file (OpenAI API requires file)
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
        temp_audio.write(audio_bytes)
        temp_audio_path = temp_audio.name

    try:
        with open(temp_audio_path, 'rb') as audio_file:
            transcription = client.audio.transcriptions.create(
                model=AIConfig.TRANSCRIPTION_MODEL,
                file=audio_file,
                response_format='text'
            )
        return transcription
    finally:
        # Clean up temporary file
        import os
        os.unlink(temp_audio_path)


def transcribe_with_local_whisper(audio_bytes):
    """
    Transcribe audio using local Whisper model.

    Args:
        audio_bytes: Audio data in bytes

    Returns:
        Transcription text
    """
    import whisper
    import torch

    # Load model (consider caching this)
    model = whisper.load_model(AIConfig.TRANSCRIPTION_MODEL)

    # Save audio to temporary file
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
        temp_audio.write(audio_bytes)
        temp_audio_path = temp_audio.name

    try:
        # Transcribe
        result = model.transcribe(temp_audio_path)
        return result['text']
    finally:
        # Clean up
        import os
        os.unlink(temp_audio_path)


def perform_speaker_diarization(audio_bytes):
    """
    Identify who said what in the audio.
    This is a placeholder for future implementation using pyannote.audio or similar.

    Args:
        audio_bytes: Audio data in bytes

    Returns:
        List of dicts with speaker segments: [{'speaker': 'SPEAKER_01', 'start': 0.0, 'end': 5.0, 'text': '...'}]
    """
    # Placeholder
    # TODO: Implement speaker diarization
    return []
