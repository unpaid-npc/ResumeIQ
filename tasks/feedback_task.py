"""Task for the Feedback agent."""
import json

from crewai import Agent, Task

from backend.schemas import (
    FeedbackDraft,
    JobMatchResult,
    ParsedResume,
    ResumeEvaluation,
    SkillsAnalysis,
)


def create_feedback_task(
    agent: Agent,
    parsed: ParsedResume,
    skills: SkillsAnalysis,
    evaluation: ResumeEvaluation,
    job_match: JobMatchResult | None,
    resume_text: str,
) -> Task:
    schema = json.dumps(FeedbackDraft.model_json_schema())
    if job_match is not None:
        job_part = "JOB MATCH RESULT:\n" + job_match.model_dump_json() + "\n\n"
    else:
        job_part = (
            "NO JOB DESCRIPTION WAS PROVIDED. Do not mention job matching and do not "
            "compare the resume to any job.\n\n"
        )
    description = (
        "Write the final feedback for this candidate using ONLY the analysis below.\n\n"
        "STRICT RULES:\n"
        "- executive_summary: 3 to 4 sentences in plain language, honest and kind.\n"
        "- strengths and weaknesses: 3 to 5 short items each, based on the evaluation.\n"
        "- recommendations: 4 to 6 specific, actionable items, most important first. "
        "Each says what to change and why.\n"
        "- bullet_rewrites: choose 2 to 4 REAL bullet points. original must be copied "
        "EXACTLY from the resume text. improved must keep the same facts and may only "
        "improve the wording (stronger verb, clearer outcome). NEVER add numbers, tools, "
        "results or achievements that are not in the resume. If a number would help, "
        "write [add real number if you have one] inside improved.\n"
        "- next_steps: 3 to 5 simple things the candidate can do next.\n"
        "- In improved, do NOT add purposes, outcomes, audiences or results that the original does not state (for example, do not add a reason such as supporting tracking). Only change the verb and wording, or add a [placeholder] for details the candidate may add.\n"
        "- Never tell the candidate to add or claim a skill, tool or project in a description unless they truly used it. Phrase such advice with the words if you have actually used it.\n"
        "- If a job match result is given, mention what is supported and what is missing "
        "honestly. Never suggest claiming skills or experience the resume does not show.\n"
        "- Judge only the resume content. Do NOT use name, gender, age, nationality, "
        "religion or location.\n"
        "- Return ONLY one JSON object that follows the JSON schema below. "
        "No explanations, no markdown.\n\n"
        "JSON SCHEMA:\n" + schema + "\n\n"
        "PARSED RESUME DATA:\n" + parsed.model_dump_json() + "\n\n"
        "SKILLS ANALYSIS:\n" + skills.model_dump_json() + "\n\n"
        "RESUME EVALUATION:\n" + evaluation.model_dump_json() + "\n\n"
        + job_part
        + "ORIGINAL RESUME TEXT:\n" + resume_text
    )
    return Task(
        description=description,
        expected_output="One valid JSON object matching the schema, and nothing else.",
        agent=agent,
    )