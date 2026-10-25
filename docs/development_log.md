# ResumeIQ Development Log

## Day 1 - Environment and setup
- Python 3.12.10 installed
- Virtual environment created at C:\Projects\ResumeIQ\.venv
- Installed: python-dotenv
- Created: .gitignore, .env.example, requirements.txt, README.md, app.py
- Next: Day 2 - PDF and DOCX text extraction
## Day 2 - Document processing
- Installed: PyMuPDF 2.0, python-docx 1.2.0, pytest 9.1.1
- Created: services/document_parser.py, tests/test_document_parser.py
- Tests: 10 passed
- Next: Day 3 - Pydantic data models

## Day 3 - Data models
- Installed: pydantic 2.14.1
- Created: backend/schemas.py, tests/test_schemas.py
- Models for all 5 agents plus safe parser for malformed AI output
- Next: Day 4 - first CrewAI agent (LLM provider choice)
