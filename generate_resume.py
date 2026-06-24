import json
import os
import subprocess
from typing import List, Literal

from jinja2 import Environment, FileSystemLoader
from ollama import chat
from pydantic import BaseModel, Field, ValidationError

template_path = "Template-Jakes-Resume.tex"

# --- Sub-models for structured nesting ---


class ContactSchema(BaseModel):
    # Freezing these exact strings so the LLM cannot mutate them
    name: Literal["Abishan Arulselvan"] = "Abishan Arulselvan"
    phone: Literal["647-562-3968"] = "647-562-3968"
    email: Literal["abiarul1016@gmail.com"] = "abiarul1016@gmail.com"
    linkedin: Literal["linkedin.com/in/abishan-arulselvan"] = (
        "linkedin.com/in/abishan-arulselvan"
    )
    github: Literal["github.com/abiarul1016-glitch"] = "github.com/abiarul1016-glitch"


class EducationItem(BaseModel):
    school: str
    location: str
    degree: str
    date: str


class CertificationItem(BaseModel):
    issuer: str
    location: str
    certification: str
    url: str
    date: str


class ExperienceItem(BaseModel):
    company: str
    location: str
    role: str
    date: str
    url: str
    # Constraint: Enforces exactly 2 to 3 bullet items per experience
    bullets: List[str] = Field(
        ...,
        min_length=2,
        max_length=3,
        description="Array containing exactly 2 to 3 bullet points describing achievements.",
    )


class ProjectItem(BaseModel):
    title: str
    url: str
    technologies: str
    date: str
    # Constraint: Enforces exactly 2 to 3 bullet items per project
    bullets: List[str] = Field(
        ...,
        min_length=2,
        max_length=3,
        description="Array containing exactly 2 to 3 bullet points highlighting technical execution.",
    )


class SkillsSchema(BaseModel):
    languages: str
    frameworks: str
    tools: str
    libraries: str


# --- Master Profile Schema containing constraints ---


class ResumeSchema(BaseModel):
    contact: ContactSchema = Field(
        ..., description="Static contact information. Do not alter."
    )

    # Enforcing the specific static education history using standard tuple/list layout
    education: List[EducationItem] = Field(
        default=[
            EducationItem(
                school="University of Waterloo",
                location="Waterloo, ON",
                degree="Bachelor of Math, Finance Specialization",
                date="Sep. 2026 -- Present",
            ),
            EducationItem(
                school="Turner Fenton Secondary School",
                location="Brampton, ON",
                degree="International Baccalaureate",
                date="Sep. 2022 -- June 2026",
            ),
        ],
        description="Static education history. Do not alter.",
    )

    # Constraint: Must return at least 1 certification
    certifications: List[CertificationItem] = Field(
        ...,
        min_length=1,
        description="List of professional certifications. Must contain at least 1 item.",
    )

    # Constraint: Maximum of 2 experiences
    experience: List[ExperienceItem] = Field(
        ...,
        max_length=2,
        description="List of professional experience items. Maximum of 2 entries.",
    )

    # Constraint: Exactly 2 projects (min=2, max=2)
    projects: List[ProjectItem] = Field(
        ...,
        min_length=2,
        max_length=2,
        description="List of technical projects. Exactly 2 entries are required.",
    )

    skills: SkillsSchema


# --- Generate JSON Schema for Ollama ---
ollama_json_schema = ResumeSchema.model_json_schema()


