"""
Task definitions for the Resume Review Crew.
"""
from crewai import Task


def build_tasks(agents: dict, resume_text: str, job_description: str, target_role: str) -> list:
    has_jd = bool(job_description and job_description.strip())

    content_analysis_task = Task(
        description=(
            "Analyze the following resume text and produce a structured breakdown.\n\n"
            f"RESUME TEXT:\n```\n{resume_text}\n```\n\n"
            "Cover, section by section (Summary, Experience, Skills, Education, "
            "Projects/Certifications if present):\n"
            "- What's present and what's missing\n"
            "- Whether bullet points use strong action verbs and quantified results "
            "(numbers, %, $, time saved)\n"
            "- Clarity, conciseness, and any vague or generic language\n"
            "- Overall structure and length appropriateness"
        ),
        expected_output=(
            "A structured section-by-section content analysis in markdown, with specific "
            "examples quoted briefly from the resume where relevant, and concrete "
            "suggestions for improvement under each section."
        ),
        agent=agents["resume_analyst"],
    )

    ats_task = Task(
        description=(
            "Using the same resume text, evaluate ATS (Applicant Tracking System) "
            "compatibility:\n"
            "- Formatting risks (tables, columns, text boxes, images, unusual fonts/symbols "
            "that may not parse correctly — infer these from how the text extracted)\n"
            "- Section headers: are they standard and recognizable (e.g. 'Experience' vs "
            "creative alternatives)?\n"
            "- Contact info placement and completeness\n"
            "- Keyword density and relevance for the candidate's apparent field"
            + (
                f"\n- Specifically check keyword alignment against this job description:\n"
                f"```\n{job_description}\n```"
                if has_jd
                else ""
            )
        ),
        expected_output=(
            "A markdown report with an ATS Compatibility Score out of 10, a list of "
            "specific risks found, and concrete formatting/keyword fixes."
        ),
        agent=agents["ats_specialist"],
    )

    if has_jd:
        fit_description = (
            "Compare the candidate's resume against this target job description and role:\n"
            f"TARGET ROLE: {target_role or 'Not specified'}\n"
            f"JOB DESCRIPTION:\n```\n{job_description}\n```\n\n"
            f"RESUME TEXT:\n```\n{resume_text}\n```\n\n"
            "Identify:\n"
            "- The 3-5 most important requirements in the JD and whether the resume "
            "demonstrates them\n"
            "- Specific gaps or missing keywords/skills\n"
            "- Concrete suggestions for how to tailor existing bullet points (not just "
            "'add more keywords') to better match this role\n"
            "- An overall Job-Fit Score out of 10"
        )
    else:
        fit_description = (
            "No specific job description was provided. Using the resume text and the "
            f"candidate's apparent target role ('{target_role or 'unspecified - infer from resume'}'), "
            "evaluate general competitiveness against current industry best practices for "
            "that field:\n"
            f"RESUME TEXT:\n```\n{resume_text}\n```\n\n"
            "Identify the 3-5 highest-impact improvements that would make this resume more "
            "competitive, and give an overall Competitiveness Score out of 10."
        )

    job_fit_task = Task(
        description=fit_description,
        expected_output=(
            "A markdown report with a numeric score out of 10, a prioritized list of gaps, "
            "and specific, rewritten example bullet points showing the improvement."
        ),
        agent=agents["job_match_strategist"],
    )

    final_report_task = Task(
        description=(
            "You have received three specialist reports: a content analysis, an ATS "
            "compatibility evaluation, and a job-fit/competitiveness assessment. "
            "Synthesize them into ONE final, polished resume review report for the "
            "candidate. Do not just concatenate the inputs.\n\n"
            "Structure the final report as:\n"
            "1. **Overall Score** (out of 10, weighted average of the sub-scores, with one "
            "sentence justifying it)\n"
            "2. **Top 3 Strengths**\n"
            "3. **Top 5 Priority Fixes** (most impactful first, each with a concrete example)\n"
            "4. **Section-by-Section Feedback** (condensed from the content analysis)\n"
            "5. **ATS Compatibility Summary**\n"
            "6. **Job-Fit Summary** (if a job description was provided) or "
            "**Competitiveness Summary** (if not)\n"
            "7. **Next Steps Checklist** (a short, actionable checklist the candidate can "
            "work through)\n\n"
            "Keep the tone direct, specific, and encouraging — like a great mentor, not a "
            "generic AI."
        ),
        expected_output=(
            "A complete, well-formatted markdown resume review report following the exact "
            "7-section structure described, ready to show directly to the candidate."
        ),
        agent=agents["report_compiler"],
        context=[content_analysis_task, ats_task, job_fit_task],
    )

    return [content_analysis_task, ats_task, job_fit_task, final_report_task]
