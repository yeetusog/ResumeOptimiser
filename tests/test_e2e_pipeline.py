from __future__ import annotations

import shutil

import pytest
from fastapi.testclient import TestClient

from backend.app.ats import calculate_ats_score
from backend.app.main import app
from backend.app.sanitizer import escape_latex_chars


client = TestClient(app)


def test_sanitizer_reserved_characters():
    assert escape_latex_chars("100% success & $50M revenue") == r"100\% success \& \$50M revenue"


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
