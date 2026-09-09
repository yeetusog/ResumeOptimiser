# Resume Optimizer

Resume Optimizer is a full-stack application that helps users improve a resume against a target job description. It evaluates ATS compatibility, identifies keyword gaps, generates stronger bullet points, and produces an exportable PDF resume.

## Overview

This project combines:

- a FastAPI backend for resume parsing, ATS scoring, optimization, and PDF generation
- a React + Vite frontend for uploading resumes, editing generated content, and downloading results
- keyword matching logic to compare resume content against a job description
- optional AI-powered bullet generation when an Anthropic API key is configured
- a heuristic fallback when external AI services are unavailable

## Tech Stack

### Frontend
- React
- Vite
- Tailwind CSS
- Monaco-based editor integration

### Backend
- FastAPI
- Uvicorn
- spaCy
- Jinja2
- pypdf and python-docx
- Tectonic

### Testing
- Pytest

## Quick Start

### 1. Prerequisites

- Python 3.11+
- Node.js 18+
- npm
- Tectonic for PDF compilation

### 2. Clone and set up the environment

```bash
git clone <repository-url>
cd ResumeOptimiser
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
```

On macOS/Linux, use:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On Windows CMD:

```cmd
.venv\Scripts\activate.bat
```

### 3. Configure environment variables

Copy the example file and adjust as needed:

```bash
cp .env.example .env
```

Default values are safe placeholders, and the backend loads them automatically when present.

### 4. Install the optional spaCy model

This app supports the optional spaCy English model for better keyword extraction:

```bash
python -m spacy download en_core_web_sm
```

If the model is unavailable, the app logs a warning and falls back to a deterministic heuristic pipeline instead of crashing.

### 5. Install Tectonic

Verify it is available:

```bash
tectonic --version
```

If needed, install it from the official release package or package manager for your OS.

### 6. Start the backend

From the repository root:

```bash
source .venv/bin/activate
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The backend health endpoint is available at:

```text
http://localhost:8000/health
```

### 7. Start the frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

Then open:

```text
http://localhost:5173
```

The Vite dev server proxies API traffic to port 8000 by default.

## Environment variables

The app reads the following values from the environment or the local `.env` file:

- `ANTHROPIC_API_KEY` — optional API key for AI bullet generation
- `ANTHROPIC_MODEL` — optional model name; default is `claude-3-7-sonnet-latest`
- `CORS_ORIGINS` — comma-separated allowed origins; default is `http://localhost:5173,http://127.0.0.1:5173`
- `MAX_UPLOAD_BYTES` — maximum request payload size for uploaded files
- `MAX_LATEX_INPUT_CHARS` — maximum size for compile input

The app is intended for local development and localhost-only use unless you explicitly set `CORS_ORIGINS` and deploy it in a controlled environment.

## Optional AI Configuration

If you want AI-powered bullet generation, define the following before starting the backend:

```bash
export ANTHROPIC_API_KEY="your_api_key_here"
export ANTHROPIC_MODEL="claude-3-7-sonnet-latest"
```

If no API key is configured, the backend logs the state and automatically falls back to its built-in heuristic generation logic.

## Testing

Run the project tests from the repository root:

```bash
source .venv/bin/activate
python -m pytest -q
```

This command includes the end-to-end pipeline tests under the root `tests/` directory.

## Docker

The backend includes a Dockerfile for local containerized execution:

```bash
cd backend
docker build -t resume-optimizer-backend .
docker run -p 8000:8000 resume-optimizer-backend
```

The container is intentionally kept local-first and should be used with localhost-only networking unless a controlled deployment environment is configured.

## Troubleshooting

- `pytest` cannot find tests: run from the repository root instead of inside `backend/`
- Vite backend requests fail: ensure the backend is running on port 8000 and the frontend proxy is unchanged
- PDF export fails: confirm Tectonic is installed and available on `PATH`
- AI generation is unavailable: set `ANTHROPIC_API_KEY` and verify the model name is supported
- spaCy warnings: install `en_core_web_sm` if you want the full NLP model

## Contributing

Contributions are welcome. Please keep changes focused, test relevant behavior, and document new setup requirements.
