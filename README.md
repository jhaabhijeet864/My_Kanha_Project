# 🕉️ My Kanha - AI Spiritual Companion

> *"Converse with Krishna through the timeless wisdom of the Bhagavad Gita"*

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com/)
[![PWA Ready](https://img.shields.io/badge/PWA-Ready-5A0FC8.svg)](https://web.dev/progressive-web-apps/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**My Kanha** is an AI-powered spiritual chatbot that brings the profound teachings of the Bhagavad Gita to life through conversational AI. Krishna responds as a **warm, personal friend** - not a verse-dumping machine. Users can ask life's deepest questions and receive guidance grounded in authentic scripture.

---

## ✨ Features

### 🎯 **Currently Working**
- ✅ **Smart Krishna Persona** - Warm, friendly responses like talking to a divine best friend
- ✅ **Warm Startup (Eager Init)** - ChromaDB and AI models pre-warmed on server boot (No first-hit lag)
- ✅ **Intelligent Message Routing** - Detects casual chat vs spiritual questions automatically
- ✅ **RAG-Powered Responses** - Answers grounded in 701 Bhagavad Gita verses
- ✅ **Progressive Web App (PWA)** - Install on mobile/desktop, works offline
- ✅ **Mobile-First Design** - Bottom navigation, touch-friendly, safe area support
- ✅ **Groq Cloud LLM** - Fast inference with llama-3.3-70b-versatile
- ✅ **Streaming Support** - Real-time SSE streaming for responsive experience
- ✅ **Multilingual** - English & Hindi language detection and responses
- ✅ **Safety Filters** - Content moderation with friendly redirects
- ✅ **Vector Search** - Semantic search across all 18 chapters using ChromaDB
- ✅ **JWT Authentication** - User registration, login, and token-based security
- ✅ **Persistent Chat History** - Link conversations to user accounts
- ✅ **Dark Mode** - Full dark theme support across all pages
- ✅ **API Documentation** - Interactive Swagger/ReDoc at `/docs`

### 🧠 **Smart Routing System**

The chatbot intelligently routes messages:

| Message Type | Example | Behavior |
|--------------|---------|----------|
| **Casual** | "Hello", "Thanks", "How are you?" | Quick friendly response, NO database query |
| **Spiritual** | "What is karma?", "I'm feeling lost" | RAG retrieval + verse context woven naturally |

**Triggers for Spiritual Mode:**
- Gita keywords: karma, dharma, yoga, soul, meditation, moksha
- Life struggles: anxious, confused, lost, depressed, stressed
- Deep questions: meaning of life, purpose, who am I
- Help requests: guide me, what should I do, advice
- Questions with 5+ words

### 📱 **PWA & Mobile Features**
- Install as native app on iOS/Android/Desktop
- Offline support with service worker caching
- Bottom navigation bar (4 tabs: Chat, Search, History, Settings)
- Safe area support for notched devices
- Touch-friendly 44px minimum tap targets
- Dynamic viewport units for mobile keyboards

### 📊 **Technical Highlights**
- **Warm Startup Optimization** - 95% reduction in first-hit latency via pre-warmed embeddings
- **701 verses indexed** across 18 chapters
- **384-dimensional embeddings** using sentence-transformers
- **3 verses per query** for focused, natural responses
- **Groq API** for fast cloud inference (llama-3.3-70b-versatile)
- **100% data coverage** validated with quality reports

---

## 🏗️ Architecture

```
My_Kanha_Project/
│
├── 📁 data/                    # Data Engineering Pipeline
│   ├── raw/                    # Original JSON datasets (7 sources)
│   ├── cleaned/                # Unified gita_master.json (701 verses)
│   └── scripts/                # ETL & validation scripts
│
├── 📁 backend/                 # FastAPI REST API
│   ├── app/
│   │   ├── api/               # Route handlers (chat, health, admin, auth)
│   │   ├── rag/               # RAG pipeline (retriever, embeddings, formatter)
│   │   ├── llm/               # LLM integration (Groq + Ollama)
│   │   ├── models/            # Pydantic schemas
│   │   ├── core/              # Safety rules, smart routing & prompts
│   │   ├── persistence/       # PostgreSQL/Data Connect interaction
│   │   └── utils/             # Language detection & text processing
│   ├── dataconnect/           # Firebase Data Connect backend config
│   ├── tests/                 # Pytest test suite
│   └── requirements.txt
│
├── 📁 dataconnect/             # Firebase Data Connect Global Config
│   └── schema/                # GraphQL schemas for PostgreSQL
│
├── 📁 vector_db/               # ChromaDB Persistent Storage
│   └── chroma/                # Indexed verse embeddings
│
├── 📁 web_app/                 # PWA Frontend (HTML/CSS/JS)
│   ├── manifest.json          # PWA manifest
│   ├── sw.js                  # Service worker
│   ├── offline.html           # Offline fallback
│   └── assets/                # CSS, JS, images
│
└── 📁 mobile_app/              # Flutter Mobile App (In Development)
```

### **Core Stack**
- **Frontend**: Vanilla JS (PWA) hosted on **Firebase Hosting**.
- **Backend**: **FastAPI** (Python) containerized with **Docker**.
- **Vector DB**: **ChromaDB** for semantic retrieval.
- **Data Persistence**: **PostgreSQL** via **Firebase Data Connect** for high-performance, structured data management.
- **LLM**: **Llama 3** (via Groq Cloud or Local Ollama).

---

## 🗄️ Database & Persistence

The project leverages a modern, hybrid data storage strategy:

1. **Semantic Knowledge**: All 701 verses are stored in **ChromaDB** as high-dimensional vectors, enabling semantic "context retrieval."
2. **User Data & History**: Managed via **Firebase Data Connect**, which provides a type-safe GraphQL interface on top of a **PostgreSQL** database.
3. **Local Fallback**: For edge deployments, the system supports a local **SQLite** database and JSON-based conversation storage.

---

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.11+
Git
Groq API Key (free at console.groq.com)
```

### 1️⃣ Clone & Setup

```bash
# Clone repository
git clone <repository-url>
cd My_Kanha_Project
```

#### Option A: Docker (Recommended)
```bash
# Start all services
docker-compose up --build
```
The API will be available at `http://localhost:8000`.

#### Option B: Manual Setup
```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
cd backend
pip install -r requirements.txt
```

### 2️⃣ Configure Environment

Create a `.env` file in the `backend/` directory:

```env
# LLM Configuration (Groq - Recommended)
LLM_PROVIDER="groq"
GROQ_API_KEY="your-groq-api-key-here"
LLM_MODEL="llama-3.3-70b-versatile"

# Or use Ollama for local inference
# LLM_PROVIDER="ollama"
# OLLAMA_BASE_URL="http://localhost:11434"
# LLM_MODEL="llama3"
```

### 3️⃣ Start Backend Server

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 4️⃣ Open the App

Navigate to: **http://127.0.0.1:8000**

### 5️⃣ Test Smart Routing

Try these messages to see the difference:

| Message | Expected Behavior |
|---------|-------------------|
| "Hello" | Quick friendly greeting, no verses |
| "What is karma?" | Verse context woven into response |
| "I'm feeling anxious" | Spiritual guidance with practical advice |

Check terminal logs for routing:
```
Casual message detected - skipping verse retrieval
Spiritual question - retrieved 3 verses
```

---

## 🔐 Authentication & User Management

**My Kanha** includes JWT-based authentication for user management and persistent chat history.

### **Key Features:**
- ✅ User registration with email validation
- ✅ Secure password hashing (PBKDF2)
- ✅ JWT token-based authentication
- ✅ Optional authentication (chat works with or without login)
- ✅ Persistent conversation history linked to users
- ✅ Session management (create, list, delete)

### **Quick Start:**

**1. Register a new user:**
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "seeker",
    "email": "seeker@example.com",
    "password": "SecurePass123!",
    "full_name": "John Seeker"
  }'
```

**2. Login and get JWT token:**
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "seeker",
    "password": "SecurePass123!"
  }'
```

**3. Use token for authenticated chat:**
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

curl -X POST "http://localhost:8000/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the meaning of life?",
    "language": "english"
  }'
