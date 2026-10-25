"""Safely turn an uploaded resume into text using a temporary file.

The uploaded bytes are written to a temporary folder, read by the existing
document parser, and the folder is deleted immediately afterwards (also when
reading fails). Nothing is stored in the project folder.
"""

import tempfile
from pathlib import Path

from services.document_parser import DocumentError, extract_text
from ui.validation import validate_upload


def read_uploaded_resume(data: bytes, filename: str) -> str:
    """Return the text of an uploaded PDF or DOCX file.

    Raises DocumentError for any problem the user can fix (wrong type, too
    large, empty, unreadable, or no extractable text).
    """
    problem = validate_upload(filename, len(data))
    if problem:
        raise DocumentError(problem)

    suffix = Path(filename).suffix.lower()
    # The folder and everything inside it is deleted when the block ends.
    with tempfile.TemporaryDirectory(prefix="resumeiq_") as folder:
        temp_path = Path(folder) / f"resume{suffix}"
        temp_path.write_bytes(data)
        return extract_text(str(temp_path))