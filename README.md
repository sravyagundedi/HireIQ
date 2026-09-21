# HireIQ — Multimodal AI Interview Intelligence Platform


## Stack

- Frontend: React 18 + TypeScript + Vite
- Backend: FastAPI + Python 3.12
- Database: PostgreSQL + SQLAlchemy
- Queue: Celery + Redis
- Speech-to-text: OpenAI Whisper (open-source)
- Audio: PyDub
- LLM evaluation: OpenAI GPT-4o or Google Gemini
- NLP: spaCy + VADER
- PDF: ReportLab + Matplotlib
- Deployment: Docker Compose; adaptable to Render/Railway

## Main flow

Candidate -> MediaRecorder -> FastAPI -> Celery -> PyDub -> Whisper -> transcript
-> spaCy/VADER -> LLM rubric evaluation -> Pydantic validation -> PostgreSQL
-> PDF report / Hiring Manager dashboard.

## Run locally

### 1. Prerequisites

Install Docker Desktop and Git.

### 2. Configure environment

Copy `.env.example` to `.env` and add an LLM key.

### 3. Start

```bash
docker compose up --build
```

Frontend: http://localhost:5173  
Backend docs: http://localhost:8000/docs

### 4. First interview

Open the frontend, enter candidate information, start an interview, answer questions,
and wait for each answer to finish processing.

### 5. Dashboard

Open the "Manager Dashboard" link in the frontend.

## Local non-Docker development

Backend:

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

You still need PostgreSQL, Redis and ffmpeg available locally.

## Important project constraints

- API keys are server-side only.
- Whisper processing is asynchronous through Celery.
- LLM responses are validated with Pydantic before database storage.
- Uploaded audio is deleted after transcription.
- Rubrics are external YAML files.
- Candidate transcript data should not be logged in production.
- Transcription failures use Celery retry.
- PDF generation does not require a headless browser.
- Evaluation prompts explicitly instruct the model to avoid demographic bias.
- Dashboard candidate queries are paginated.

## Demo account

This starter does not implement authentication because the supplied brief does not specify an
authentication provider. The manager dashboard is therefore a protected-by-route UI placeholder
for demo purposes. Add JWT/OAuth before a real production deployment.

## Deliverables to prepare

1. Live deployment URL
2. GitHub repository
3. Sample interview recording
4. Sample generated PDF
5. Prompt templates and rubric YAML
6. Whisper WER analysis
7. Dashboard screenshots
8. Architecture diagram
9. AI bias review
10. README and demo instructions

See `docs/AI_BIAS_REVIEW.md`, `docs/ARCHITECTURE.md`, and `docs/WER_ANALYSIS.md`.

## Current implementation scope

This package is an internship-ready end-to-end starter implementation. The supplied brief
does not define an authentication mechanism, so authentication is intentionally left as a
next production-hardening step. The core candidate interview, async transcription, rubric-based
LLM evaluation, NLP enrichment, PDF report and hiring dashboard flows are included.

For a real hiring deployment, add authentication/authorization, encrypted object storage,
rate limiting, audit logging, stronger privacy controls, and formal model validation.
