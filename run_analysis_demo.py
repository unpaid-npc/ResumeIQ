"""Runs Parser -> Skills Analyst -> Evaluator on the synthetic resume. Uses 3 API requests."""
from backend.schemas import OutputValidationError
from run_parser_demo import SAMPLE_RESUME
from services.analysis_service import AnalysisError, analyze_resume
from services.llm_config import ConfigError


def main() -> None:
    try:
        results = analyze_resume(SAMPLE_RESUME)
    except (ConfigError, OutputValidationError, AnalysisError) as exc:
        print("Problem:", exc)
        return

    print("\n=== SKILLS ===")
    for s in results.skills.skills:
        print(f"{s.skill:<14} {s.category:<20} {s.status}")

    print("\n=== SCORES (0-10) ===")
    for name, value in results.evaluation.scores.model_dump().items():
        print(f"{name:<22} {value}")

    print("\n=== STRENGTHS ===")
    for f in results.evaluation.strengths:
        print(f"- [{f.area}] {f.observation}")

    print("\n=== IMPROVEMENTS ===")
    for f in results.evaluation.improvements:
        print(f"- [{f.area}] {f.observation}")
        if f.suggestion:
            print(f"    Suggestion: {f.suggestion}")


if __name__ == "__main__":
    main()