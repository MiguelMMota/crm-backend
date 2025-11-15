"""
Celery tasks for background processing of AI pipeline.
"""
import base64
import io
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from ai_pipeline.video_processor import extract_faces_from_frame
from ai_pipeline.face_recognition import match_face, create_face_signature
from ai_pipeline.audio_processor import transcribe_audio
from ai_pipeline.note_extractor import extract_notes_from_transcription


@shared_task
def process_video_chunk(user_id, video_data, timestamp):
    """
    Process video chunk to identify participants via face recognition.

    Args:
        user_id: ID of the user making the call
        video_data: Base64 encoded video frame
        timestamp: Timestamp of the video chunk
    """
    try:
        # Decode base64 video frame
        image_bytes = base64.b64decode(video_data)

        # Extract faces from frame
        faces = extract_faces_from_frame(image_bytes)

        # Match each face against existing signatures
        for face in faces:
            relationship = match_face(user_id, face['embedding'])

            if relationship:
                # Get recent notes for this relationship
                from apps.notes.models import Note
                recent_notes = Note.objects.filter(
                    relationship=relationship,
                    status='ACTIVE'
                ).order_by('-importance_score', '-created_at')[:5]

                # Send identification to WebSocket
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'call_{user_id}',
                    {
                        'type': 'participant_identified',
                        'participant': {
                            'id': relationship.id,
                            'name': relationship.name,
                            'relationship_type': relationship.relationship_type,
                        },
                        'notes': [
                            {
                                'id': note.id,
                                'text': note.note_text,
                                'importance': note.importance_score,
                                'created_at': note.created_at.isoformat(),
                            }
                            for note in recent_notes
                        ]
                    }
                )
            else:
                # New participant detected - will need to create profile later
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'call_{user_id}',
                    {
                        'type': 'new_participant',
                        'participant': {
                            'face_embedding': face['embedding'].tolist(),
                            'timestamp': timestamp,
                        }
                    }
                )

        return {'status': 'success', 'faces_found': len(faces)}

    except Exception as e:
        return {'status': 'error', 'message': str(e)}


@shared_task
def process_audio_chunk(user_id, audio_data, timestamp):
    """
    Process audio chunk for transcription.

    Args:
        user_id: ID of the user making the call
        audio_data: Base64 encoded audio data
        timestamp: Timestamp of the audio chunk
    """
    try:
        # Decode base64 audio
        audio_bytes = base64.b64decode(audio_data)

        # Transcribe audio
        transcription = transcribe_audio(audio_bytes)

        # Send transcription to WebSocket (optional, for real-time display)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'call_{user_id}',
            {
                'type': 'transcription_update',
                'transcription': transcription,
                'timestamp': timestamp,
            }
        )

        return {'status': 'success', 'transcription': transcription}

    except Exception as e:
        return {'status': 'error', 'message': str(e)}


@shared_task
def finalize_call_processing(user_id, interaction_id):
    """
    Finalize call processing after call ends.
    Generate notes from full transcription.

    Args:
        user_id: ID of the user
        interaction_id: ID of the interaction record
    """
    try:
        from apps.interactions.models import Interaction
        from apps.notes.models import Note

        interaction = Interaction.objects.get(id=interaction_id, user_id=user_id)

        # Extract notes from transcription
        notes_data = extract_notes_from_transcription(
            interaction.transcription,
            list(interaction.relationships.all())
        )

        # Create Note objects
        created_notes = []
        for note_data in notes_data:
            note = Note.objects.create(
                user_id=user_id,
                relationship_id=note_data['relationship_id'],
                interaction=interaction,
                note_text=note_data['text'],
                importance_score=note_data.get('importance', 5),
                status='ACTIVE'
            )
            created_notes.append(note)

            # Send note to WebSocket
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'call_{user_id}',
                {
                    'type': 'note_generated',
                    'note': {
                        'id': note.id,
                        'relationship_id': note.relationship_id,
                        'text': note.note_text,
                        'importance': note.importance_score,
                    }
                }
            )

        return {'status': 'success', 'notes_created': len(created_notes)}

    except Exception as e:
        return {'status': 'error', 'message': str(e)}


@shared_task
def identify_participants(user_id, face_embeddings):
    """
    Identify call participants from face embeddings.
    Used during call start to quickly identify known participants.
    """
    try:
        from apps.relationships.models import Relationship

        identified = []
        for embedding in face_embeddings:
            relationship = match_face(user_id, embedding)
            if relationship:
                identified.append({
                    'id': relationship.id,
                    'name': relationship.name,
                    'relationship_type': relationship.relationship_type,
                })

        return {'status': 'success', 'identified': identified}

    except Exception as e:
        return {'status': 'error', 'message': str(e)}
