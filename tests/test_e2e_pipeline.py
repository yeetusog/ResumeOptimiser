from __future__ import annotations

import shutil

import pytest
from fastapi.testclient import TestClient

from backend.app.ats import calculate_ats_score, extract_keywords
from backend.app.main import app
from backend.app.sanitizer import escape_latex_chars


client = TestClient(app)


def test_sanitizer_reserved_characters():
    escaped = escape_latex_chars(r"C:\temp\build && rm -rf / && echo 100% success & $50M revenue {x} _ # ~ ^")
    assert r"\textbackslash{}" in escaped
    assert r"\%" in escaped
    assert r"\&" in escaped
    assert r"\$" in escaped
    assert r"\_" in escaped
    assert r"\{" in escaped
    assert r"\}" in escaped
    assert r"\textasciitilde{}" in escaped
    assert r"\textasciicircum{}" in escaped


def test_ats_keyword_extraction_ignores_generic_boilerplate():
    jd = (
        "Senior Java Engineer with Spring Boot, REST API, AWS Lambda, and Machine Learning. "
        "Responsibilities include building scalable systems with Microsoft SQL Server, Python, and Docker. "
        "Opportunity to collaborate with teams and improve the environment."
    )
    keywords = extract_keywords(jd)
    assert "responsibilities" not in keywords
    assert "opportunity" not in keywords
    assert "environment" not in keywords
    assert "spring boot" in keywords
    assert "rest api" in keywords
    assert "aws lambda" in keywords
    assert "machine learning" in keywords
    assert "microsoft sql server" in keywords


def test_ats_calculation_is_deterministic():
    result = calculate_ats_score(
        resume_text="Built production Python APIs with FastAPI for analytics products.",
        jd_text="Python FastAPI Docker",
    )

    assert result["score"] == 66.67
    assert result["matched_keywords"] == ["fastapi", "python"]
    assert result["missing_keywords"] == ["docker"]


@pytest.mark.skipif(shutil.which("tectonic") is None, reason="Tectonic CLI is required for PDF compilation")
def test_compile_endpoint_returns_pdf_headers():
    latex = r"""
\documentclass{article}
\usepackage[margin=1in]{geometry}
\begin{document}
\section*{Optimized Resume}
This validation document confirms the FastAPI compile endpoint returns a binary PDF.
\vspace{18cm}
End of document.
\end{document}
"""
    response = client.post("/api/compile", json={"latex": latex})

    assert response.status_code == 200
    assert "application/pdf" in response.headers["content-type"]
    assert int(response.headers["content-length"]) > 5000
