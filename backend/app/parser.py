from __future__ import annotations

import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from docx import Document
from fastapi import UploadFile
from pypdf import PdfReader


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
