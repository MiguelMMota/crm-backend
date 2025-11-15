import json
import base64
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from celery_app.tasks import process_video_chunk, identify_participants

User = get_user_model()


class CallConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time call processing.
    Receives video/audio chunks from the browser extension.
    Sends back participant identifications and note summaries.
    """

    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = f'call_{self.user_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to call processing service'
        }))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Receive message from WebSocket (browser extension)
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'video_chunk':
                # Process video chunk for face recognition
                await self.handle_video_chunk(data)

            elif message_type == 'audio_chunk':
                # Process audio chunk for transcription
                await self.handle_audio_chunk(data)

            elif message_type == 'call_start':
                # Initialize call processing
                await self.handle_call_start(data)

            elif message_type == 'call_end':
                # Finalize call processing
                await self.handle_call_end(data)

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def handle_call_start(self, data):
        """Handle call start event"""
        await self.send(text_data=json.dumps({
            'type': 'call_started',
            'message': 'Call processing started'
        }))

    async def handle_video_chunk(self, data):
        """Process video chunk for face recognition"""
        video_data = data.get('video_data')  # base64 encoded video frame
        timestamp = data.get('timestamp')

        # Queue async task to process video chunk
        # This will be handled by Celery
        process_video_chunk.delay(
            user_id=self.user_id,
            video_data=video_data,
            timestamp=timestamp
        )

        # Send acknowledgment
        await self.send(text_data=json.dumps({
            'type': 'chunk_received',
            'chunk_type': 'video',
            'timestamp': timestamp
        }))

    async def handle_audio_chunk(self, data):
        """Process audio chunk for transcription"""
        audio_data = data.get('audio_data')  # base64 encoded audio
        timestamp = data.get('timestamp')

        # Queue async task for audio processing
        # Will be implemented in Celery tasks

        await self.send(text_data=json.dumps({
            'type': 'chunk_received',
            'chunk_type': 'audio',
            'timestamp': timestamp
        }))

    async def handle_call_end(self, data):
        """Handle call end event"""
        await self.send(text_data=json.dumps({
            'type': 'call_ended',
            'message': 'Call processing completed'
        }))

    # Handler for messages sent from Celery tasks
    async def participant_identified(self, event):
        """Send participant identification to WebSocket client"""
        await self.send(text_data=json.dumps({
            'type': 'participant_identified',
            'participant': event['participant'],
            'notes': event.get('notes', [])
        }))

    async def new_participant(self, event):
        """Send new participant notification to WebSocket client"""
        await self.send(text_data=json.dumps({
            'type': 'new_participant',
            'participant': event['participant']
        }))

    async def note_generated(self, event):
        """Send newly generated note to WebSocket client"""
        await self.send(text_data=json.dumps({
            'type': 'note_generated',
            'note': event['note']
        }))
