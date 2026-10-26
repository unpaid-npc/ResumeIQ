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

## Day 7 - Feedback agent and full workflow
- Created: agents/feedback_generator.py, tasks/feedback_task.py, services/report_service.py, run_full_demo.py, tests/test_report_service.py
- Updated: backend/schemas.py (FeedbackDraft), tasks/resume_tasks.py (soft skills to communication, tools from bullets)
- Design: Feedback agent writes words only; skills, scores and job match are copied by our code. Bullet rewrites are filtered: originals must exist in the resume and improved lines may not contain numbers absent from the resume
- Tests: 53 passed (LLM mocked). Live runs with and without a job description both succeeded
- Known limits: faithfulness filter checks numbers only, not invented non-numeric claims (prompt rule added); scores vary slightly between runs
- Next: Day 8 - dark-themed Streamlit UI

## Day 8 - Dark-themed Streamlit UI

- Installed and pinned streamlit==1.66.1; `pip check` reported no broken requirements.
- Added `.streamlit/config.toml` (dark base theme, 5 MB upload limit, usage stats off, minimal toolbar).
- Added `ui/` package: `styles.py` (palette and CSS), `components.py` (escaped HTML building blocks), `validation.py`, `upload.py` (temporary-file reader), `runner.py` (validation, reading and analysis with step callbacks), `pages.py` (Dashboard and Analyze Resume).
- `app.py` is now the real entry point (`streamlit run app.py`).
- Added `tests/test_app_validation.py` (20 tests, LLM mocked). Full suite: 73 passed.
- Manual check in the browser: dashboard and analyze pages render in the dark theme, and one full analysis with a synthetic resume and NO job description completed and showed results.
- Not yet tested in the UI: a run WITH a job description, and a PDF upload.
- Known limit: the AI analysis is one call, so progress shows 3 honest steps, not per-agent ticks.
- Next: Day 9 (charts, skills and job-match visuals, bullet rewrites, downloads).

### Day 8 addendum - theme and polish
- Dashboard: agent team cards, session-only "latest analysis" panel (real counts only), guardrails list; stats shown as a 2x2 grid.
- Restyled to a neutral dark-gray, Google AI Studio-like look (Material dark accents). Font: DM Sans via Google Fonts (Google Sans is proprietary), with a system fallback.
- Fixed button styling with more specific selectors (Streamlit was overriding them).
- Installed and pinned plotly==7.1.0 for Day 9 (not used yet).
- Still untested in the UI: a run WITH a job description, and a PDF upload.

## Day 9 - Analytics and export
- Added score cards with radar and bar charts (Plotly, dark-styled), skills summary with category chart and evidence, job-match summary with donut chart and requirement details, before/after bullet rewrites, detailed findings.
- Added JSON and Markdown downloads (ui/export.py). Tests: 103 passed.
- Verified in the UI: a run without a job description, a run with a job description (7 requirements, 4 supported, 2 partial, 1 no evidence).
- Not yet tested in the UI: PDF upload.
- Known limits: rewrite filter checks invented numbers only; rewrites may contain "[add real number if you have one]" placeholders; scores vary between runs; results are not saved after the page closes.

## Day 10 - Final documentation
- Fixed stale Dashboard text. Verified a PDF upload end to end (no job description) and downloaded the Markdown and JSON reports.
- Wrote the full README (agentic design, CrewAI, Mermaid diagram, setup, privacy, limitations), docs/architecture.md and two screenshots.
- Final check: 103 tests passed, pip check clean.
- Not tested: a scanned-image PDF (unsupported), a PDF run with a job description.
