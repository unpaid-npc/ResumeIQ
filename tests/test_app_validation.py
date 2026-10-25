"""Tests for the UI input validation, upload reading and runner. The AI is mocked."""

import io
from pathlib import Path
from unittest.mock import patch

import pytest

from services.analysis_service import AnalysisError
from services.document_parser import DocumentError
from services.llm_config import ConfigError
from ui.runner import InputError, analyze_upload
from ui.upload import read_uploaded_resume
from ui.validation import (
    MAX_UPLOAD_BYTES,
    describe_error,
    normalize_job_description,
    validate_job_description,
    validate_upload,
)

VALID_JD = "We need a Python developer with experience in APIs and testing."


def _docx_bytes(text: str) -> bytes:
    from docx import Document

    doc = Document()
    doc.add_paragraph(text)
    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


# ---------- validate_upload ----------
def test_upload_accepts_pdf_and_docx_any_case():
    assert validate_upload("cv.pdf", 100) is None
    assert validate_upload("CV.DOCX", 100) is None


def test_upload_rejects_missing_name():
    assert "upload" in validate_upload(None, 100).lower()


def test_upload_rejects_wrong_type():
    assert "Unsupported" in validate_upload("cv.txt", 100)


def test_upload_rejects_empty_file():
    assert "empty" in validate_upload("cv.pdf", 0)


def test_upload_rejects_too_large_file():
    assert "too large" in validate_upload("cv.pdf", MAX_UPLOAD_BYTES + 1)


def test_upload_accepts_exact_limit():
    assert validate_upload("cv.pdf", MAX_UPLOAD_BYTES) is None


# ---------- job description ----------
def test_job_description_is_optional():
    assert validate_job_description(None) is None
    assert validate_job_description("   ") is None
    assert normalize_job_description("   ") is None


def test_job_description_is_trimmed():
    assert normalize_job_description("  hello  ") == "hello"


def test_job_description_length_limits():
    assert validate_job_description("x" * 40) is None
    assert "too short" in validate_job_description("x" * 39)
    assert "too long" in validate_job_description("x" * 10_001)


# ---------- describe_error ----------
def test_known_errors_have_friendly_messages():
    assert describe_error(DocumentError("bad file")) == (
        "Could not read the resume",
        "bad file",
    )
    assert "not configured" in describe_error(ConfigError("x"))[0]
    assert describe_error(AnalysisError("failed twice"))[1] == "failed twice"


def test_unknown_error_does_not_leak_its_text():
    title, detail = describe_error(RuntimeError("secret-key-123"))
    assert title == "Something went wrong"
    assert "secret-key-123" not in detail
    assert "RuntimeError" in detail


# ---------- upload reading and temp files ----------
def test_read_uploaded_docx_returns_text():
    text = read_uploaded_resume(_docx_bytes("Jane Test - Python developer."), "cv.docx")
    assert "Jane Test" in text


def test_read_uploaded_rejects_bad_type_before_reading():
    with pytest.raises(DocumentError):
        read_uploaded_resume(b"data", "cv.txt")


def test_temp_folder_is_deleted_after_success():
    seen = {}

    def fake_extract(path):
        seen["path"] = path
        assert Path(path).exists()
        return "resume text"

    with patch("ui.upload.extract_text", side_effect=fake_extract):
        read_uploaded_resume(b"data", "../my private name.pdf")

    assert Path(seen["path"]).name == "resume.pdf"  # never the user's file name
    assert not Path(seen["path"]).exists()


def test_temp_folder_is_deleted_after_failure():
    seen = {}

    def fake_extract(path):
        seen["path"] = path
        raise DocumentError("unreadable")

    with patch("ui.upload.extract_text", side_effect=fake_extract):
        with pytest.raises(DocumentError):
            read_uploaded_resume(b"data", "cv.pdf")

    assert not Path(seen["path"]).exists()


# ---------- runner ----------
def test_runner_without_job_description():
    sentinel = object()
    steps = []
    with patch("ui.runner.read_uploaded_resume", return_value="resume text"), patch(
        "ui.runner.run_full_analysis", return_value=sentinel
    ) as mock_run:
        result = analyze_upload(b"data", "cv.pdf", "   ", lambda k, s: steps.append((k, s)))

    assert result is sentinel
    mock_run.assert_called_once_with("resume text", None)
    assert steps == [
        ("check", "active"),
        ("check", "done"),
        ("read", "active"),
        ("read", "done"),
        ("analyze", "active"),
        ("analyze", "done"),
    ]


def test_runner_passes_trimmed_job_description():
    with patch("ui.runner.read_uploaded_resume", return_value="resume text"), patch(
        "ui.runner.run_full_analysis", return_value=object()
    ) as mock_run:
        analyze_upload(b"data", "cv.pdf", f"  {VALID_JD}  ")

    mock_run.assert_called_once_with("resume text", VALID_JD)


def test_runner_rejects_bad_input_without_calling_ai():
    steps = []
    with patch("ui.runner.run_full_analysis") as mock_run:
        with pytest.raises(InputError):
            analyze_upload(b"data", "cv.txt", None, lambda k, s: steps.append((k, s)))
        with pytest.raises(InputError):
            analyze_upload(b"data", "cv.pdf", "too short")

    mock_run.assert_not_called()
    assert steps[-1] == ("check", "failed")


def test_runner_marks_analysis_step_failed_and_reraises():
    steps = []
    with patch("ui.runner.read_uploaded_resume", return_value="resume text"), patch(
        "ui.runner.run_full_analysis", side_effect=AnalysisError("model failed")
    ):
        with pytest.raises(AnalysisError):
            analyze_upload(b"data", "cv.pdf", None, lambda k, s: steps.append((k, s)))

    assert steps[-1] == ("analyze", "failed")


def test_runner_marks_read_step_failed():
    steps = []
    with patch("ui.runner.read_uploaded_resume", side_effect=DocumentError("no text")):
        with pytest.raises(DocumentError):
            analyze_upload(b"data", "cv.pdf", None, lambda k, s: steps.append((k, s)))

    assert steps[-1] == ("read", "failed")