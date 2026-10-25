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

## Day 5 - Skills Analysis and Resume Evaluation agents
- Created: agents/skills_analyst.py, agents/resume_evaluator.py, run_analysis_demo.py
- Updated: tasks/resume_tasks.py, services/analysis_service.py (3-stage pipeline with one retry on malformed output), tests/test_analysis_service.py
- Tests: 34 passed (LLM mocked). Live demo verified: demonstrated vs mentioned_only correct, scores plausible, no invented data
- Known issues to tune on Day 7: Teamwork categorized as leadership; Excel not extracted into tools
- Next: Day 6 - Job description matching

## Day 6 - Job description matching
- Created: agents/job_matcher.py, tasks/job_match_task.py, tests/test_job_matching.py, run_match_demo.py
- Updated: services/analysis_service.py (optional matcher stage; skipped when no job description)
- Tests: 42 passed (LLM mocked). Live demo: statuses plausible; fixed years-of-experience overstatement with a prompt rule
- Known issues to tune on Day 7: Teamwork categorized as leadership; Excel not extracted into tools
- Next: Day 7 - Feedback agent and full workflow
