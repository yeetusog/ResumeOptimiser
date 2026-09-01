# CLAUDE.md

## Project context

This repository contains a full-stack resume optimization tool. The application helps a user upload a resume, compare it against a target job description, identify missing keywords, generate stronger achievement statements, and export a final PDF resume.

## Architecture summary

### Backend
- FastAPI application in `backend/app/main.py`
- ATS scoring logic in `backend/app/ats.py`
- Resume parsing in `backend/app/parser.py`
- LaTeX rendering in `backend/app/compiler.py`
- LaTeX sanitization in `backend/app/sanitizer.py`
- Resume template in `backend/app/templates/resume.tex.j2`

### Frontend
- React + Vite app in `frontend/src`
- Main flow is managed in `frontend/src/App.jsx`
- UI components are separated into reusable files under `frontend/src/components`

### Current functional flow
1. User uploads a resume in PDF, DOCX, TXT, or TEX format.
2. Backend extracts the text and sends it back to the frontend.
3. User enters or pastes a job description and optional role details.
4. Backend calculates ATS alignment and missing keywords.
5. The app can generate optimized bullet points via:
   - Anthropic API if `ANTHROPIC_API_KEY` is set
   - heuristic fallback otherwise
6. Generated content is rendered into a LaTeX resume template.
7. The final LaTeX document is compiled into a PDF for download.

## Current status

### Completed
- Resume upload support
- Text extraction for common document formats
- ATS scoring and keyword comparison
- Resume optimization workflow
- LaTeX rendering and sanitization
- PDF export support through Tectonic
- Vite frontend and basic UI flow

### Pending improvements
- Better resume-to-job matching accuracy
- More robust parsing for edge-case resume layouts
- Expanded test coverage across frontend and backend flows
- Improved deployment config and environment management
- Persistence for saved resumes or generated outputs
- Monitoring, logging, and user-facing error handling
- CI/CD pipeline for automated validation

## Recommended next improvements

### 1. Quality improvements
- Refine keyword extraction and matching for better ATS scoring accuracy.
- Add stricter normalization for phrasing variations, synonyms, and role-specific terminology.
- Improve generated bullet quality by combining resume context with stronger accomplishment framing.

### 2. Reliability improvements
- Add validation for malformed uploads and empty document contents.
- Add more API-level tests for each endpoint.
- Handle Tectonic availability errors more gracefully in the UI.

### 3. Product improvements
- Add user accounts or saved resume history.
- Add export options beyond PDF.
- Provide side-by-side comparison between original and optimized resume text.
- Improve editor usability with better formatting, preview, and validation.

### 4. DevOps improvements
- Add Docker Compose for local stack startup.
- Include environment variable templates such as `.env.example`.
- Add CI checks for linting, tests, and build validation.

## Local development notes

- Backend dependencies are listed in `backend/requirements.txt`.
- Frontend dependencies are managed through `frontend/package.json`.
- Tectonic must be installed for PDF generation.
- The API is expected to run on port 8000.
- The frontend is expected to run on port 5173.

## Important implementation notes

- The project is a working MVP, not yet a production-ready SaaS product.
- The backend already includes a useful fallback path when no AI key is available.
- The README should stay user-facing and concise; project-specific details and future work should remain in this file.
- Avoid committing user-specific local paths, usernames, or machine-specific environment details into the public repository.

## Suggested future tasks

- Add `.env.example` file for backend configuration.
- Add a deployment section for Docker Compose or cloud hosting.
- Add testing for malformed job descriptions and edge-case PDF content.
- Create a pre-commit or CI workflow for validation.
- Add lightweight UX polish for error banners, loading indicators, and empty states.

## Maintainership guidance

When updating this project:
- keep public-facing documentation generic and professional
- keep internal planning, roadmap notes, and technical debt in `CLAUDE.md`
- prefer small, incremental improvements backed by tests
- keep the README focused on setup and usage rather than implementation history
