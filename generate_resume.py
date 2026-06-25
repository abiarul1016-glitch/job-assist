import json
import os
import subprocess
from datetime import datetime

from jinja2 import Environment, FileSystemLoader
from ollama import chat

template_path = "Template-Jakes-Resume.tex"


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
            "certification": "CS50's Introduction to Computer Programming",
            "url": "https://cs50.harvard.edu/certificates/c050320c-e34a-42eb-a1c7-81eb14e23551",
            "date": "Sep. 2025 -- Jan. 2026",
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
                "Selected as official photographer and videographer for SpurHacks, one of Canada's largest hackathons",
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
        "libraries": "numpy, pandas, ollama, google-genai",
        "verbal_languages": "English (native), French (fluent), Tamil (native)",
        "Finance & Business": "Equity research and valuation; retail discretionary trading; algorithmic trading system development",
    },
    "awards": [
        "HOSA Student Leadership Conference — CPR/FA (2024): 1st Place Nationwide",
        "Canadian Parents for French — Orals (2025): 1st - National Champion",
        "Fermat Mathematics Contest (2025): School Champion; Top 25% Nationally",
        "Target Alpha Stock Pitch Competition (2023): 1st Place in Canada",
    ],
}


def main():

    CONTENT_GENERATION_MESSAGES = []

    job_description = """

    Investment Banking Summer Analyst - Infrastructure M&A Advisory - Summer 2027

    About the job
Our Firm

Agentis Capital Advisors is a leading global financial advisor with a reputation for delivering unparalleled value and advice to its clients. The firm has been the recipient of numerous industry rewards in recent years, including 2024 P3 Awards Financial Advisor of the Year. Our guiding principles and ability to generate value for clients sets us apart. Agentis acts as a sell-side and buy-side advisor on a wide variety of global transactions including renewable power, energy, digital, transportation, and public-private partnerships. Our clients include leading infrastructure funds, pension funds, contractors, and governments.

Agentis Capital Advisors is a business segment of Agentis Capital Partners, which operates a synergistic platform across four main business segments: Agentis Capital Partners (principal investments), Agentis Capital Advisors (financial advisory and asset management services), Agentis Capital Mining Partners (mining advisory), and Agentis Capital Markets (capital markets).

The Opportunity

The intern program includes a formal program of instruction in project finance, financial statement analysis, and financial modeling. Analyst interns are expected to demonstrate financial modeling capabilities through real-world applications and will be invited to work on active projects. You will be recognized and rewarded for your individual performance within a close-knit team and meritocratic culture. Upon successful completion of the internship, interns have the opportunity to be invited back to join Agentis in a full-time position.

Participating in the execution of equity and debt offerings, mergers and acquisitions, public-private partnerships, and principal investments
Assisting in the development of complex financial models for infrastructure transactions, including the use of macros and VBA programming
Assisting in the management of due diligence processes, including managing third-party advisors
Developing asset valuations using a variety of approaches
    
"""

    prompt_content = f"""

    You are an expert AI resume writer specializing in Applicant Tracking Systems (ATS) optimization.
    Your task is to tailor the user's resume data to perfectly match a target job description.

    ### 1. TARGET JOB DESCRIPTION
    {job_description}

    ### 2. INPUT PROFILE DATA (JSON format)
    {json.dumps(user_data, indent=2)}

    CRITICAL FILTERING & LENGTH RULES:
    1. EXPERIENCE FILTER: The user data contains multiple experiences. You must evaluate them and select EXACTLY the top 2 most relevant experiences for the job description. Discard the rest. DO NOT make up new experiences, under any circumstances.
    2. PROJECT FILTER: Select up to 3 of the most relevant projects.
    3. CERTIFICATION FILTER: Select up to 2 certifications.
    4. BULLET COUNT: Every single item in 'experience' and 'projects' must contain exactly 2 or 3 bullet points. Never provide 1 bullet point; never exceed 3 bullet points.

    CRITICAL STRUCTURAL CONSTRAINTS
    - **Output Schema:** You must adhere 100% to the provided JSON structural boundaries. Do not alter keys or nestings.
    - **Strict Bullet Count:** Generate exactly 2 or 3 bullet points for each experience item and project item. Never exceed 3 bullet points under any circumstance.
    - **Immutable Blocks:** Keep the "contact" and "education" blocks completely identical to the input data. Do not modify, add, or delete any characters within them.
    - **LaTeX Safety:** Use plain text only. Do not use special characters (e.g., %, $, &, _, #, etc.). Avoid Markdown bolding (**) or italics (*) inside the string fields.

    BULLET POINT CONTENT QUALITY
    - **STAR/CAR Formula:** Write every bullet point using the Situation/Task/Context -> Action -> Result framework.
    - **Impact First:** Start bullet points with strong action verbs and emphasize quantifiable metrics or technical outcomes wherever possible.
    - **ATS Optimization:** Seamlessly integrate highly relevant keywords and technical skills found in the target job description to maximize resume scannability.
    - One bullet point must explain the project/experience itself

    The tone of the resume should be natural, reflecting a positive, hard working, and disciplined person. DO NOT make up new experiences, under any circumstances.

    Return only the optimized JSON object following these rules.

    """

    CONTENT_GENERATION_MESSAGES.append({"role": "user", "content": prompt_content})

    response = chat(
        model="qwen3.5:9b-mlx",
        messages=CONTENT_GENERATION_MESSAGES,
        think=False,
    )

    model_response = json.loads(response.message.content)
    CONTENT_GENERATION_MESSAGES.append(
        {"role": "assistant", "content": response.message.content}
    )

    print("Resume: \n", json.dumps(model_response, indent=2))
    generate_resume(model_response)

    todays_date = datetime.now().strftime("%B %d, %Y")

    cover_letter = {
        "date": todays_date,
        "subject_line": "Job Application for [Job Title]",
        "recipient": {
            "team": "Company Recruitment Team",
            "company": "Company Name from Job Description",
            "address_line_1": "Street Address or Remote if applicable",
            "address_line_2": "City, State, Zip Code",
        },
        "content": {
            "salutation": "Dear [Hiring Team / Company Name Team],",
            "introduction": "A strong 2-3 sentence opening hook. State the role and why you are drawn to their technical mission.",
            "body_paragraph_1": "Focus on your professional experience and core strengths. Highlight your work ethic, adaptability, and how you deliver impact.",
            "body_paragraph_2": "Focus on technical execution. Highlight 1 or 2 of your key projects (like your local-first automation pipelines) and how your skills directly solve the problems outlined in the job description.",
            "sign_off": "A professional sign-off phrase appropriate for this company culture (e.g., 'Sincerely,', 'Best regards,', 'Respectfully,')",
        },
    }

    cover_letter_prompt = f"""
    
        Now, your task is to write a highly tailored, compelling cover letter based on the optimized resume data and the target job description.

        ### 1. TONAL DIRECTIONS
        The letter must sound natural, professional, and authentic. Avoid generic AI corporate fluff. 
        Infuse the tone with a clear sense of grit, discipline, optimism, and passion for the specific engineering challenges mentioned.

        ### 2. CRITICAL STRUCTURAL CONSTRAINTS
        You must return ONLY a JSON object adhering exactly to this schema:
        
        {json.dumps(cover_letter, indent=2)}

        ### 3. LATEX SAFETY & FORMATTING
        - Use plain text only. DO NOT use unescaped LaTeX special characters (%, $, &, _, #). This will break the string, so DO NOT use them.
        - Do not use Markdown formatting (**, *) inside the JSON fields.

        Return only the optimized JSON object following these rules.
    """

    CONTENT_GENERATION_MESSAGES.append({"role": "user", "content": cover_letter_prompt})

    test_prompt = {"role": "user", "content": cover_letter_prompt}

    response = chat(
        model="qwen3.5:9b-mlx",
        messages=CONTENT_GENERATION_MESSAGES,
        think=False,
    )

    model_response = json.loads(response.message.content)
    # Enforce the exact current date in the payload python-side as a safety net
    # model_response["date"] = todays_date

    print("Cover Letter: \n", json.dumps(model_response, indent=2))
    generate_cover_letter(model_response)


def generate_resume(
    data, template_path="Template-Jakes-Resume.tex", output_tex="output_resume.tex"
):

    edit_latex(data, template_path, output_tex)

    # 4. Compile the .tex file into a PDF using pdflatex
    compile_latex_to_pdf(output_tex)


def generate_cover_letter(
    data,
    template_path="Template-Jakes-Cover-Letter.tex",
    output_tex="output_cover_letter.tex",
):

    edit_latex(data, template_path, output_tex)

    # 4. Compile the .tex file into a PDF using pdflatex
    compile_latex_to_pdf(output_tex)


def edit_latex(data, template_path, output_tex):

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
