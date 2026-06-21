"""
Agent definitions for the Resume Review Crew.

Four specialist agents collaborate sequentially:
1. Resume Content Analyst   - reviews writing quality & completeness
2. ATS Optimization Specialist - checks ATS/formatting compatibility
3. Career Coach & Job-Fit Strategist - compares resume to a target job
4. Lead Report Compiler     - synthesizes everything into one final report
"""
from crewai import Agent, LLM


def build_llm(api_key: str, model: str = "gemini/gemini-2.5-flash", temperature: float = 0.4) -> LLM:
    """
    Construct the Gemini-backed LLM shared by all agents.

    `model` uses CrewAI's native Gemini provider via the "gemini/<model-name>"
    prefix. Gemini 2.5 Flash and Flash-Lite are free-tier eligible (rate limited).
    Get a free key at https://aistudio.google.com/apikey
    """
    return LLM(model=model, api_key=api_key, temperature=temperature)


def build_agents(llm: LLM) -> dict:
    resume_analyst = Agent(
        role="Resume Content Analyst",
        goal=(
            "Carefully read the candidate's resume and produce a clear, structured "
            "breakdown of its sections, content quality, and completeness."
        ),
        backstory=(
            "You are a meticulous former corporate recruiter with 12 years of experience "
            "screening thousands of resumes across tech, finance, and operations roles. "
            "You have a sharp eye for vague bullet points, missing metrics, and weak "
            "summaries, and you always explain WHY something is weak, not just THAT it is."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    ats_specialist = Agent(
        role="ATS Optimization Specialist",
        goal=(
            "Evaluate how well the resume would survive an Applicant Tracking System (ATS) "
            "scan, focusing on formatting, structure, and keyword presence."
        ),
        backstory=(
            "You spent years reverse-engineering how ATS platforms like Workday, Greenhouse, "
            "and Taleo parse resumes. You know which formatting choices silently break "
            "parsing (tables, columns, graphics, headers/footers) and which keyword patterns "
            "get resumes flagged as a strong match."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    job_match_strategist = Agent(
        role="Career Coach & Job-Fit Strategist",
        goal=(
            "Compare the resume against the target job description (if provided) or general "
            "industry best practices, and identify the most impactful gaps and tailoring "
            "opportunities."
        ),
        backstory=(
            "You are a career coach who has helped candidates land offers at competitive "
            "companies. You focus on alignment between what the resume demonstrates and what "
            "a role actually requires, and you prioritize the 3-5 changes that will move the "
            "needle most, instead of overwhelming the candidate with minor nitpicks."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    report_compiler = Agent(
        role="Lead Report Compiler",
        goal=(
            "Synthesize the content analysis, ATS evaluation, and job-fit assessment into a "
            "single, well-organized, actionable feedback report for the candidate."
        ),
        backstory=(
            "You are the senior editor on the team. You take detailed input from specialists "
            "and turn it into a polished, encouraging, and genuinely useful final report, with "
            "a clear overall score and a prioritized action list."
        ),
        llm=llm,
        verbose=True,
        allow_delegation=False,
    )

    return {
        "resume_analyst": resume_analyst,
        "ats_specialist": ats_specialist,
        "job_match_strategist": job_match_strategist,
        "report_compiler": report_compiler,
    }
