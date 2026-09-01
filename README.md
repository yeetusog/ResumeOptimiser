# Resume Optimizer

Resume Optimizer is a full-stack application that helps users improve their resume against a target job description. The system analyzes a resume, scores it for ATS compatibility, identifies missing keywords, rewrites bullet points for better alignment, and compiles a polished LaTeX-based resume into a downloadable PDF.

## Project Overview

This project combines:

- A FastAPI backend for parsing resumes, checking ATS fit, generating optimized content, and compiling PDF output
- A Vite + React frontend for uploading resumes, editing the generated LaTeX, and downloading the final PDF
- A keyword and scoring engine that compares resume content with the target job description
- An optional AI optimization flow using Anthropic’s API when an API key is provided
- A fallback heuristic generator so the app still works without an external LLM

## Stack

### Frontend
- React 18
- Vite
- Monaco editor integration for LaTeX editing
- Tailwind CSS for styling

### Backend
- FastAPI
- Uvicorn
- spaCy for keyword extraction
- Jinja2 template rendering
- Tectonic for PDF generation from LaTeX
- pypdf and python-docx for document parsing

### Testing
- Pytest
- End-to-end pipeline checks for ATS scoring and PDF compilation

---

## Features Implemented

### Completed Services

1. Resume upload and parsing
   - Supports `.pdf`, `.docx`, `.tex`, and `.txt`
   - Extracts readable text from uploaded files
   - Returns cleaned content to the frontend for editing and scoring

2. ATS compatibility scoring
   - Extracts technical and job-relevant keywords from the job description
   - Compares those keywords against the resume text
   - Computes a match score and lists matched vs. missing keywords

3. Resume optimization workflow
   - Accepts resume text, job description, role title, and proficiencies
   - Generates optimized accomplishment bullets
   - Uses a heuristic generator by default
   - Optionally uses Anthropic API if `ANTHROPIC_API_KEY` is configured

4. LaTeX resume generation
   - Builds a resume template with ATS metrics and optimized bullet points
   - Escapes unsafe LaTeX characters before rendering

5. PDF compilation
   - Renders the generated LaTeX with Tectonic
   - Returns a downloadable PDF to the browser

6. Frontend user experience
   - File uploader
   - ATS score display
   - Job description input
   - Target role and skill fields
   - LaTeX editor panel
   - PDF export button

7. Health and API endpoints
   - `/health`
   - `/api/upload`
   - `/api/ats-score`
   - `/api/optimize`
   - `/api/compile`

---

## Current Project Status

### Services Completed

The application is in a working MVP stage and includes the main functional flow:

- Upload resume
- Parse text
- Compare against job description
- Score ATS alignment
- Generate optimized bullet points
- Render LaTeX resume content
- Download compiled PDF

### Tasks Pending / Planned Improvements

These are the next logical improvements the project can take on:

1. Better deployment setup
   - Add full Docker Compose orchestration for backend and frontend
   - Add environment configuration examples for production deployment

2. Enhanced testing coverage
   - Add frontend tests for form behavior and optimization flow
   - Add backend validation tests for edge cases and malformed uploads
   - Add CI checks for linting and automated builds

3. Improved optimization quality
   - Fine-tune keyword matching logic for better resume-job alignment
   - Add a stronger resume rewrite engine with user-specific tailoring

4. Production readiness
   - Add authentication and user session handling
   - Add persistent storage for resume histories and generated outputs
   - Add logging, error monitoring, and operational metrics

5. UX refinements
   - Improve validation messages and error states
   - Make the LaTeX editor more advanced with syntax highlighting and preview improvements

---

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
│   └── .venv/   (created locally when you set up Python environment)
├── frontend/
│   ├── src/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── node_modules/  (created after npm install)
├── tests/
│   └── test_e2e_pipeline.py
├── README.md
└── .gitignore
```

---

## Local Setup Instructions (Git Bash)

The following examples use Git Bash for Windows.

### 1. Clone the project

```bash
cd /c/Users/Yatin/Desktop/Projects/ResumeATS
git clone <repository-url>
cd resume-optimizer
```

If the project is already downloaded, just move into the root folder:

```bash
cd /c/Users/Yatin/Desktop/Projects/ResumeATS/resume-optimizer
```

### 2. Set up the backend

Open a Git Bash terminal and run:

```bash
cd /c/Users/Yatin/Desktop/Projects/ResumeATS/resume-optimizer/backend
python -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. Install Tectonic for PDF export

