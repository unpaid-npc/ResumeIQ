# ResumeIQ Architecture

## Layers

- **UI (`ui/`, `app.py`)**: Streamlit pages, dark theme CSS, escaped HTML components, Plotly charts, input validation, a temporary-file upload reader and the runner that reports progress.
- **Services (`services/`)**: document parsing (PDF and DOCX, 5 MB limit), LLM configuration, the analysis stages and the report builder.
- **Agents and tasks (`agents/`, `tasks/`)**: CrewAI definitions for the five agents and their tasks.
- **Schemas (`backend/schemas.py`)**: Pydantic models for every stage and the final report.

## Request flow

1. The UI validates the file type, size and the optional job description.
2. The upload is written to a temporary folder as resume.pdf or resume.docx, read by the document parser, and the folder is deleted.
3. run_full_analysis(resume_text, job_description) runs the stages in order: Parser, Skills Analyst, Evaluator, Job Matcher (only with a job description) and Feedback Writer.
4. Each stage output is validated by Pydantic. A stage retries once on malformed output.
5. Skills, scores and job match are copied into the report by code. The Feedback Writer produces words only.
6. Bullet rewrites pass a faithfulness filter: the original line must appear in the resume and the improved line may not add numbers the resume lacks.
7. The FinalReport is stored in the Streamlit session and drawn by the view modules. JSON and Markdown downloads are built from it.

## Design decisions

- Validation, upload reading, the runner, charts and export contain no or little Streamlit code, so they can be tested directly.
- All text placed into HTML is escaped.
- The LLM is mocked in tests, so the suite uses no API requests.
- Protected characteristics are not used in scoring.

## Known limits

See the limitations section of the README.