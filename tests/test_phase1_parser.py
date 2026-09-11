from __future__ import annotations

from backend.app.parser import parse_editable_content, reconstruct_latex


def test_parse_editable_content_tracks_source_spans_and_reconstructs_original():
    original = r"""\documentclass[10pt,letterpaper]{article}
\usepackage[margin=0.65in]{geometry}
\begin{document}
\begin{center}
    {\LARGE \textbf{Optimized Resume Highlights}}\\
    \vspace{4pt}
    Target Role: Software Engineer
\end{center}

\section*{Selected Impact}
\begin{itemize}
    \item Built scalable Python APIs for high-volume analytics workloads.
    \item Improved system reliability with Docker, CI/CD, and SQL automation.
\end{itemize}

\section*{Alignment Summary}
\begin{itemize}
    \item ATS match score: 87%
    \item Matched keywords: Python, SQL, Docker
\end{itemize}
\end{document}
"""

    nodes = parse_editable_content(original)

    assert nodes
    assert all("source_span" in node and len(node["source_span"]) == 2 for node in nodes)
    assert reconstruct_latex(original, nodes) == original


def test_parse_editable_content_keeps_protected_regions_outside_editable_spans():
    original = r"""\documentclass[10pt,letterpaper]{article}
\usepackage[margin=0.65in]{geometry}
\begin{document}
\section*{Selected Impact}
\begin{itemize}
    \item Built measurable automation improvements.
\end{itemize}
\end{document}
"""

    nodes = parse_editable_content(original)
    protected = []

    for node in nodes:
        start, end = node["source_span"]
        protected.append((start, end))

    assert protected
    assert reconstruct_latex(original, nodes) == original
    assert all(start < end for start, end in protected)


def test_parse_template_supports_current_resume_template_shape():
    from pathlib import Path

    template = Path("backend/app/templates/resume.tex.j2").read_text(encoding="utf-8")
    nodes = parse_editable_content(template)

    assert nodes
    assert any(node["id"].startswith("bullet_") for node in nodes)
    assert reconstruct_latex(template, nodes) == template
