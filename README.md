# AI Navigator for Municipal Services - Diia Contest

AI-powered system for classifying and processing municipal utility problems in Ukrainian cities.

## Features

- 🎙️ **Voice Input**: Transcribe audio recordings of utility problems
- 🤖 **Smart Classification**: Automatically categorize problems using AI (KNN, LLM, or Hybrid approach)
- 📝 **Appeal Generation**: Generate formal appeal letters in Ukrainian
- 🚨 **Urgency Detection**: Identify emergency situations requiring immediate action
- 📊 **Vector Search**: RAG-based classification using embeddings

## Tech Stack

- **Backend**: FastAPI, Python 3.12+
- **Database**: PostgreSQL with pgvector extension
- **AI/ML**: OpenAI-compatible API (CodeMie), Gemini for transcription
- **ORM**: SQLModel with Alembic migrations

## Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL with pgvector extension
- uv package manager (or pip)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Korb1t/SombraAISquad_Diia.AIContest.git
cd SombraAISquad_Diia.AIContest
```

2. Copy environment variables:
```bash
cp .env.example .env
```

3. Configure your `.env` file with:
   - Database credentials
   - CodeMie API key
   - Classifier settings

4. Install dependencies:
```bash
uv sync
```

### Database Setup

1. Initialize the database:
```bash
uv run python app/scripts/init_db.py
```

This will:
- Create the pgvector extension
- Create all tables
- Load categories and examples with embeddings

### Running the Application

```bash
uv run fastapi dev --host 0.0.0.0 --port 8000
```

Or with Docker:
```bash
docker-compose up
```

### API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

## API Endpoints

### Classification
- `POST /api/v1/classify/` - Classify a utility problem

### Voice Input
- `POST /api/v1/voice/transcribe` - Transcribe audio to text
- `POST /api/v1/voice/extract` - Extract structured data from text

### Appeal Generation
- `POST /api/v1/appeal/generate` - Generate formal appeal letter

### Utilities
- `GET /api/v1/utils/health-check/` - Health check endpoint

## Configuration

### Classifier Types

Choose one in `.env`:
- `knn` - Fast vector-based classification
- `llm` - AI-powered classification with reasoning
- `hybrid` - KNN first, fallback to LLM if confidence < threshold

### Environment Variables

See `.env.example` for all available configuration options.

## Project Structure

```
app/
├── api/              # API routes and endpoints
├── core/             # Core configuration
├── data/             # Categories and dataset
├── db_models/        # Database models
├── llm/              # LLM client and prompts
├── schemas/          # Pydantic schemas
├── scripts/          # Database initialization
├── services/         # Business logic
│   └── classifier/   # Classification strategies
└── utils/            # Utility functions
```

## License

Copyright © 2025 Sombra AI Squad
