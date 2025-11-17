# CRM Backend

AI-enriched CRM backend with video/audio processing, face/voice recognition, and automated note generation.

## Features

- **Video/Audio Processing**: Process video calls to extract frames and audio
- **Face Recognition**: Identify call participants using face embeddings (face_recognition library)
- **Voice Recognition**: Identify speakers using voice embeddings (placeholder for future implementation)
- **Transcription**: Convert speech to text using Whisper (OpenAI API or local)
- **Note Extraction**: Generate structured notes using GPT-4 or local LLM (Llama)
- **Real-time Updates**: WebSocket support for live call processing
- **Background Processing**: Celery tasks for async AI pipeline
- **Vector Search**: pgvector for similarity matching of face/voice embeddings

## Tech Stack

- **Backend**: Django 5.0 + Django REST Framework
- **Database**: PostgreSQL 16 with pgvector extension
- **Cache/Message Broker**: Redis
- **WebSocket**: Django Channels
- **Background Tasks**:
  - Celery Worker - Processes async AI tasks (video/audio processing, face recognition, transcription)
  - Celery Beat - Scheduler for periodic tasks (cleanup, reports, maintenance)
- **AI/ML**:
  - OpenAI API (Whisper, GPT-4) - Production
  - Local Whisper - Development transcription
  - face_recognition/DeepFace - Face recognition
  - Transformers (Llama) - Local LLM option

## Prerequisites

- Docker & Docker Compose
- (Optional) CUDA for GPU acceleration with local models

## Quick Start

### 1. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` if needed (default values work for local development):
- AI model selection: `USE_OPENAI_APIS=false` (uses local models, free)
- For production: Set `USE_OPENAI_APIS=true` and add your `OPENAI_API_KEY`

### 2. Start All Services

```bash
docker-compose up --build
```

This single command will:
- ✅ Start PostgreSQL with pgvector extension
- ✅ Start Redis for caching and message brokering
- ✅ Run Django migrations automatically
- ✅ Start Django development server (port 8000)
- ✅ Start Celery worker for async AI processing
- ✅ Start Celery beat for scheduled tasks

### 3. Create Superuser (Optional)

In a new terminal:

```bash
docker-compose exec web python manage.py createsuperuser
```

That's it! The API is now running at `http://localhost:8000`

## Alternative: Local Development (Without Docker)

If you prefer running services locally:

<details>
<summary>Click to expand local setup instructions</summary>

### Prerequisites
- Python 3.11+
- Poetry
- PostgreSQL 16+ with pgvector
- Redis

### Setup

```bash
# Install dependencies
poetry install

# Start PostgreSQL and Redis (or run in Docker)
docker-compose up postgres redis -d

# Configure environment
cp .env.example .env
# Edit .env: Set DB_HOST=localhost, REDIS_URL=redis://localhost:6379/0

# Run migrations
poetry run python manage.py migrate

# Create superuser
poetry run python manage.py createsuperuser
```

### Run Services (3 terminals)

**Terminal 1 - Django:**
```bash
poetry run python manage.py runserver
```

**Terminal 2 - Celery Worker:**
```bash
poetry run celery -A celery_app.celery_config worker -l info
```

**Terminal 3 - Celery Beat (optional):**
```bash
poetry run celery -A celery_app.celery_config beat -l info
```

</details>

## API Documentation

### Authentication

All endpoints except auth require `Authorization: Token <token>` header.

#### POST `/api/auth/users/register/`
Register a new user.

**Request:**
```json
{
  "username": "user123",
  "email": "user@example.com",
  "password": "securepass123",
  "password_confirm": "securepass123",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:**
```json
{
  "user": { "id": 1, "username": "user123", ... },
  "token": "abc123..."
}
```

#### POST `/api/auth/users/login/`
Login and receive auth token.

#### POST `/api/auth/users/logout/`
Logout (delete token).

#### GET `/api/auth/users/me/`
Get current user info.

### Relationships

#### GET `/api/relationships/`
List all relationships for current user.

Query params:
- `relationship_type`: Filter by type (FAMILY, FRIEND, etc.)
- `search`: Search by name, email, phone

#### GET `/api/relationships/{id}/`
Get relationship details with notes count.

#### POST `/api/relationships/`
Create new relationship.

#### PUT `/api/relationships/{id}/`
Update relationship.

#### DELETE `/api/relationships/{id}/`
Delete relationship.

### Interactions

#### GET `/api/interactions/`
List all interactions for current user.

Query params:
- `interaction_type`: Filter by type (VIDEO_CALL, PHONE_CALL, etc.)
- `search`: Search in transcription/summary

#### GET `/api/interactions/{id}/`
Get interaction details with full transcription.

#### POST `/api/interactions/`
Create new interaction.

### Notes

#### GET `/api/notes/`
List all notes for current user.

Query params:
- `relationship`: Filter by relationship ID
- `status`: Filter by status (ACTIVE, ARCHIVED, DELETED)
- `search`: Search in note text

#### PUT `/api/notes/{id}/`
Update note (e.g., change status).

### WebSocket

#### `ws://localhost:8000/ws/call/{user_id}/?token={auth_token}`
Real-time call processing WebSocket.

