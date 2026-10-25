"""Tasks: the job cards handed to each agent."""
import json

from crewai import Agent, Task

from backend.schemas import ParsedResume


def create_parse_task(agent: Agent, resume_text: str) -> Task:
    schema = json.dumps(ParsedResume.model_json_schema())
    description = (
        "Read the resume text below and extract its information.\n\n"
        "STRICT RULES:\n"
        "- Use ONLY information written in the resume. Never invent anything.\n"
        "- If something is missing, use null for single values or an empty list [].\n"
        "- Mark an experience as is_internship true only if the resume says internship or intern.\n"
        "- technical_skills = programming languages, libraries, methods. "
        "business_skills = business or soft skills. tools = software and platforms.\n"
        "- Return ONLY one JSON object that follows this JSON schema. "
        "No explanations, no markdown.\n\n"
        "JSON SCHEMA:\n" + schema + "\n\n"
        "RESUME TEXT:\n" + resume_text
    )
    return Task(
        description=description,
        expected_output="One valid JSON object matching the schema, and nothing else.",
        agent=agent,
    )