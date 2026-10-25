"""Run one resume analysis from an upload, reporting progress step by step.

No Streamlit code here, so tests can mock the AI and check the behavior.
"""

from collections.abc import Callable

from backend.schemas import FinalReport
from services.report_service import run_full_analysis
from ui.upload import read_uploaded_resume
from ui.validation import (
    normalize_job_description,
    validate_job_description,
    validate_upload,
)

# Steps shown to the user, in order. The AI analysis is ONE step because
# run_full_analysis() is a single call and gives no per-agent progress.
STEP_KEYS = ("check", "read", "analyze")
STEP_LABELS = {
    "check": "Checking your inputs",
    "read": "Reading the resume text",
    "analyze": "Running the AI analysis (this can take a minute)",
}

StepCallback = Callable[[str, str], None]


class InputError(ValueError):
    """The user's input is not acceptable. The message is safe to show."""


def analyze_upload(
    data: bytes,
    filename: str,
    job_description: str | None = None,
    on_step: StepCallback | None = None,
) -> FinalReport:
    """Validate, read and analyze an uploaded resume.

    `on_step(key, state)` is called with state "active", "done" or "failed".
    Any error is re-raised after the failing step is reported.
    """

    def notify(key: str, state: str) -> None:
        if on_step is not None:
            on_step(key, state)

    current = "check"
    try:
        notify("check", "active")
        problem = validate_upload(filename, len(data)) or validate_job_description(
            job_description
        )
        if problem:
            raise InputError(problem)
        job = normalize_job_description(job_description)
        notify("check", "done")

        current = "read"
        notify("read", "active")
        resume_text = read_uploaded_resume(data, filename)
        notify("read", "done")

        current = "analyze"
        notify("analyze", "active")
        report = run_full_analysis(resume_text, job)
        notify("analyze", "done")
        return report
    except Exception:
        notify(current, "failed")
        raise