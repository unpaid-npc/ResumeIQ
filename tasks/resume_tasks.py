"""Tasks: the job cards handed to each agent."""
import json

from crewai import Agent, Task
from pydantic import BaseModel

from backend.schemas import ParsedResume, ResumeEvaluation, SkillsAnalysis

JSON_ONLY = (
    "Return ONLY one JSON object that follows the JSON schema below. "
    "No explanations, no markdown.\n\n"
)


def _schema(model: type[BaseModel]) -> str:
    return json.dumps(model.model_json_schema())


def create_parse_task(agent: Agent, resume_text: str) -> Task:
    description = (
        "Read the resume text below and extract its information.\n\n"
        "STRICT RULES:\n"
        "- Use ONLY information written in the resume. Never invent anything.\n"
        "- If something is missing, use null for single values or an empty list [].\n"
        "- Mark an experience as is_internship true only if the resume says internship or intern.\n"
        "- technical_skills = programming languages, libraries, methods. "
        "business_skills = business or soft skills. tools = software and platforms.\n"
        "- tools must include EVERY software or platform named anywhere in the resume, including inside job or project bullets (for example Excel), not only in the skills list.\n"
        + JSON_ONLY
        + "JSON SCHEMA:\n" + _schema(ParsedResume) + "\n\n"
        "RESUME TEXT:\n" + resume_text
    )
    return Task(
        description=description,
        expected_output="One valid JSON object matching the schema, and nothing else.",
        agent=agent,
    )


def create_skills_task(agent: Agent, parsed: ParsedResume, resume_text: str) -> Task:
    description = (
        "Analyze the skills of this candidate.\n\n"
        "STRICT RULES:\n"
        "- List only skills that appear in the parsed data or the resume text. "
        "Never add a skill the resume does not mention.\n"
        "- category must be one of: technical, data_analytics, business_analytics, "
        "communication, leadership, domain_specific.\n"
        "- Put soft skills like communication, teamwork and collaboration in the communication category. Use leadership only when the resume shows leading, managing or mentoring people or projects.\n"
        "- status = demonstrated ONLY if a project, job or internship in the resume "
        "shows the skill being used. Otherwise status = mentioned_only.\n"
        "- For a demonstrated skill, evidence = a short pointer to where it is shown "
        "(project name or job title, plus what was done). "
        "For a mentioned_only skill, evidence = an empty string.\n"
        "- Each skill appears only once.\n"
        + JSON_ONLY
        + "JSON SCHEMA:\n" + _schema(SkillsAnalysis) + "\n\n"
        "PARSED RESUME DATA:\n" + parsed.model_dump_json() + "\n\n"
        "ORIGINAL RESUME TEXT:\n" + resume_text
    )
    return Task(
        description=description,
        expected_output="One valid JSON object matching the schema, and nothing else.",
        agent=agent,
    )


def create_evaluation_task(
    agent: Agent, parsed: ParsedResume, skills: SkillsAnalysis, resume_text: str
) -> Task:
    description = (
        "Evaluate the quality of this resume.\n\n"
        "STRICT RULES:\n"
        "- Give each score as a whole number from 0 to 10 (10 = excellent, 5 = average, "
        "0 = very poor). Be honest. Do not inflate scores.\n"
        "- quantification: score low when achievements rarely include real numbers.\n"
        "- Give 2 to 5 strengths and 3 to 6 improvements. Each finding needs: area, "
        "observation, evidence (a short phrase copied from the resume), and for "
        "improvements a suggestion.\n"
        "- NEVER invent numbers, achievements or experience in a suggestion. If a number "
        "would help, say 'add the real number if you have one'.\n"
        "- Judge only the writing and content. Do NOT use name, gender, age, nationality, "
        "religion, marital status or location in any score or comment.\n"
        + JSON_ONLY
        + "JSON SCHEMA:\n" + _schema(ResumeEvaluation) + "\n\n"
        "PARSED RESUME DATA:\n" + parsed.model_dump_json() + "\n\n"
        "SKILLS ANALYSIS:\n" + skills.model_dump_json() + "\n\n"
        "ORIGINAL RESUME TEXT:\n" + resume_text
    )
    return Task(
        description=description,
        expected_output="One valid JSON object matching the schema, and nothing else.",
        agent=agent,
    )