user_data = {
    "contact": {
        "name": "Abishan Arulselvan",
        "phone": "647-562-3968",
        "email": "abiarul1016@gmail.com",
        "linkedin": "linkedin.com/in/abishan-arulselvan",
        "github": "github.com/abiarul1016-glitch",
    },
    "education": [
        {
            "school": "University of Waterloo",
            "location": "Waterloo, ON",
            "degree": "Bachelor of Math, Finance Specialization: MATH 145, 146 and CS 146 (Advanced)",
            "date": "Sep. 2026 -- Present",
        },
        {
            "school": "Turner Fenton Secondary School",
            "location": "Brampton, ON",
            "degree": "International Baccalaureate Diploma Program",
            "date": "Sep. 2022 -- June 2026",
        },
    ],
    "certifications": [
        {
            "issuer": "Harvard CS50",
            "location": "Cambridge, Massachusetts",
            "certification": "CS50's Introduction to Programming with Python",
            "url": "https://cs50.harvard.edu/certificates/c050320c-e34a-42eb-a1c7-81eb14e23551",
            "date": "Sep. 2025 -- April 2026",
        },
        {
            "issuer": "Harvard CS50",
            "location": "Cambridge, Massachusetts",
            "certification": "CS50's Introduction to Programming with Python",
            "url": "https://cs50.harvard.edu/certificates/c050320c-e34a-42eb-a1c7-81eb14e23551",
            "date": "Sep. 2025 -- April 2026",
        },
    ],
    "experience": [
        {
            "company": "Independent",
            "location": "GTA, ON",
            "role": "DJ (Instagram: @ dj.abishan)",
            "date": "Oct. 2023 -- Oct. 2025",
            "url": "",
            "bullets": [
                "Built a personal brand from the ground up, performing at school and private events with audiences of up to 800+ attendees",
                "Managed all operational aspects, including booking negotiations, pricing structure development, promotion, and client relationship management",
            ],
        },
        {
            "company": "Independent",
            "location": "GTA, ON",
            "role": "Photographer and Videographer (Instagram: @ abi.flicks)",
            "date": "Jul. 2022 -- Aug. 2025",
            "url": "",
            "bullets": [
                "Self-taught photographer, videographer, and editor producing promotional, commercial, and event-based media",
                "Selected as official photographer and videographer for SpurHacks, one of Canada’s largest hackathons",
            ],
        },
        {
            "company": "Tech Corp",
            "location": "Remote",
            "role": "Software Engineer",
            "date": "June 2024 -- Present",
            "url": "",
            "bullets": [
                "Developed scalable features using Python and Flask, improving system uptime.",
                "Collaborated with cross-functional teams to deliver projects ahead of schedule.",
            ],
        },
    ],
    "projects": [
        {
            "title": "rental suite",
            "url": "https://github.com/abiarul1016-glitch/rental-suite",
            "technologies": "Python, Playwright, Ollama, Qwen, Pydantic, asyncio",
            "date": "Feb. 2026 -- April 2026",
            "overview": "rental suite is a local-first automation tool that concurrently posts optimized real estate listings to Facebook Marketplace and Kijiji. It utilizes a local LLM to generate fresh ad content every five cycles, avoiding duplicate detection while managing end-to-end browser automation.",
            "bullets": [
                "Engineered a multi-platform automation pipeline using Python and Playwright to handle concurrent listing operations across Facebook Marketplace and Kijiji.",
                "Integrated local Qwen 3.5 models via Ollama to dynamically generate optimized listing titles, detailed descriptions, and search tags verified through Pydantic data validation structures.",
                "Implemented an asynchronous concurrency model using asyncio and browser session persistence to execute form filling and photo uploads simultaneously, cutting manual listing management time down entirely.",
                "Designed a self-updating JSON data storage layer to track property histories, rotating text variations every five runs to systematically bypass platform duplicate content flags.",
            ],
        },
        {
            "title": "Skipper",
            "url": "https://github.com/abiarul1016-glitch/Skipper",
            "technologies": "Python, Flask, Twilio, Ollama, MLX-Audio (Voice Cloning)",
            "date": "March 2026 -- May 2026",
            "overview": """"Skipper" is an automated tool that uses AI, voice cloning, and caller ID spoofing to generate realistic, automated calls to school attendance offices for student absences. It integrates with Google Calendar and local LLM models to generate excuses and uses Twilio to impersonate a parent's voice, aiming to bypass detection.""",
            "bullets": [
                "Engineered an automated telephonic absence verification system by integrating Twilio API and Flask so I could skip school by cloning my dad's voice!",
                "Integrated MLX-Audio to synthesize text-to-speech outputs mimicking authenticated parental voice profiles, successfully bypassing manual school office screening barriers across multiple test deployments",
                "Architected a scalable backend orchestration layer using a local Ollama LLM to dynamically parse administrative call-response configurations and ensure 100 percent execution accuracy under varying cellular conditions",
            ],
        },
        {
            "title": "sent.",
            "url": "https://github.com/abiarul1016-glitch/auto-job-cold-emailer",
            "technologies": "Python, Playwright, Ollama, Qwen LLM, aiosmtplib, Asynchronous Programming",
            "date": "April 2026 -- May 2026",
            "overview": """sent. is an interactive command-line AI agent that automates the job search process by researching companies, generating personalized cold emails, and sending them via Gmail. The tool utilizes local Qwen models through Ollama for personalization, Playwright for browser automation, and tracks sent emails to prevent duplicates.""",
            "bullets": [
                "Accelerated corporate lead qualification and outreach efficiency by engineering an autonomous, multi-stage CLI web agent that collapses research and contact pipelines into a single session",
                "Orchestrated a dynamic browser scraping infrastructure using Playwright to extract real-time web text, interface with DOM elements, and cache multi-session authentication states",
                "Mitigated bounce rates and out-of-context outreach by leveraging a local Qwen LLM via Ollama to generate highly targeted, context-aware email payloads delivered asynchronously via aiosmtplib SMTP routing",
                "Eliminated duplicate message delivery risks across iterative script cycles by developing a state-persistent JSON tracking system to validate target history prior to network dispatch",
            ],
        },
        {
            "title": "Aise",
            "url": "https://github.com/abiarul1016-glitch/easymind",
            "technologies": "Python, Django, Django REST Framework, SQLite, Ollama, HTML/CSS",
            "date": "May 2026 -- June 2026",
            "overview": """Aise is a fast, single-page web app designed to simplify making reminders. It uses a custom HTML/CSS frontend and a Django REST backend to handle basic reminder creation and management. Its key features include:AI Parsing: Extracts titles, dates, times, and locations from standard text using a local Ollama AI model. Smart Fallbacks: Uses basic Python code to process text if the AI is offline. Title Polishing: Cleans up messy text into neat, readable titles.Flexible Accounts: Saves reminders for logged-in users while still allowing anonymous guest access.""",
            "bullets": [
                "Accomplished a 4x reduction in event creation friction by engineering a custom single-page Django web application that replaces multi-field inputs with a single conversational field",
                "Developed RESTful CRUD endpoints and an asynchronous processing pipeline utilizing Django REST Framework to instantly parse and clean unstructured reminder strings into validated schema payloads",
                "Optimized application uptime and system resilience by implementing high-performance local LLM extraction (Ollama/Qwen 3.5) alongside zero-dependency Python heuristic fallbacks for guaranteed offline token parsing",
            ],
        },
        {
            "title": "TeaTime",
            "url": "https://www.instagram.com/teatime_canada/",
            "technologies": "JA Company Program, Excel, Public Speaking, Pitching, Social Media Marketing",
            "date": "Oct. 2023 -- April 2024",
            "overview": """A 6-month long project developed by a group of teenagers within the JA Company Program. Led to lasting friendships as well as great profits, as we sold many products at the First Canadian Place in Downtown Toronto.""",
            "bullets": [
                "Co-founded a consumer goods brand specializing in curated international tea boxes, managing the full product lifecycle from sourcing to sale.",
                "Spearheaded financial strategy, including pricing models and cost analysis, contributing to a fully sold-out initial product batch within one week.",
            ],
        },
    ],
    "skills": {
        "languages": "C, Python, SQL, HTML, CSS, JavaScript",
        "frameworks": "React, Flask, FastAPI",
        "tools": "Git, Docker, Ollama, Twilio",
        "libraries": "numpy, pandas",
    },
}


