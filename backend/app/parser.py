from __future__ import annotations

import os
import re
from pathlib import Path
from tempfile import NamedTemporaryFile

from docx import Document
from fastapi import UploadFile
from pypdf import PdfReader


def parse_editable_content(source: str) -> list[dict]:
    r"""Return non-overlapping editable text nodes with exact source spans.

    The parser is intentionally conservative: it captures only text that is meant to be user-editable
    while leaving structural LaTeX commands, environments, and Jinja placeholders intact.
    """
    if not source:
        return []

    text = str(source)
    nodes: list[dict] = []
    bullet_index = 0

    def add_node(node_id: str, section: str, content: str, start: int, end: int) -> None:
        cleaned = content.strip()
        if not cleaned or start < 0 or end < start or end > len(text):
            return
        nodes.append(
            {
                "id": node_id,
                "section": section,
                "text": cleaned,
                "source_span": [start, end],
                "protected": False,
            }
        )

    for match in re.finditer(r"\\item\s*(.*?)(?=\\item|\\end\{itemize\}|\\end\{enumerate\}|\\section\*?|\\end\{document\}|$)", text, flags=re.DOTALL):
        bullet_index += 1
        literal = match.group(1)
        start, end = match.span(1)
        if not literal.strip():
            continue
        add_node(f"bullet_{bullet_index}", "experience", text[start:end], start, end)

    for match in re.finditer(r"Target\s+Role:\s*(\{\{[^}]+\}\}|[^\n\\]+)", text):
        start, end = match.span(1)
        content = text[start:end]
        if "{{" in content or "}}" in content:
            continue
        add_node("target_role", "header", content, start, end)

    return sorted(nodes, key=lambda node: node["source_span"][0])


def reconstruct_latex(original: str, nodes: list[dict]) -> str:
    """Return the original LaTeX unchanged when the nodes match the source exactly."""
    if not original:
        return ""
    if not nodes:
        return original

    normalized = sorted(nodes, key=lambda node: node["source_span"][0])
    last_index = 0
    reconstructed: list[str] = []

    for node in normalized:
        start, end = node["source_span"]
        if start < 0 or end < start or end > len(original):
            raise ValueError(f"Node source span is invalid: {node}")
        if start < last_index:
            raise ValueError(f"Node source spans overlap: {node}")
        reconstructed.append(original[last_index:start])
        reconstructed.append(original[start:end])
        last_index = end

    reconstructed.append(original[last_index:])
    return "".join(reconstructed)


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".tex", ".txt"}
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", "10485760"))


async def extract_text_from_upload(file: UploadFile) -> str:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {suffix or 'unknown'}")

    content = await file.read()
    if not content:
        raise ValueError("Uploaded file is empty")
    if len(content) > MAX_UPLOAD_BYTES:
        raise ValueError(f"Uploaded file exceeds the {MAX_UPLOAD_BYTES} byte limit")

    with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        return extract_text(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _extract_pdf(path)
    if suffix == ".docx":
        return _extract_docx(path)
    if suffix in {".tex", ".txt"}:
        return path.read_text(encoding="utf-8", errors="ignore")
    raise ValueError(f"Unsupported file type: {suffix or 'unknown'}")


def _extract_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    if not reader.pages:
        raise ValueError("The uploaded PDF is empty or unreadable.")

    pages = []
    for page in reader.pages:
        extracted = page.extract_text() or ""
        pages.append(extracted.strip())

    text = "\n".join(page for page in pages if page)
    if not text.strip() or len(text.strip()) < 30:
        raise ValueError("The uploaded PDF appears empty or image-only. Please upload a text-based PDF or another supported file.")
    return text


def _extract_docx(path: Path) -> str:
    document = Document(str(path))
    paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]
    table_cells = []
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.text.strip():
                    table_cells.append(cell.text.strip())
    return "\n".join(paragraphs + table_cells)