**Client → Server Messages:**
- `call_start` - Notify call has started
- `video_chunk` - Send video frame for processing
- `audio_chunk` - Send audio for transcription
- `call_end` - Notify call has ended

**Server → Client Messages:**
- `connection_established` - Connection confirmed
- `participant_identified` - Participant recognized with notes
- `new_participant` - Unknown participant detected
- `note_generated` - New note created
- `transcription_update` - Real-time transcription

## AI Pipeline

### Face Recognition

1. Extract faces from video frames using `face_recognition` library
2. Generate 128-dimensional embeddings
3. Store in `FaceSignature` model with pgvector
4. Match new faces using cosine similarity (threshold: 0.6)

### Transcription

**Production (OpenAI):**
- Uses Whisper API
- Higher accuracy, faster

**Development (Local):**
- Uses local Whisper model (base/small/medium)
- Free but requires more compute

### Note Extraction

**Production (GPT-4):**
- Extracts structured notes from transcription
- Identifies important facts per person
- Assigns importance scores

**Development (Llama/Placeholder):**
- Simpler keyword-based extraction
- Can be replaced with local Llama model

## Project Structure

```
crm-backend/
├── config/              # Django settings, URLs, ASGI
├── apps/
│   ├── users/          # User model, auth endpoints
│   ├── relationships/  # Contact management
│   ├── interactions/   # Call/meeting records
│   ├── notes/         # Auto-generated notes
│   └── signatures/    # Face/voice embeddings
├── ai_pipeline/       # AI processing modules
│   ├── config.py      # AI model configuration
│   ├── video_processor.py
│   ├── audio_processor.py
│   ├── face_recognition.py
│   ├── voice_recognition.py
│   └── note_extractor.py
├── websocket/         # WebSocket consumers
│   ├── consumers.py
│   └── routing.py
└── celery_app/        # Background tasks
    ├── celery_config.py
    └── tasks.py
```

## Development

### Run Tests

```bash
poetry run pytest
```

### Format Code

```bash
poetry run black .
```

### Lint

```bash
poetry run flake8
```

### Access Admin Panel

Navigate to `http://localhost:8000/admin` and login with superuser credentials.

## Deployment Considerations

1. **Environment Variables**: Set all production values in `.env`
2. **Database**: Use PostgreSQL 16+ with pgvector extension
3. **AI Models**:
   - Set `USE_OPENAI_APIS=true`
   - Configure `OPENAI_API_KEY`
4. **Redis**: Ensure Redis is accessible
5. **Static Files**: Run `python manage.py collectstatic`
6. **ASGI Server**: Use Daphne or Uvicorn for WebSocket support
7. **Celery**: Deploy worker and beat processes separately
8. **Security**:
   - Set `DEBUG=False`
   - Use strong `SECRET_KEY`
   - Configure `ALLOWED_HOSTS`
   - Enable HTTPS
   - Set proper CORS origins

## Troubleshooting

### pgvector Installation Issues

If pgvector fails to install, ensure PostgreSQL development headers are installed:

```bash
# macOS
brew install postgresql

# Ubuntu/Debian
sudo apt-get install postgresql-server-dev-16
```

### Face Recognition Library Issues

The `face_recognition` library requires dlib, which needs CMake:

```bash
# macOS
brew install cmake

# Ubuntu/Debian
sudo apt-get install cmake
```

### Local Whisper Performance

For better performance with local Whisper:
- Use GPU acceleration (CUDA)
- Use smaller models (tiny, base) for development
- Consider using faster-whisper for production local deployment
