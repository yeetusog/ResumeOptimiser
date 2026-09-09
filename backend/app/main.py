from __future__ import annotations

import json
import logging
import os
import re
from typing import Any

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field

from .ats import calculate_ats_score
from .compiler import compile_latex_to_pdf, render_resume_latex
from .parser import extract_text_from_upload
from .sanitizer import escape_latex_chars


load_dotenv()
logger = logging.getLogger("resume_optimizer.main")
SYSTEM_PROMPT = """You are an elite executive resume writer. Return ONLY a valid JSON object matching this structural contract:
{
  "bullet_points": [
    "Architected scalable microservices using Python FastAPI, reducing latency by 35%",
    "Streamlined CI/CD pipelines cut deployment cycles down to 10 minutes"
  ]
}
Do not include markdown code block syntax, commentary, or LaTeX commands inside the response."""


def _cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


app = FastAPI(title="Resume Optimizer API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ATSRequest(BaseModel):
    resume_text: str = Field(..., min_length=1)
    jd_text: str = Field(..., min_length=1)


class OptimizeRequest(ATSRequest):
    user_proficiencies: list[str] = Field(default_factory=list)
    target_title: str = "Software Engineer"


class CompileRequest(BaseModel):
    latex: str = Field(..., min_length=1, max_length=200000)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/upload")
async def upload_resume(file: UploadFile = File(...)) -> dict[str, str]:
    try:
        text = await extract_text_from_upload(file)
        return {"filename": file.filename or "resume", "text": text}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/ats-score")
def ats_score(payload: ATSRequest) -> dict:
    return calculate_ats_score(payload.resume_text, payload.jd_text)


@app.post("/api/optimize")
async def optimize(payload: OptimizeRequest) -> dict:
    ats = calculate_ats_score(payload.resume_text, payload.jd_text)
    generation_source, raw_bullets = await _generate_bullets(payload, ats)
    sanitized_bullets = [escape_latex_chars(bullet) for bullet in raw_bullets[:8]]
    latex_code = render_resume_latex(
        sanitized_bullets,
        target_title=escape_latex_chars(payload.target_title),
        ats_score=ats["score"],
        matched_keywords=[escape_latex_chars(value) for value in ats["matched_keywords"][:20]],
        missing_keywords=[escape_latex_chars(value) for value in ats["missing_keywords"][:20]],
    )
    return {
        "bullet_points": raw_bullets[:8],
        "ats": ats,
        "latex_code": latex_code,
        "generation_source": generation_source,
    }


@app.post("/api/compile")
def compile_resume(payload: CompileRequest) -> Response:
    try:
        pdf = compile_latex_to_pdf(payload.latex)
    except RuntimeError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="Optimized_Resume.pdf"'},
    )


async def _generate_bullets(payload: OptimizeRequest, ats: dict[str, Any]) -> tuple[str, list[str]]:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        try:
            return "anthropic", await _generate_with_anthropic(payload, ats, api_key)
        except httpx.HTTPError as exc:
            logger.warning("Anthropic generation failed; using heuristic fallback", extra={"kind": "anthropic_http_error", "detail": str(type(exc).__name__)})
        except ValueError as exc:
            logger.warning("Anthropic response schema was invalid; using heuristic fallback", extra={"kind": "anthropic_schema_error", "detail": str(exc)})
        except Exception as exc:
            logger.exception("Unexpected Anthropic generation failure; using heuristic fallback")
    else:
        logger.info("No ANTHROPIC_API_KEY configured; using heuristic bullet generation")
    return "heuristic", _generate_heuristic_bullets(payload, ats)


async def _generate_with_anthropic(payload: OptimizeRequest, ats: dict[str, Any], api_key: str) -> list[str]:
    user_prompt = {
        "resume_text": payload.resume_text[:12000],
        "job_description": payload.jd_text[:12000],
        "user_proficiencies": payload.user_proficiencies,
        "matched_keywords": ats["matched_keywords"],
        "missing_keywords": ats["missing_keywords"],
    }
    model_name = os.getenv("ANTHROPIC_MODEL", "claude-3-7-sonnet-latest")
    async with httpx.AsyncClient(timeout=40) as client:
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": model_name,
                "max_tokens": 800,
                "temperature": 0.2,
                "system": SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": json.dumps(user_prompt)}],
            },
        )
        response.raise_for_status()
    content = response.json()["content"][0]["text"]
    parsed = json.loads(content)
    bullets = parsed.get("bullet_points")
    if not isinstance(bullets, list) or not all(isinstance(item, str) for item in bullets):
        raise ValueError("LLM response did not match the required schema")
    return [_strip_latex(item) for item in bullets if item.strip()]


def _generate_heuristic_bullets(payload: OptimizeRequest, ats: dict[str, Any]) -> list[str]:
    keywords = (ats.get("matched_keywords") or [])[:6] + (ats.get("missing_keywords") or [])[:4]
    proficiencies = [item for item in payload.user_proficiencies if item.strip()]
    focus_terms = keywords or proficiencies or ["stakeholder outcomes", "delivery quality", "operational efficiency"]
    source_sentences = [
        sentence.strip()
        for sentence in re.split(r"[\n.!?]+", payload.resume_text)
        if len(sentence.strip()) > 30
    ][:4]

    bullets = []
    for index, term in enumerate(focus_terms[:6]):
        source = source_sentences[index % len(source_sentences)] if source_sentences else "Delivered measurable improvements across complex initiatives"
        bullets.append(
            f"Advanced {payload.target_title} outcomes by applying {term} expertise to {source[:110].rstrip()}"
        )
    return bullets or ["Delivered measurable business impact through focused execution and cross-functional collaboration"]


def _strip_latex(text: str) -> str:
    return re.sub(r"[{}\\]", "", text).strip()