def main():

    job_description = "This is a software internship job at Google for undergraduate students. Your role will primarily involve QA (Quality Assurance), so having knowledge of automation frameworks such as Playwright, would be useful."

    prompt_content = f"""
    You are an expert resume optimizer, who tailors resumes for given job descriptions.
    Process the following input profile data to tailor it to this job description:
    
    {job_description}
    
    .
    You must adhere completely to the structural boundaries provided by the schema.
    Don't use special characters, only use plain text, as this will be used for job applications, and be generated via a LaTex editor.
    Ensure the improved bullet points utilize keywords, so that the resume is easily scannable by ATS and recruiters. They must also follow the STAR/CAR convention.

    CRITICAL INSTRUCTIONS:
    - You must include exactly 2 or 3 highly optimized bullet points for each experience item and project item. 
    - Do not exceed 3 bullet points per item under any circumstance.
    - Keep the contact and education blocks strictly identical to the input.


    Input Profile Data:
    {json.dumps(user_data, indent=2)}

    """

    max_retries = 3
    messages = [{"role": "user", "content": prompt_content}]

    for attempt in range(max_retries):
        print(f"Generation Attempt {attempt + 1}/{max_retries}...")

        try:
            # Execute chat with format constraint
            response = chat(
                model="qwen3.5:9b",
                messages=messages,
                options={"temperature": 0.0},
                format=ResumeSchema.model_json_schema(),
                think=False,
            )

            # Attempt Pydantic validation
            validated_data = ResumeSchema.model_validate_json(response.message.content)
            print("Successfully validated JSON against Pydantic schema!")

            generate_resume(validated_data)
            return

        except ValidationError as ve:
            print(f" Validation failed on attempt {attempt + 1}.")

            # Format the exact errors to hand back to the LLM
            error_feedback = f"""
            Your previous JSON output failed Pydantic validation with the following errors:
            {str(ve)}
            
            Please correct your mistakes and output a perfectly compliant JSON structure.
            """

            # Append the failed output and the error message to the history
            messages.append({"role": "assistant", "content": response.message.content})
            messages.append({"role": "user", "content": error_feedback})

        except Exception as e:
            print(f"An unexpected API or decoding error occurred: {e}")

    raise RuntimeError(
        f"Failed to generate valid profile structure after {max_retries} attempts."
    )


