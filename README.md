# 🏠 Utility Problem Classifier - Diia.AI Contest

**SombraAI Squad** submission for Diia.AI Contest

AI-powered system for classifying utility problems and routing them to the appropriate municipal services in Ukraine. Built as a mobile-first web application with Diia-inspired design.

## 🎯 Features

- **AI Classification** - Hybrid classifier (LLM + KNN + RAG) for problem categorization
- **Smart Service Routing** - Automatic assignment to responsible municipal services based on category and location
- **Appeal Generation** - AI-generated formal letters to services
- **Voice Input** - Ukrainian language voice dictation
- **Interactive Map** - Address selection with reverse geocoding
- **Mobile-First UI** - iPhone mockup interface following Diia design patterns

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  Frontend   │────▶│   Backend    │────▶│  PostgreSQL  │
│  (React)    │     │  (FastAPI)   │     │  + pgvector  │
└─────────────┘     └──────────────┘     └──────────────┘
      │                     │
      │                     │
      ▼                     ▼
  Vite/Nginx           LLM Service
```

### Stack

**Frontend:**
- React 18 + TypeScript
- Vite (build tool)
- TailwindCSS (styling)
- React Query (state management)
- Leaflet (maps)
- Lucide Icons

**Backend:**
- FastAPI (Python 3.11+)
- SQLModel + PostgreSQL
- pgvector (embeddings)
- LangChain (LLM orchestration)
- Groq API (classification)

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)

### Run with Docker Compose (Recommended)

```bash
# Clone repository
git clone <repo-url>
cd SombraAISquad_Diia.AIContest

# Create .env file with required variables
cp .env.example .env
# Edit .env and set your API keys and database credentials

# Start all services
docker-compose up --build

# Services will be available at:
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
# Database: localhost:5432
```

### Local Development

#### Backend

```bash
# Install uv (Python package manager)
pip install uv

# Install dependencies
uv sync

# Run database migrations
alembic upgrade head

# Initialize database with categories
python -m app.scripts.init_db

# Start server
uvicorn app.main:app --reload --port 8000
```

Backend: `http://localhost:8000`  
API Docs: `http://localhost:8000/docs`

#### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend: `http://localhost:5173`

## 📁 Project Structure

```
.
├── app/                    # Backend application
│   ├── api/               # API routes
│   │   └── routes/
│   │       ├── solve_problem.py    # Main orchestration endpoint
│   │       ├── classify.py         # Classification endpoint
│   │       └── ...
│   ├── services/          # Business logic
│   │   ├── classifier/    # Hybrid classifier (LLM + KNN)
│   │   ├── service_resolver.py  # Service routing logic
│   │   └── letter_generator.py  # Appeal text generation
│   ├── llm/              # LLM clients and prompts
│   ├── db_models/        # Database models
│   └── schemas/          # Pydantic schemas
│
├── frontend/              # Frontend application
│   ├── src/
│   │   ├── api/          # API client
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   └── types/        # TypeScript types
│   ├── Dockerfile
│   └── nginx.conf
│
├── alembic/              # Database migrations
├── docker-compose.yml    # Full stack orchestration
└── README.md
```

## 🔌 API Endpoints

### Main Endpoint: `/api/v1/solve/`

Complete flow: classification → service routing → appeal generation

**Request:**
```json
{
  "user_info": {
    "name": "Василь Васильович Байдак",
    "address": "Володимира Великого 10",
    "city": "Львів",
    "phone": "+380123456789"
  },
  "problem_text": "У під'їзді вже тиждень не горить лампочка"
}
```

**Response:**
```json
{
  "classification": {
    "category_id": "lighting",
    "category_name": "Освітлення",
    "confidence": 0.92,
    "is_urgent": false
  },
  "service": {
    "service_info": {
      "service_name": "Львівобленерго",
      "service_phone": "+38 (032) 239-21-26",
      "service_email": "kca@loe.lviv.ua"
    }
  },
  "appeal_text": "Доброго дня!\n\nПрошу звернути увагу..."
}
```

### Other Endpoints:

- `POST /api/v1/classify/` - Problem classification only
- `POST /api/v1/resolve_service/` - Service routing only
- `POST /api/v1/appeal/` - Appeal generation only
- `POST /api/v1/voice/transcribe/` - Voice transcription
- `GET /api/v1/utils/health-check/` - Health check

## 🎨 Frontend Features

### iPhone Mockup
- Realistic iPhone 15 Pro interface
- Working status bar (time, signal, battery)
- Dynamic Island
- Diia-inspired gradient background

### User Flows

**Flow 1: Home Address**
```
Services Grid → Utility Problems → Home Address
  → Problem Form → AI Processing → Results → Feedback
```

**Flow 2: Other Address**
```
Services Grid → Utility Problems → Other Address
  → Map Selection → Problem Form → AI Processing → Results → Feedback
```

### Voice Dictation
- Web Speech API with Ukrainian (`uk-UA`)
- Real-time waveform visualization
- Continuous dictation support

### Map Integration
- OpenStreetMap via Leaflet
- Reverse geocoding (Nominatim API)
- Interactive marker placement
- Address search with mock data

## 🛠️ Development

### Backend Development

```bash
# Run tests
pytest

# Format code
black app/
ruff check app/

# Type checking
mypy app/

# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

### Frontend Development

```bash
cd frontend

# Type checking
npm run type-check

# Linting
npm run lint

# Build
npm run build
```

## 🐳 Docker Commands

```bash
# Build and start all services
docker-compose up --build

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild specific service
docker-compose up --build frontend
```

## 📝 Environment Variables

Create `.env` file in project root:

```env
# Database
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_DB=diia_utility
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

# API Keys
GROQ_API_KEY=your_groq_api_key

# CORS (for development)
BACKEND_CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

## 🌐 Deployment

### Production Deployment

1. Set environment variables
2. Build and run with Docker Compose
3. Configure reverse proxy (nginx/traefik)
4. Set up SSL certificates

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Frontend Only

```bash
cd frontend
npm run build
# Deploy dist/ folder to any static hosting (Vercel, Netlify, etc.)
```

## 📊 Classification Categories

- Освітлення (Lighting)
- Водопостачання (Water Supply)
- Опалення (Heating)
- Каналізація (Sewage)
- Дороги / Тротуари (Roads/Sidewalks)
- Благоустрій (Landscaping)
- Сміття (Waste Management)
- Ліфти (Elevators)
- Паркування (Parking)
- Інше (Other)

## 👥 Team

**SombraAI Squad** - Diia.AI Contest Submission

## 📄 License

MIT License

