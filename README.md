# Global Opportunity Tracker

An AI-powered automated system designed to discover, track, extract, and index global scholarships, fellowships, accelerators, grants, and creative opportunities for students, founders, and researchers.

## Project Structure

```
├── backend/                       # Python FastAPI Application
│   ├── app/
│   │   ├── ai/                    # Anthropic Claude & OpenAI embeddings pipelines
│   │   ├── api/                   # REST API routes (opportunities, search, tracker)
│   │   ├── models/                # SQLAlchemy database schema models
│   │   ├── notifications/         # Email (SendGrid) & Telegram Bot integrations
│   │   ├── pipeline/              # Deduplication, AI extraction & DB synchronizer
│   │   └── scrapers/              # Beautiful Soup & RSS scrapers
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                      # Next.js 14 Web Application
│   ├── src/app/
│   │   ├── globals.css            # Aetheric Glass Glassmorphism Theme stylesheet
│   │   ├── page.tsx               # Opportunity Discovery dashboard
│   │   └── tracker/page.tsx       # Kanban Board application tracker
│
├── .github/workflows/             # Automated daily scrape Actions runner
└── docker-compose.yml             # Local PostgreSQL & Redis environment
```

## Quick Start (5 Minutes)

### 1. Launch Backend Server
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
- Interactive API Docs will be available at http://localhost:8000/docs
- Local database file `opportunities.db` will automatically initialize on startup.

### 2. Launch Frontend Dashboard
```bash
cd frontend
npm install
npm run dev
```
- Open http://localhost:3000 (or the active Next.js port) in your browser.

## Key Features

- **Aetheric Glass UI**: Premium dark mode visual styling.
- **pgvector Vector Search**: Natural language semantic queries. If SQLite is used in local development, it computes similarity in Python using a cosine distance fallback.
- **Smart Scraper Engine**: Automates item collection from RSS and main news sites, parses them, and falls back to structured templates if keys are missing.