```

### **Authentication Endpoints:**
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login & get JWT token
- `GET /auth/me` - Get current user profile
- `POST /auth/refresh` - Refresh expired token

📖 **Complete guide:** See [AUTHENTICATION.md](AUTHENTICATION.md)

---

## 📡 API Endpoints

### **Chat Endpoints**

#### `POST /chat`
Main chat endpoint with smart routing

**Request:**
```json
{
  "message": "How can I find peace of mind?",
  "language": "english",
  "top_k": 3
}
```

**Response:**
```json
{
  "response": "Hey friend, peace of mind is something we all seek...",
  "sources": [
    {
      "chapter": 2,
      "verse": 66,
      "english": "One who is not connected with the Supreme...",
      "similarity_score": 0.89
    }
  ],
  "metadata": {
    "model": "llama-3.3-70b-versatile",
    "message_type": "spiritual",
    "context_verses": 3
  }
}
```

#### `POST /chat/stream`
Streaming chat with Server-Sent Events (SSE)

---

### **Health Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Welcome message & API info |
| `/health/chroma` | GET | ChromaDB status & verse count |

---

### **Admin Endpoints** 🔐

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/admin/stats` | GET | Collection statistics |
| `/admin/llm-status` | GET | LLM availability & models |
| `/admin/reindex` | POST | Rebuild vector index |

