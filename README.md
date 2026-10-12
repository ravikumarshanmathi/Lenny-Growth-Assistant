# 🚀 The Lenny Growth Assistant

> AI-powered conversational assistant for product & growth managers — grounded in Lenny's Podcast transcripts.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB?style=flat-square&logo=react)](https://react.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat-square&logo=postgresql)](https://www.postgresql.org)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-000000?style=flat-square)](https://ollama.ai)
[![Vite](https://img.shields.io/badge/Vite-5-646CFF?style=flat-square&logo=vite)](https://vitejs.dev)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat-square&logo=docker)](https://docs.docker.com/compose/)

---

## 📑 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Getting Started](#-getting-started)
  - [Option A — Docker Compose (Recommended)](#option-a--docker-compose-recommended-one-command-startup)
  - [Option B — Run Everything Locally (Without Docker)](#option-b--run-everything-locally-without-docker)
- [Setting Up Ollama (Local LLM)](#-setting-up-ollama-local-llm)
- [Switching LLM Providers](#-switching-llm-providers)
- [Data Ingestion (Transcripts)](#-data-ingestion-transcripts)
- [Running Tests](#-running-tests)
- [API Reference](#-api-reference)
- [Environment Variables Reference](#-environment-variables-reference)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)

---

## ✨ Features

| Feature | Description |
|---|---|
| **RAG-powered Q&A** | Ask product & growth questions grounded in 500+ hours of Lenny's Podcast transcripts with source citations |
| **Essay Generation** | Generate ~1,250-word "Ship 30 for 30" style essays with expert-grounded references |
| **Artifact Viewer** | Preview Markdown / HTML / CSS artifacts in a secure, sandboxed side panel |
| **Provider Toggle** | Seamlessly switch between Cloud LLMs (Anthropic Claude, OpenAI GPT) and local inference via Ollama |
| **Session Persistence** | Full chat history stored in PostgreSQL with timestamps and metadata |
| **Structured Logging** | JSON-formatted request/response logging with middleware |

---

## 🏗 Architecture

```
┌──────────────┐       ┌───────────────┐       ┌────────────────┐
│   React UI   │──────▶│   FastAPI     │──────▶│  PostgreSQL    │
│   (Vite)     │  HTTP │   Backend     │  SQL  │  + pgvector    │
│   :5173      │◀──────│   :8000       │◀──────│  :5432         │
└──────────────┘       └───────┬───────┘       └────────────────┘
                               │
                    ┌──────────┴──────────┐
                    │    LLM Provider     │
                    │  ┌───────────────┐  │
                    │  │ Ollama (local)│  │
                    │  │ :11434        │  │
                    │  ├───────────────┤  │
                    │  │ Anthropic API │  │
                    │  ├───────────────┤  │
                    │  │ OpenAI API    │  │
                    │  └───────────────┘  │
                    └─────────────────────┘
```

**Data Flow:**
1. User sends a message from the React frontend
2. FastAPI backend receives it, retrieves relevant transcript chunks via RAG (pgvector similarity search)
3. Chunks + user query are sent to the configured LLM provider (Ollama / Claude / GPT)
4. LLM generates a grounded response with citations
5. Response is streamed back to the frontend and persisted in PostgreSQL

---

## 📂 Project Structure

```
lenny-growth-assistant/
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── main.py             # App entrypoint, middleware, routers
│   │   ├── config.py           # Pydantic settings (env vars)
│   │   ├── api/
│   │   │   ├── chat.py         # POST /api/chat — send messages
│   │   │   ├── sessions.py     # CRUD /api/sessions — manage chat sessions
│   │   │   ├── health.py       # GET /health — readiness probe
│   │   │   ├── schemas/        # Pydantic request/response models
│   │   │   └── middleware/     # Structured logging middleware
│   │   ├── agent/
│   │   │   ├── orchestrator.py # Routes queries to the correct tool/provider
│   │   │   ├── providers/      # Ollama, Anthropic, OpenAI adapters
│   │   │   ├── prompts/        # System prompt templates
│   │   │   └── tools/          # Agent tools (RAG retrieval, essay writer)
│   │   ├── rag/
│   │   │   ├── chunker.py      # Text chunking logic
│   │   │   ├── embedder.py     # Sentence-transformer embeddings
│   │   │   ├── retriever.py    # pgvector similarity search
│   │   │   └── preprocessor.py # Transcript preprocessing
│   │   └── db/
│   │       ├── models.py       # SQLAlchemy models (sessions, messages, chunks)
│   │       └── session.py      # Async engine & session factory
│   ├── tests/                  # Pytest test suite
│   ├── init_db.py              # Standalone DB table creation script
│   ├── Dockerfile              # Backend Docker image
│   └── requirements.txt        # Python dependencies
│
├── frontend/                   # React + Vite UI
│   ├── src/
│   │   ├── App.jsx             # Main application component
│   │   ├── main.jsx            # React DOM entry
│   │   ├── components/
│   │   │   ├── ChatFeed.jsx        # Message list & rendering
│   │   │   ├── ChatInterface.jsx   # Input box & send logic
│   │   │   ├── ArtifactViewer.jsx  # Sandboxed artifact preview
│   │   │   ├── Sidebar.jsx         # Session list & navigation
│   │   │   ├── CitationCard.jsx    # Source citation display
│   │   │   ├── ProviderDropdown.jsx# LLM provider selector
│   │   │   └── LoginModal.jsx      # Auth modal
│   │   ├── utils/              # API client, DOMPurify wrapper
│   │   └── styles/             # CSS design system
│   ├── index.html              # HTML entry
│   ├── vite.config.js          # Vite config with API proxy
│   ├── tailwind.config.js      # Tailwind CSS config
│   ├── Dockerfile              # Frontend Docker image
│   └── package.json            # Node dependencies
│
├── data/                       # Transcripts & ingestion
│   ├── ingest.py               # Bulk transcript ingestion script
│   ├── raw_transcripts/        # Raw source transcripts
│   ├── transcripts/            # Processed transcripts
│   └── scripts/                # Helper scripts
│
├── docs/                       # Documentation
│   ├── PRD.md                  # Product Requirements Document
│   ├── architecture.md         # Architecture specification
│   └── design.md               # UI/UX design specification
│
├── agent_transcripts/          # AI agent iteration logs
├── docker-compose.yml          # Full-stack orchestration
├── .env.example                # Environment template
└── .gitignore
```

---

## 📋 Prerequisites

Make sure the following are installed on your machine before proceeding:

| Tool | Version | Required For | Install Link |
|---|---|---|---|
| **Docker Desktop** | 20.10+ | Docker Compose setup | [docker.com/get-started](https://docs.docker.com/get-docker/) |
| **Docker Compose** | v2+ | Orchestrating services | Included with Docker Desktop |
| **Ollama** | Latest | Local LLM inference | [ollama.ai/download](https://ollama.ai/download) |
| **Python** | 3.11+ | Backend (local dev only) | [python.org](https://www.python.org/downloads/) |
| **Node.js** | 20+ | Frontend (local dev only) | [nodejs.org](https://nodejs.org/) |
| **Git** | Latest | Cloning the repository | [git-scm.com](https://git-scm.com/) |

> **Note:** If you use **Option A (Docker Compose)**, you only need Docker Desktop and Ollama installed. Python and Node.js are not required.

---

## 🚀 Getting Started

### Option A — Docker Compose (Recommended, One-Command Startup)

This spins up **PostgreSQL + Backend + Frontend** with a single command.

#### Step 1: Clone the Repository

```bash
git clone <repo-url>
cd lenny-growth-assistant
```

#### Step 2: Create the `.env` File

```bash
cp .env.example .env
```

Open `.env` in your editor and review the defaults. **For Ollama (default), no API keys are needed.**

> ⚠️ **Important:** If running Ollama on your **host machine** (not inside Docker), change:
> ```env
> OLLAMA_BASE_URL=http://host.docker.internal:11434
> ```
> This allows the Docker container to reach Ollama running on your PC.

#### Step 3: Start Ollama & Pull a Model

_(See the [Ollama section](#-setting-up-ollama-local-llm) below for detailed instructions)_

```bash
# Start the Ollama server (if not already running)
ollama serve

# Pull the default model (in a new terminal)
ollama pull llama3:8b
```

#### Step 4: Start All Services

```bash
docker compose up --build
```

This will:
1. Pull & start **PostgreSQL 16** with the **pgvector** extension (port `5432`)
2. Build & start the **FastAPI backend** (port `8000`)
3. Build & start the **React frontend** (port `5173`)

#### Step 5: Open the Application

| Service | URL |
|---|---|
| 🌐 **Frontend** | [http://localhost:5173](http://localhost:5173) |
| 🔌 **Backend API** | [http://localhost:8000](http://localhost:8000) |
| 📖 **Swagger Docs** | [http://localhost:8000/docs](http://localhost:8000/docs) |
| 📖 **ReDoc** | [http://localhost:8000/redoc](http://localhost:8000/redoc) |
| 💚 **Health Check** | [http://localhost:8000/health](http://localhost:8000/health) |

#### Step 6: Stop All Services

```bash
# Graceful shutdown (preserves data)
docker compose down

# Full cleanup (removes volumes/data too)
docker compose down -v
```

---

### Option B — Run Everything Locally (Without Docker)

Use this approach for development if you prefer running each service directly on your machine.

#### Step 1: Start PostgreSQL with pgvector

You need a PostgreSQL 16 instance with the `pgvector` extension. The easiest way is still via Docker:

```bash
docker run -d \
  --name lenny-db \
  -e POSTGRES_USER=lenny \
  -e POSTGRES_PASSWORD=lenny_dev_password \
  -e POSTGRES_DB=lenny_growth_assistant \
  -p 5432:5432 \
  pgvector/pgvector:pg16
```

Wait a few seconds for it to initialize, then verify:

```bash
docker logs lenny-db
# Look for: "database system is ready to accept connections"
```

#### Step 2: Start Ollama

```bash
ollama serve
# In another terminal:
ollama pull llama3:8b
```

#### Step 3: Set Up the Backend

```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment
python -m venv venv

# Activate it
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (CMD):
.\venv\Scripts\activate.bat
# macOS / Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Create or edit `backend/.env` with **local** connection details:

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3:8b
DATABASE_URL=postgresql+asyncpg://lenny:lenny_dev_password@localhost:5432/lenny_growth_assistant
POSTGRES_USER=lenny
POSTGRES_PASSWORD=lenny_dev_password
POSTGRES_DB=lenny_growth_assistant
```

> **Key difference from Docker:** `OLLAMA_BASE_URL` uses `localhost` instead of `ollama` (the Docker service name).

Initialize the database tables:

```bash
python init_db.py
```

Start the backend server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ Backend is now running at **http://localhost:8000**

#### Step 4: Set Up the Frontend

Open a **new terminal**:

```bash
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

✅ Frontend is now running at **http://localhost:5173**

> **Note:** The Vite dev server proxies `/api/*` and `/health/*` requests to the backend. When running locally without Docker, you may need to update `vite.config.js` to change the proxy target from `http://backend:8000` to `http://localhost:8000`:
>
> ```js
> // vite.config.js — proxy target for local dev
> proxy: {
>   '/api': {
>     target: 'http://localhost:8000',
>     changeOrigin: true,
>   },
>   '/health': {
>     target: 'http://localhost:8000',
>     changeOrigin: true,
>   },
> },
> ```

---

## 🤖 Setting Up Ollama (Local LLM)

Ollama lets you run large language models locally on your machine — **completely free, no API keys required**.

### 1. Install Ollama

| Platform | Install Command / Link |
|---|---|
| **Windows** | Download from [ollama.ai/download](https://ollama.ai/download) |
| **macOS** | `brew install ollama` or download from [ollama.ai/download](https://ollama.ai/download) |
| **Linux** | `curl -fsSL https://ollama.ai/install.sh \| sh` |

### 2. Start the Ollama Server

```bash
ollama serve
```

This starts the Ollama API server on `http://localhost:11434`.

> 💡 On Windows/macOS, if you installed the desktop app, Ollama may already be running in the system tray.

### 3. Pull a Model

```bash
# Recommended default (good balance of speed & quality):
ollama pull llama3:8b

# Lighter alternative (faster, less VRAM):
ollama pull phi3:mini

# Larger, higher quality:
ollama pull llama3:70b
```

### 4. Verify It's Working

```bash
# Check if the server is running
curl http://localhost:11434

# Output: "Ollama is running"

# List downloaded models
ollama list

# Test a quick prompt
ollama run llama3:8b "Hello, how are you?"
```

### 5. Configure the App to Use Ollama

In your `.env` file, set:

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434       # For local dev
# OLLAMA_BASE_URL=http://host.docker.internal:11434  # For Docker on host Ollama
# OLLAMA_BASE_URL=http://ollama:11434        # If running Ollama as a Docker service
OLLAMA_MODEL=llama3:8b
```

### Ollama URL Cheat Sheet

| Scenario | `OLLAMA_BASE_URL` Value |
|---|---|
| Backend runs locally, Ollama runs locally | `http://localhost:11434` |
| Backend runs in Docker, Ollama runs on host | `http://host.docker.internal:11434` |
| Both run in Docker (same compose network) | `http://ollama:11434` |

### Model Recommendations

| Model | VRAM Needed | Speed | Quality | Best For |
|---|---|---|---|---|
| `phi3:mini` | ~3 GB | ⚡ Fast | ★★★☆ | Quick testing, low-resource machines |
| `llama3:8b` | ~5 GB | ⚡ Fast | ★★★★ | **Default — recommended for most users** |
| `mistral:7b` | ~5 GB | ⚡ Fast | ★★★★ | Good alternative to Llama 3 |
| `llama3:70b` | ~40 GB | 🐢 Slow | ★★★★★ | Best quality, needs powerful GPU |

---

## 🔄 Switching LLM Providers

The app supports three LLM backends. Switch between them by changing your `.env` file:

### Ollama (Local — Default, Free)

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3:8b
```

### Anthropic Claude (Cloud)

```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxx
```

Get your API key at [console.anthropic.com](https://console.anthropic.com/)

### OpenAI GPT (Cloud)

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx
```

Get your API key at [platform.openai.com](https://platform.openai.com/api-keys)

> **Provider Resolution Logic:** The app uses a priority system:
> 1. If `LLM_PROVIDER=anthropic` and `ANTHROPIC_API_KEY` is set → uses Claude
> 2. If `LLM_PROVIDER=openai` and `OPENAI_API_KEY` is set → uses OpenAI
> 3. Otherwise → falls back to **Ollama** (zero-cost default)

After changing the provider, **restart the backend** for changes to take effect:
```bash
# Docker
docker compose restart backend

# Local
# Stop uvicorn (Ctrl+C) and re-run:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 📥 Data Ingestion (Transcripts)

Before the RAG pipeline can answer questions, you need to ingest transcript data into the database.

### 1. Add Transcript Files

Place your transcript files (`.txt` or `.md`) in one of these directories:

```
data/raw_transcripts/
data/transcripts/
agent_transcripts/
```

**File naming convention:**
```
{episode_id}_{guest_name}_{title_slug}.txt
```
Example: `ep_301_elena_verna_growth_loops.txt`

**Optional metadata headers** (at the top of each file):
```
Episode: How Elena Verna Thinks About Growth
Guest: Elena Verna
---
(transcript content below)
```

### 2. Run the Ingestion Script

```bash
# From the project root directory
python data/ingest.py
```

This script will:
1. Load the `all-MiniLM-L6-v2` sentence-transformer embedding model
2. Scan all candidate directories for `.txt` and `.md` files
3. Chunk each transcript into ~400-word segments with 50-word overlap
4. Generate vector embeddings for each chunk
5. Store chunks + embeddings in the `transcript_chunks` table (pgvector)
6. **Skip files already indexed** (idempotent — safe to re-run)

> **Note:** Make sure PostgreSQL is running and the `DATABASE_URL` in your `.env` points to it. If running locally, use `postgresql://lenny:lenny_dev_password@localhost:5432/lenny_growth_assistant` (without `+asyncpg`).

---

## 🧪 Running Tests

```bash
cd backend

# Activate virtual environment if not already active
# Windows: .\venv\Scripts\Activate.ps1
# macOS/Linux: source venv/bin/activate

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run a specific test file
pytest tests/test_health.py
pytest tests/test_llm_factory.py
pytest tests/test_rag_engine.py
pytest tests/test_sessions.py
```

---

## 📡 API Reference

### Health Check

```
GET /health
```
Returns service status, uptime, LLM provider info, and system details.

### Chat

```
POST /api/chat
Content-Type: application/json

{
  "session_id": "uuid-string",
  "message": "What are the best growth loops?",
  "provider": "ollama"          // optional override
}
```

### Sessions

```
GET    /api/sessions              # List all sessions
POST   /api/sessions              # Create a new session
GET    /api/sessions/{id}         # Get session with messages
DELETE /api/sessions/{id}         # Delete a session
```

> 📖 Full interactive docs available at **http://localhost:8000/docs** (Swagger UI)

---

## 📝 Environment Variables Reference

| Variable | Default | Description |
|---|---|---|
| `LLM_PROVIDER` | `ollama` | LLM backend: `ollama`, `anthropic`, or `openai` |
| `OLLAMA_BASE_URL` | `http://ollama:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3:8b` | Ollama model name |
| `ANTHROPIC_API_KEY` | _(empty)_ | Anthropic API key for Claude |
| `OPENAI_API_KEY` | _(empty)_ | OpenAI API key for GPT |
| `POSTGRES_USER` | `lenny` | PostgreSQL username |
| `POSTGRES_PASSWORD` | `lenny_dev_password` | PostgreSQL password |
| `POSTGRES_DB` | `lenny_growth_assistant` | PostgreSQL database name |
| `DATABASE_URL` | `postgresql+asyncpg://...` | Full async database connection string |
| `BACKEND_HOST` | `0.0.0.0` | Backend bind host |
| `BACKEND_PORT` | `8000` | Backend bind port |
| `BACKEND_RELOAD` | `true` | Hot-reload on code changes |
| `LOG_LEVEL` | `info` | Logging verbosity |
| `VITE_API_BASE_URL` | `http://localhost:8000` | Frontend → Backend URL |
| `CHUNK_SIZE` | `512` | RAG chunk size (tokens) |
| `CHUNK_OVERLAP` | `64` | RAG chunk overlap (tokens) |
| `RETRIEVAL_TOP_K` | `10` | Number of chunks to retrieve |
| `RERANK_TOP_K` | `5` | Number of chunks after re-ranking |

---

## 🔧 Troubleshooting

### Common Issues

<details>
<summary><strong>❌ "Connection refused" when backend tries to reach Ollama</strong></summary>

**Cause:** The backend can't connect to the Ollama server.

**Fix (Docker):**
```env
# If Ollama runs on your host machine (not in Docker):
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

**Fix (Local):**
```env
# Make sure Ollama is running:
ollama serve

# And use localhost:
OLLAMA_BASE_URL=http://localhost:11434
```
</details>

<details>
<summary><strong>❌ "model not found" error from Ollama</strong></summary>

**Cause:** The model specified in `OLLAMA_MODEL` hasn't been pulled yet.

**Fix:**
```bash
ollama pull llama3:8b
# or whatever model is in your .env:
ollama pull phi3:mini
```
</details>

<details>
<summary><strong>❌ Frontend shows "Network Error" or can't reach the backend</strong></summary>

**Cause:** The Vite proxy is pointing to the wrong backend URL.

**Fix (Local dev):** Update `frontend/vite.config.js`:
```js
target: 'http://localhost:8000',   // not http://backend:8000
```

**Fix (Docker):** The Docker Compose config handles this automatically. Make sure the backend container is healthy:
```bash
docker compose ps
docker compose logs backend
```
</details>

<details>
<summary><strong>❌ Database connection errors</strong></summary>

**Cause:** PostgreSQL isn't running or the connection string is wrong.

**Fix:**
```bash
# Check if the DB container is running
docker compose ps db
docker compose logs db

# Test the connection
docker exec -it lenny-db psql -U lenny -d lenny_growth_assistant -c "SELECT 1;"
```
</details>

<details>
<summary><strong>❌ "pg_isready" healthcheck keeps failing</strong></summary>

**Cause:** PostgreSQL hasn't finished starting up yet.

**Fix:** Wait 10–15 seconds and try again. The `docker-compose.yml` has a health check with a start period. Run:
```bash
docker compose up --build --wait
```
</details>

<details>
<summary><strong>❌ Frontend hot-reload not working in Docker</strong></summary>

**Cause:** File-watching may not work across Docker volume mounts on some OSes.

**Fix:** Add polling to `vite.config.js`:
```js
server: {
  watch: {
    usePolling: true,
  },
},
```
</details>

<details>
<summary><strong>❌ "Out of memory" when running Ollama models</strong></summary>

**Cause:** The model requires more VRAM/RAM than available.

**Fix:** Switch to a smaller model:
```env
OLLAMA_MODEL=phi3:mini
```
```bash
ollama pull phi3:mini
```
</details>

---

## 📄 License

MIT
