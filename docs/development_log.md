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

## Day 4 (part 1) - CrewAI and LLM connection
- Installed: crewai 1.15.30 (with google-genai extra)
- Provider: Gemini free tier, model gemini-3.5-flash-lite (set in .env)
- Created: services/llm_config.py, check_llm.py
- Tests: 23 passed. Connection test: OK

## Day 4 (part 2) - Resume Parser Agent
- Created: agents/resume_parser.py, tasks/resume_tasks.py, services/analysis_service.py, run_parser_demo.py
- Tests: 27 passed (LLM mocked). Live demo: parser output verified, phone correctly null
- Disabled CrewAI tracing/telemetry (privacy). Ignored .crewai/
- Next: Day 5 - Skills Analysis and Resume Evaluation agents
