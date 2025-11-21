# 🏠 Utility Problem Classifier - Frontend

React + TypeScript + Vite + TailwindCSS + React Query + Leaflet

A mobile-first web application for classifying and routing utility problems to the appropriate municipal services in Ukraine. Built as an iPhone mockup interface mimicking the Diia app design.

## 📱 Features

- **iPhone Mockup UI** - Full iPhone 15 Pro interface simulation
- **Two Address Selection Flows:**
  - Home address (preset from user profile)
  - Other address (interactive map with search)
- **Voice Dictation** - Ukrainian language voice-to-text (Web Speech API)
- **Real-time Classification** - AI-powered problem categorization
- **Service Routing** - Automatic assignment to responsible municipal services
- **Feedback System** - User satisfaction collection

## 🚀 Quick Start

### Development Mode

```bash
# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend will be available at: **http://localhost:5173**

### Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

### Docker

```bash
# Build image
docker build -t diia-frontend .

# Run container
docker run -p 3000:80 diia-frontend
```

### Full Stack with Docker Compose

```bash
# From project root
docker-compose up
```

Frontend: `http://localhost:3000`  
Backend: `http://localhost:8000`

## 📁 Project Structure

```
frontend/
├── src/
│   ├── api/              # API client and React Query hooks
│   │   ├── client.ts     # Axios configuration
│   │   └── hooks.ts      # useSolveProblem hook
│   ├── components/       # React components
│   │   ├── PhoneMockup.tsx     # iPhone simulator
│   │   ├── Loader.tsx          # Loading screen with trident
│   │   ├── FeedbackModal.tsx   # User feedback collection
│   │   └── ErrorModal.tsx      # Error handling
│   ├── pages/            # Page components
│   │   ├── HomePage.tsx          # Service selection grid
│   │   ├── ClassifierPage.tsx   # Address type selection
│   │   ├── MapPage.tsx          # Interactive map (Leaflet)
│   │   ├── ProblemFormPage.tsx  # Problem description form
│   │   └── ResultPage.tsx       # Classification results
│   ├── lib/              # Utilities
│   │   └── utils.ts      # cn() for Tailwind classes
│   ├── types/            # TypeScript definitions
│   │   └── api.ts        # API types synced with backend
│   ├── assets/           # Static assets
│   │   └── trident.png   # Ukrainian trident logo
│   └── App.tsx           # Main app with routing
├── Dockerfile            # Production Docker image
└── vite.config.ts        # Vite config with API proxy
```

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```env
# Optional: Override API URL (default uses Vite proxy)
# VITE_API_URL=http://localhost:8000/api/v1
```

### API Proxy (Development)

Vite automatically proxies `/api` requests to backend:

```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- Request: `/api/v1/solve/` → `http://localhost:8000/api/v1/solve/`

### Import Aliases

Use `@/` for clean imports:

```typescript
import { api } from '@/api/client'
import { Loader } from '@/components/Loader'
import { cn } from '@/lib/utils'
```

## 📚 Technologies

- **React 18** - UI library with hooks
- **TypeScript** - Type safety
- **Vite** - Fast build tool with HMR
- **TailwindCSS** - Utility-first CSS framework
- **React Query** - Server state management with caching
- **Axios** - HTTP client
- **Leaflet** - Interactive maps (OpenStreetMap)
- **Lucide React** - Icon library
- **Web Speech API** - Voice dictation (Ukrainian)

## 🎨 Design System

- **Colors:** Diia-inspired gradient (blue → cyan → yellow)
- **Components:** Custom iPhone mockup with status bar
- **Typography:** System fonts with proper Ukrainian support
- **Icons:** Lucide React (consistent stroke width)
- **Spacing:** Tailwind spacing scale
- **Animations:** Smooth transitions with scale transforms

## 🗺️ Map Features

- **OpenStreetMap** integration
- **Reverse Geocoding** via Nominatim API
- **Interactive Marker** - drag & drop or click to place
- **Search Panel** - Mock street addresses (Lviv)
- **Controls:**
  - Zoom In/Out
  - My Location (GPS)
  - Search addresses

## 🎤 Voice Dictation

Uses **Web Speech API** with Ukrainian language support:

```typescript
const SpeechRecognition = window.webkitSpeechRecognition;
recognition.lang = 'uk-UA';
recognition.continuous = true;
recognition.interimResults = true;
```

**Browser Support:**
- ✅ Chrome / Edge (full support)
- ✅ Safari (partial)
- ❌ Firefox (not supported)

## 🔗 API Integration

### Main Endpoint: `/api/v1/solve/`

**Request:**
```json
{
  "user_info": {
    "name": "Василь Васильович Байдак",
    "address": "Володимира Великого 10",
    "city": "Львів",
    "phone": "+380123456789"
  },
  "problem_text": "У під'їзді не горить лампочка"
}
```

**Response:**
```json
{
  "classification": {
    "category_name": "Освітлення",
    "confidence": 0.85,
    ...
  },
  "service": {
    "service_info": {
      "service_name": "Львівобленерго",
      "service_phone": "+38 (032) 239-21-26",
      ...
    }
  },
  "appeal_text": "Доброго дня!\n\n..."
}
```

## 🛠️ Commands

```bash
npm run dev          # Start dev server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
```

## 📝 User Flow

1. **Home Screen** - Service grid (only "Utility Problems" active)
2. **Address Selection:**
   - Option A: "Home Address" (preset)
   - Option B: "Other Address" (map selection)
3. **Problem Description:**
   - Text input or voice dictation
   - Real-time waveform visualization
4. **Processing:** Loading screen with trident animation
5. **Results:**
   - Classification category
   - Responsible service contacts
   - Generated formal appeal letter
6. **Feedback:** User satisfaction survey

## 🇺🇦 Localization

- All UI text in Ukrainian
- Voice recognition: `uk-UA`
- Map labels: Ukrainian via Nominatim
- Date/time: Ukrainian format

## 🐳 Docker Deployment

The Dockerfile uses multi-stage build for optimal image size:

1. **Build stage:** Compile with Node.js
2. **Production stage:** Serve with Nginx

Default port: **80**

## 📄 License

Part of Diia.AI Contest submission by SombraAI Squad.

