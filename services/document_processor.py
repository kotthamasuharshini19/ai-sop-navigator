import os
import re
from pathlib import Path

from pypdf import PdfReader
from docx import Document


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


# -------------------------------------------------
# TEXT EXTRACTION
# -------------------------------------------------

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file."""

    reader = PdfReader(file_path)

    pages = []

    for page in reader.pages:
        text = page.extract_text() or ""

        if text.strip():
            pages.append(text.strip())

    return "\n".join(pages).strip()


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from a DOCX file."""

    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:

        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    return "\n".join(paragraphs).strip()


def extract_text_from_txt(file_path: str) -> str:
    """Extract text from a TXT file."""

    return Path(file_path).read_text(
        encoding="utf-8",
        errors="ignore"
    ).strip()


def extract_text(file_path: str) -> str:
    """Extract text from supported SOP formats."""

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    extension = path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {extension}. "
            f"Supported formats: PDF, DOCX, TXT."
        )

    if extension == ".pdf":
        return extract_text_from_pdf(file_path)

    if extension == ".docx":
        return extract_text_from_docx(file_path)

    if extension == ".txt":
        return extract_text_from_txt(file_path)

    return ""


# -------------------------------------------------
# SOP SECTION DETECTION
# -------------------------------------------------

def split_into_sop_sections(text: str):
    """
    Split SOP into logical numbered sections.

    Example:

    1. COMPANY LAPTOP LOSS OR THEFT
    2. PASSWORD AND ACCOUNT SECURITY
    3. REMOTE WORK AND COMPANY DEVICES
    """

    if not text.strip():
        return []

    # Normalize line breaks
    text = re.sub(r"\r\n?", "\n", text)

    # Detect numbered headings such as:
    # 1. TITLE
    # 2. TITLE
    # 10. TITLE
    pattern = r"(?m)(?=^\s*\d+\.\s+[A-Z][^\n]*)"

    sections = re.split(
        pattern,
        text
    )

    cleaned_sections = []

    for section in sections:

        section = section.strip()

        if not section:
            continue

        # Ignore very small fragments
        if len(section) < 40:
            continue

        cleaned_sections.append(section)

    return cleaned_sections


# -------------------------------------------------
# FALLBACK CHUNKING
# -------------------------------------------------

def chunk_text(
    text: str,
    chunk_size: int = 1200,
    overlap: int = 200
):
    """
    Split text into logical SOP sections first.

    If numbered sections are detected, each section
    becomes a chunk.

    Otherwise, use normal overlapping chunks.
    """

    if not text.strip():
        return []

    # First try logical SOP sections
    sections = split_into_sop_sections(text)

    if len(sections) >= 2:
        return sections

    # ---------------------------------------------
    # Fallback for documents without headings
    # ---------------------------------------------

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = end - overlap

    return chunks


# -------------------------------------------------
# PROCESS SOP
# -------------------------------------------------

def process_sop(file_path: str):
    """
    Complete SOP processing pipeline.

    Returns:
        {
            "file_name": ...,
            "text": ...,
            "chunks": ...,
            "chunk_count": ...
        }
    """

    text = extract_text(file_path)

    if not text:
        raise ValueError(
            "No readable text was found in the SOP."
        )

    chunks = chunk_text(text)

    return {
        "file_name": os.path.basename(file_path),
        "text": text,
        "chunks": chunks,
        "chunk_count": len(chunks)
    }