This application requires Tectonic to generate PDFs from LaTeX.

If you are using Windows, install it in one of these ways:

Option A: via winget

```bash
winget install TectonicProject.Tectonic
```

Option B: from the official Tectonic distribution

Visit the official Tectonic download page and install it, then ensure the binary is available in your PATH.

Option C: from Git Bash shell using the official installer script

```bash
curl --proto '=https' --tlsv1.2 -LsSf https://drop-sh.fullyjustified.net | sh
```

Then confirm it is available:

```bash
tectonic --version
```

### 4. Start the backend server

```bash
cd /c/Users/Yatin/Desktop/Projects/ResumeATS/resume-optimizer/backend
source .venv/Scripts/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:

- http://localhost:8000
- Health check: http://localhost:8000/health

---

### 5. Set up the frontend

Open a second Git Bash terminal:

```bash
cd /c/Users/Yatin/Desktop/Projects/ResumeATS/resume-optimizer/frontend
npm install
npm run dev -- --host 0.0.0.0
```

The frontend will run on:

- http://localhost:5173

The Vite server is configured with a proxy to the backend API at `http://127.0.0.1:8000`.

---

## Running the Full Project Together

You need two terminals open:

Terminal 1 (Backend)

```bash
cd /c/Users/Yatin/Desktop/Projects/ResumeATS/resume-optimizer/backend
source .venv/Scripts/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Terminal 2 (Frontend)

```bash
cd /c/Users/Yatin/Desktop/Projects/ResumeATS/resume-optimizer/frontend
npm install
npm run dev -- --host 0.0.0.0
```

Then open:

```text
http://localhost:5173
```

---

## Optional AI Configuration

The backend supports Anthropic-based optimized bullet generation when an API key is present.

Set the environment variable in your terminal before starting the backend:

```bash
export ANTHROPIC_API_KEY="your_api_key_here"
export ANTHROPIC_MODEL="claude-3-5-sonnet-latest"
```

If the key is not set, the app will automatically fall back to the built-in heuristic optimization logic.

---

## Docker Run (Optional)

The backend includes a Dockerfile. You can build and run it from the backend directory:

```bash
cd /c/Users/Yatin/Desktop/Projects/ResumeATS/resume-optimizer/backend
docker build -t resume-optimizer-backend .
docker run -p 8000:8000 resume-optimizer-backend
```

This starts the FastAPI service on port 8000.

---

## Testing

Before running tests, ensure the backend virtual environment is activated and dependencies are installed:

```bash
cd /c/Users/Yatin/Desktop/Projects/ResumeATS/resume-optimizer/backend
source .venv/Scripts/activate
python -m pytest -q
```

The repository includes tests covering:

- LaTeX escaping logic
- ATS score determinism
- PDF compilation via the compile endpoint when Tectonic is available

> Note: the compile test is automatically skipped if Tectonic is not installed on the system.

---

## Common Troubleshooting

### Frontend cannot connect to backend
- Make sure the backend is running on port 8000.
- Confirm the Vite proxy configuration in `frontend/vite.config.js` points to `http://127.0.0.1:8000`.

### PDF generation fails
- Install Tectonic and verify it is in your PATH.
- Run `tectonic --version` to confirm the installation.

### Resume parsing fails
- Confirm the uploaded file type is supported.
- Check that the file is not empty or corrupted.

### Missing Python packages
- Reinstall the backend dependencies:

```bash
pip install -r requirements.txt
```

---

## Summary

This project is a practical resume optimization tool that combines ATS evaluation, content generation, and resume export into a single workflow. It is already functional as a local MVP and is ready for continued enhancement in testing, deployment, and production-grade polish.

If you want, the next step can be to add a Docker Compose setup, CI pipeline, or a more advanced resume generation strategy.
