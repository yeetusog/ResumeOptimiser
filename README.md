# Resume Optimizer

Resume Optimizer is a full-stack application that helps users improve their resume against a target job description. It evaluates ATS compatibility, identifies keyword gaps, generates stronger bullet points, and produces a polished, exportable resume in PDF format.

## Overview

This project combines:

- a FastAPI backend for resume parsing, ATS scoring, optimization, and PDF generation
- a React + Vite frontend for uploading resumes, editing generated content, and downloading results
- keyword matching logic to compare resume content against a job description
- optional AI-powered bullet generation when an Anthropic API key is configured
- a heuristic fallback for cases where external AI services are unavailable

## Features

- Resume upload and parsing from PDF, DOCX, TEX, and TXT files
- ATS score calculation based on keyword coverage
- Matched and missing keyword analysis
- Resume bullet optimization using AI or deterministic fallback logic
- LaTeX resume rendering with safe escaping for generated content
- PDF export using Tectonic
- Clean frontend workflow for scoring, optimizing, editing, and downloading resumes

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

## Project Structure

```text
resume-optimizer/
├── backend/
│   ├── app/
│   │   ├── ats.py
│   │   ├── compiler.py
│   │   ├── main.py
│   │   ├── parser.py
│   │   ├── sanitizer.py
│   │   └── templates/
│   │       └── resume.tex.j2
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .venv/
├── frontend/
│   ├── src/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── postcss.config.js
├── tests/
│   └── test_e2e_pipeline.py
├── .gitignore
├── README.md
└── CLAUDE.md
```

## Quick Start

### 1. Clone the repository

```bash
git clone <repository-url>
cd resume-optimizer
```

### 2. Set up the backend

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. Install Tectonic

Install Tectonic so the project can compile LaTeX into PDF output.

```bash
tectonic --version
```

If needed, install Tectonic from the official release package or via your package manager.

### 4. Start the backend

```bash
cd backend
source .venv/Scripts/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Start the frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

Then open the app in the browser at:

```text
http://localhost:5173
```

## Optional AI Configuration

If you want AI-powered bullet generation, set the following environment variables before starting the backend:

```bash
export ANTHROPIC_API_KEY="your_api_key_here"
export ANTHROPIC_MODEL="claude-3-5-sonnet-latest"
```

If no API key is configured, the application automatically falls back to its built-in heuristic generation logic.

## Docker

The backend includes a Dockerfile for local containerized execution:

```bash
cd backend
docker build -t resume-optimizer-backend .
docker run -p 8000:8000 resume-optimizer-backend
```

## Testing

```bash
cd backend
source .venv/Scripts/activate
python -m pytest -q
```

The test suite covers core ATS scoring and PDF generation behavior.

## Roadmap

Planned improvements include:

- stronger SEO and ATS keyword matching logic
- broader resume parsing coverage and validation
- improved deployment and environment configuration
- more comprehensive automated tests
- production-grade monitoring, logging, and persistence

## Contributing

Contributions are welcome. Please keep changes focused, test relevant behavior, and document any new setup requirements.
