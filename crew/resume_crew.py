"""
Assembles and runs the Resume Review Crew end-to-end.
"""
from crewai import Crew, Process

from .agents import build_agents, build_llm
from .tasks import build_tasks


def run_resume_review(
    api_key: str,
    resume_text: str,
    job_description: str = "",
    target_role: str = "",
    model: str = "gemini/gemini-2.5-flash",
) -> str:
    """
    Runs the full 4-agent resume review crew and returns the final markdown
    report as a string.

    Args:
        api_key: Google Gemini API key (free tier works fine).
        resume_text: Plain text extracted from the candidate's resume.
        job_description: Optional job posting text for tailored feedback.
        target_role: Optional target job title, used as extra context.
        model: CrewAI/LiteLLM model string, e.g. "gemini/gemini-2.5-flash".
    """
    llm = build_llm(api_key=api_key, model=model)
    agents = build_agents(llm)
    tasks = build_tasks(
        agents=agents,
        resume_text=resume_text,
        job_description=job_description,
        target_role=target_role,
    )

    crew = Crew(
        agents=list(agents.values()),
        tasks=tasks,
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()
    return str(result)