---

## ⚙️ Configuration

### Environment Variables

```env
# Application
APP_NAME="Kanha API"
DEBUG=True

# LLM Configuration
LLM_PROVIDER="groq"           # "groq" or "ollama"
GROQ_API_KEY="gsk_..."        # Required for Groq
LLM_MODEL="llama-3.3-70b-versatile"
LLM_TEMPERATURE=0.75
LLM_MAX_TOKENS=768

# Embeddings
EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"

# Vector Database
CHROMA_PERSIST_DIR="./vector_db/chroma"

# RAG Configuration
TOP_K_RESULTS=3               # Reduced from 5 for focused responses
SIMILARITY_THRESHOLD=0.3

# Admin
API_KEY="your-secret-admin-key"
```

---

## 🧪 Testing

```bash
cd backend
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

---

## 📊 Dataset Statistics

| Metric | Value |
|--------|-------|
| **Total Verses** | 701 |
| **Chapters** | 18 |
| **Languages** | 3 (Sanskrit, English, Hindi) |
| **Embeddings** | 701 × 384 dimensions |
| **Vector Store** | ChromaDB (cosine similarity) |

---

## 🔒 Safety & Moderation

The chatbot includes friendly safety filters:

- ✅ **Harmful content detection** - Gentle redirection with empathy
- ✅ **Off-topic handling** - Friendly "that's outside my wheelhouse" response
- ✅ **Respectful interfaith** - Acknowledges all paths to truth
- ✅ **Technical questions** - Warm redirect to life/spiritual topics

---

## 📈 Roadmap

### ✅ Completed
- [x] Data pipeline (ETL, cleaning, validation)
- [x] Vector database setup (ChromaDB)
- [x] RAG retrieval system
- [x] LLM integration (Groq + Ollama)
- [x] FastAPI backend
- [x] Streaming chat support
- [x] Smart message routing (casual vs spiritual)
- [x] Warm Krishna persona
- [x] JWT Authentication
- [x] Conversation history persistence (Firebase Data Connect + PostgreSQL)
- [x] PWA support (manifest, service worker, offline)
- [x] Mobile-first responsive design
- [x] Bottom navigation
- [x] Dark mode support
- [x] API documentation
- [x] Warm Startup (Eager Init) Performance Optimization
- [x] Response quality fine-tuning
- [x] Docker deployment and orchestration

### 🚧 In Progress
- [ ] PWA icon generation
- [ ] Flutter mobile app

### 🎯 Future
- [ ] Voice interface
- [ ] Personalized recommendations
- [ ] Multi-language verse display
- [ ] Community reflections & sharing

---

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern async web framework
- **Groq API** - Fast cloud LLM inference
- **ChromaDB** - Vector database for RAG
- **Firebase Data Connect** - PostgreSQL managed connection
- **PostgreSQL** - Relational database for persistent user data
- **Docker** - Containerization and orchestration

### Frontend
- **Vanilla JS** - Lightweight, no framework
- **PWA** - Service worker, manifest, offline support
- **Firebase Hosting** - Fast global CDN deployment
- **CSS3** - Mobile-first, dark mode, safe areas

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

---

## 📄 License

This project is for educational and spiritual purposes.

---

## 🙏 Acknowledgments

- **Bhagavad Gita As It Is** - A.C. Bhaktivedanta Swami Prabhupada
- **Groq** - Fast LLM inference
- **FastAPI** - Modern Python web framework
- **ChromaDB** - Vector database solution

---

<div align="center">

**🕉️ May this project bring peace and wisdom to all seekers 🕉️**

*"You have the right to work only, but never to its fruits."*
— Bhagavad Gita 2:47

**Built with 💙 for spiritual seekers everywhere**

</div>
