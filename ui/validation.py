"""Input validation and friendly error messages for the ResumeIQ UI.

This module has no Streamlit code, so it can be tested on its own.
"""

from pathlib import Path

from services.analysis_service import AnalysisError
from services.document_parser import DocumentError
from services.llm_config import ConfigError

ALLOWED_EXTENSIONS = (".pdf", ".docx")
MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB, same limit as the document parser
MIN_JOB_DESCRIPTION_CHARS = 40
MAX_JOB_DESCRIPTION_CHARS = 10_000


def validate_upload(filename: str | None, size_bytes: int) -> str | None:
    """Check an uploaded file. Return an error message, or None if it is fine."""
    if not filename:
        return "Please upload your resume as a PDF or DOCX file."
    extension = Path(filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        return "Unsupported file type. Please upload a PDF or DOCX file."
    if size_bytes <= 0:
        return "The uploaded file is empty."
    if size_bytes > MAX_UPLOAD_BYTES:
        limit_mb = MAX_UPLOAD_BYTES // (1024 * 1024)
        return f"The file is too large. The maximum size is {limit_mb} MB."
    return None


def normalize_job_description(text: str | None) -> str | None:
    """Trim the job description. Return None when it is empty (it is optional)."""
    if text is None:
        return None
    cleaned = text.strip()
    return cleaned or None


def validate_job_description(text: str | None) -> str | None:
    """Check the optional job description. Return an error message or None."""
    cleaned = normalize_job_description(text)
    if cleaned is None:
        return None  # no job description is allowed
    if len(cleaned) < MIN_JOB_DESCRIPTION_CHARS:
        return (
            "The job description is too short to be useful. "
            "Paste the full text, or leave the box empty."
        )
    if len(cleaned) > MAX_JOB_DESCRIPTION_CHARS:
        return (
            f"The job description is too long (maximum "
            f"{MAX_JOB_DESCRIPTION_CHARS:,} characters). Please shorten it."
        )
    return None


def describe_error(exc: Exception) -> tuple[str, str]:
    """Turn an exception into a (title, detail) pair that is safe to show.

    Known ResumeIQ errors show their own message. Unknown errors show only the
    error type, never the raw text, in case it contains sensitive details.
    """
    if isinstance(exc, DocumentError):
        return "Could not read the resume", str(exc)
    if isinstance(exc, ConfigError):
        return (
            "AI model is not configured",
            "Check the LLM settings in your .env file, then restart the app.",
        )
    if isinstance(exc, AnalysisError):
        return "The analysis could not be completed", str(exc)
    return (
        "Something went wrong",
        f"Unexpected error ({type(exc).__name__}). This can happen when the "
        "free-tier request limit is reached. Wait a minute and try again.",
    )