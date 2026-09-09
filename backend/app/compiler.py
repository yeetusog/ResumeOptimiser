from __future__ import annotations

import logging
import os
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape


logger = logging.getLogger("resume_optimizer.compiler")
APP_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = APP_DIR / "templates"
MAX_LATEX_CHARS = int(os.getenv("MAX_LATEX_INPUT_CHARS", "200000"))


def render_resume_latex(
    bullet_points: list[str],
    target_title: str = "Software Engineer",
    ats_score: float = 0.0,
    matched_keywords: list[str] | None = None,
    missing_keywords: list[str] | None = None,
) -> str:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=select_autoescape(default=False),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("resume.tex.j2")
    return template.render(
        bullet_points=bullet_points,
        target_title=target_title,
        ats_score=round(float(ats_score or 0), 2),
        matched_keywords=", ".join(matched_keywords or []) or "None",
        missing_keywords=", ".join(missing_keywords or []) or "None",
    )


def compile_latex_to_pdf(latex_source: str) -> bytes:
    if not shutil.which("tectonic"):
        raise RuntimeError("Tectonic CLI is not installed or not available on PATH")
    if len(latex_source or "") > MAX_LATEX_CHARS:
        raise RuntimeError("LaTeX source is too large for compilation")

    with tempfile.TemporaryDirectory(prefix="resume_optimizer_") as tmpdir:
        workdir = Path(tmpdir)
        tex_path = workdir / f"resume_{uuid.uuid4().hex}.tex"
        tex_path.write_text(latex_source, encoding="utf-8")

        try:
            result = subprocess.run(
                ["tectonic", str(tex_path)],
                cwd=str(workdir),
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
                shell=False,
            )
        except subprocess.TimeoutExpired as exc:
            logger.warning("LaTeX compilation timed out")
            raise RuntimeError("LaTeX compilation timed out") from exc

        if result.returncode != 0:
            details = (result.stderr or result.stdout or "Unknown LaTeX compilation error").strip()
            details = details.replace(str(workdir), "<tempdir>")
            logger.warning("LaTeX compilation failed", extra={"diagnostic_length": len(details)})
            raise RuntimeError(details[-2000:])

        pdf_path = tex_path.with_suffix(".pdf")
        if not pdf_path.exists():
            raise RuntimeError("Tectonic finished without producing a PDF")
        return pdf_path.read_bytes()
