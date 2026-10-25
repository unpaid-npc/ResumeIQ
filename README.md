# ResumeIQ

AI-powered resume review agent built with CrewAI.

> Work in progress. The full documentation (architecture diagram, screenshots, limitations) will be added at the end of the project.

## What works today

- Upload a resume (PDF or DOCX, max 5 MB) in a dark-themed Streamlit app.
- Optionally paste a job description. The app works with or without one.
- A sequence of AI agents (Parser, Skills Analyst, Evaluator, Job Matcher, Feedback Writer) analyzes the resume. Each agent's output is validated before the next agent runs.
- The app shows an executive summary, strengths, weaknesses, recommendations and next steps.
- Uploaded resumes are read from a temporary file that is deleted straight away. They are never saved in the project folder.

## Coming next

Score charts, a skills view, a job-match view, before/after bullet rewrites and downloadable reports.

## Setup (Windows, VS Code, PowerShell)

```powershell
cd C:\Projects\ResumeIQ
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your own LLM settings. Never commit `.env`.

## Run the app

```powershell
streamlit run app.py
```

## Run the tests

```powershell
python -m pytest -q
```

## Privacy note

Free-tier Gemini may use inputs to improve its models. Use only synthetic resumes or your own resume.