def generate_resume(
    data, template_path="Template-Jakes-Resume.tex", output_tex="output_resume.tex"
):

    # 1. Configure Jinja to use LaTeX-safe delimiters
    env = Environment(
        block_start_string="[%",
        block_end_string="%]",
        variable_start_string="<<",
        variable_end_string=">>",
        comment_start_string="[#",
        comment_end_string="#]",
        loader=FileSystemLoader(os.path.dirname(template_path) or "."),
    )

    # 2. Load and render the template with dictionary
    template = env.get_template(os.path.basename(template_path))
    rendered_tex = template.render(data=data)

    # 3. Write the filled-in LaTeX code to a new file
    with open(output_tex, "w") as f:
        f.write(rendered_tex)

    # 4. Compile the .tex file into a PDF using pdflatex
    compile_latex_to_pdf(output_tex)


def compile_latex_to_pdf(tex_file_path, output_dir=None):
    """Compiles a .tex file into a .pdf file using pdflatex."""
    if not os.path.exists(tex_file_path):
        raise FileNotFoundError(f"The file {tex_file_path} does not exist.")

    # Base command flags
    # '-interaction=nonstopmode' prevents the CLI from freezing on error
    cmd = ["pdflatex", "-interaction=nonstopmode"]

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        cmd.append(f"-output-directory={output_dir}")

    cmd.append(tex_file_path)

    try:
        print("Compiling LaTeX document...")
        # Run compiler and capture output logs
        result = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
        )
        print("Success! PDF generated.")
        return True
    except subprocess.CalledProcessError as e:
        print("Compilation failed with exit code:", e.returncode)
        print("Error details:\n", e.stdout)  # LaTeX writes errors to stdout
        return False


if __name__ == "__main__":
    main()
