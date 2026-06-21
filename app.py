"""
Streamlit front-end for the CrewAI Resume Review Agent.

Upload a resume (PDF or DOCX), optionally paste a job description, and get a
structured, multi-agent review report powered by the free Google Gemini API.
"""

import os
import re
import traceback
from io import BytesIO

import streamlit as st
from dotenv import load_dotenv
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate

from crew.resume_crew import run_resume_review
from utils.file_parser import extract_resume_text

load_dotenv()


def generate_pdf(report_text):
    """Generate a PDF version of the report."""
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()

    story = [
        Paragraph(
            report_text.replace("\n", "<br/>"),
            styles["BodyText"]
        )
    ]

    doc.build(story)

    buffer.seek(0)

    return buffer


def extract_score(report, label):
    """Extract score values from the report."""

    patterns = [
        rf"{label}.*?(\d+\.?\d*)/10",
        rf"{label}.*?(\d+\.?\d*)",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            report,
            re.IGNORECASE | re.DOTALL
        )

        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass

    return 0.0


st.set_page_config(
    page_title="AI Resume Review Crew",
    page_icon="📄",
    layout="wide"
)

MODEL_OPTIONS = {
    "Gemini 2.5 Flash (recommended)": "gemini/gemini-2.5-flash",
    "Gemini 2.5 Flash-Lite (fastest, lightest)": "gemini/gemini-2.5-flash-lite",
}

st.title("📄 AI Resume Review Crew")

st.caption(
    "A multi-agent resume reviewer built with CrewAI and Google Gemini. "
    "Upload your resume to get a detailed, structured review."
)

with st.sidebar:
    st.header("⚙️ Settings")

    default_key = os.getenv("GEMINI_API_KEY", "")

    api_key = st.text_input(
        "Google Gemini API Key",
        value=default_key,
        type="password",
        help="Get a free key at https://aistudio.google.com/apikey",
    )

    model_label = st.selectbox(
        "Model",
        list(MODEL_OPTIONS.keys())
    )

    model = MODEL_OPTIONS[model_label]

    st.markdown("---")

    st.markdown(
        "**Free tier note:** Gemini Flash models are free with rate limits. "
        "Get your key at [Google AI Studio](https://aistudio.google.com/apikey) "
        "— no credit card required."
    )

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Upload your resume")

    uploaded_file = st.file_uploader(
        "PDF or DOCX",
        type=["pdf", "docx"]
    )

with col2:
    st.subheader("2. (Optional) Target role")

    target_role = st.text_input(
        "Target job title",
        placeholder="e.g. Senior Data Analyst"
    )

    job_description = st.text_area(
        "Paste the job description (optional, but recommended for tailored feedback)",
        height=200,
        placeholder="Paste the full job posting here for a tailored job-fit analysis...",
    )

run_clicked = st.button(
    "🚀 Review My Resume",
    type="primary",
    use_container_width=True
)

if run_clicked:

    if not api_key:
        st.error(
            "Please enter your Gemini API key in the sidebar. "
            "Get a free one at https://aistudio.google.com/apikey"
        )

    elif not uploaded_file:
        st.error("Please upload a resume file (PDF or DOCX).")

    else:
        try:

            with st.spinner("Extracting text from your resume..."):
                resume_text = extract_resume_text(uploaded_file)

            with st.spinner(
                "Your AI crew is reviewing the resume... "
                "this can take 30-90 seconds as 4 specialist agents work through it."
            ):

                report = run_resume_review(
                    api_key=api_key,
                    resume_text=resume_text,
                    job_description=job_description,
                    target_role=target_role,
                    model=model,
                )

            st.success("Review complete!")

            overall = extract_score(report, "Overall Score")
            ats = extract_score(report, "ATS")
            jobfit = (
    extract_score(report, "Job Fit Score")
    or extract_score(report, "Job-Fit Score")
    or extract_score(report, "Job Fit")
)

            col_a, col_b, col_c = st.columns(3)

            with col_a:
                st.metric(
                    "Overall Score",
                    f"{overall}/10"
                )

            with col_b:
                st.metric(
                    "ATS Score",
                    f"{ats}/10"
                )

            with col_c:
                st.metric(
                    "Job Fit Score",
                    f"{jobfit}/10"
                )

            st.write("### 📊 Score Dashboard")

            st.write("Overall Score")
            st.progress(min(overall / 10, 1.0))

            st.write("ATS Score")
            st.progress(min(ats / 10, 1.0))

            st.write("Job Fit Score")
            st.progress(min(jobfit / 10, 1.0))

            st.markdown("---")

            st.markdown(report)

            st.download_button(
                "⬇️ Download Report (Markdown)",
                data=report,
                file_name="resume_review_report.md",
                mime="text/markdown",
            )

            pdf_file = generate_pdf(report)

            st.download_button(
                "📄 Download Report (PDF)",
                data=pdf_file,
                file_name="resume_review_report.pdf",
                mime="application/pdf",
            )

        except ValueError as ve:
            st.error(str(ve))

        except Exception as e:
            if "RESOURCE_EXHAUSTED" in str(e):
                st.error(
            "⚠️ Gemini free-tier quota exceeded.\n\n"
            "Please wait 1-2 minutes and try again, "
            "or switch to Gemini 2.5 Flash-Lite in the sidebar."
        )

            elif "API_KEY_INVALID" in str(e):
                st.error(
            "❌ Invalid Gemini API Key. "
            "Please check your API key and try again."
        )

            else:
                st.error(
            f"Something went wrong while running the crew: {e}"
        )

            with st.expander("Show technical details"):
                st.code(traceback.format_exc())

st.markdown("---")

st.caption(
    "Built with CrewAI 🤝 Streamlit 🤝 Google Gemini. "
    "Your resume and job description are sent only to the Gemini API "
    "for analysis and are not stored by this app."
)