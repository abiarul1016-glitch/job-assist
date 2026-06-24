from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ollama import AsyncClient
from pydantic import BaseModel
from rapidfuzz import process

app = FastAPI()

# Allow your JavaScript frontend to communicate with your backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your specific frontend URL in production
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

MASTER_PROFILE = {
    "first_name": "Abishan",
    "last_name": "Arulselvan",
    "middle_name": "",
    "email": "abiarul1016@gmail.com",
    "github_url": "https://github.com/abiarul1016-glitch",
    "linkedin_url": "https://www.linkedin.com/in/abishan-arulselvan/",
    "address": "8 Ridgehaven Court",
    "city": "Brampton",
    "province": "Ontario",
    "country": "Canada",
    "postal_code": "L6P3K7",
    "phone_number": "6475623968",
    "job": "Skipper",
    "school": "University of Waterloo",
}


# matching fields request body
class matchFieldsRequest(BaseModel):
    fields: list[str]


MESSAGES = [
    {
        "role": "system",
        "content": f"""
        You are a helpful assistant which aids users to apply to jobs.
        Don't use special characters, only use plain text, as this will be used for job applications.
        You will assist users by returning details regarding their profile if needed, or answering application questions in their tone, with tailored answers.
        Here is the given profile of your user: {MASTER_PROFILE}.
        """,
    }
]

JOB_DETAILS = ""


async def chat(MESSAGES=MESSAGES):
    response = await AsyncClient().chat(
        model="qwen3.5:9b", messages=MESSAGES, think=False
    )

    return response.message.content


@app.get("/")
async def index():
    return {"message": "This is the API serving data for Job Assist."}


@app.get("/newAI")
async def newAI():

    # reset messages list, for new application
    MESSAGES.clear()

    MESSAGES.append(
        {
            "role": "system",
            "content": f"""
        You are a helpful assistant which aids users to apply to jobs.
        Don't use special characters, only use plain text, as this will be used for job applications.
        You will assist users by returning details regarding their profile if needed, or answering application questions in their tone, with tailored answers.
        Here is the given profile of your user: {MASTER_PROFILE}.
        """,
        }
    )

    return "New AI context successfully established."


@app.get("/master-profile/")
async def master_profile():

    return MASTER_PROFILE


@app.get("/fuzzy-match/{inputFieldText}")
async def fuzzyMatch(inputFieldText: str):

    clean_input = inputFieldText.lower()

    if result := process.extractOne(
        clean_input, MASTER_PROFILE.keys(), score_cutoff=70
    ):
        return result[0]
    else:
        return None


# askAI request body
class queryDict(BaseModel):
    query: str


@app.post("/updateAI/")
async def updateAI(update: queryDict):

    # update JOB_DETAILS global variable, for possible later use
    globals()["JOB_DETAILS"] = update.query

    MESSAGES.append(
        {
            "role": "user",
            "content": f"Here is some additional details regarding the job: {JOB_DETAILS}",
        }
    )
    return await chat()


@app.post("/askAI/")
async def askAI(queryDict: queryDict):
    MESSAGES.append({"role": "user", "content": queryDict.query})
    return await chat()


@app.get("/tailoredResume")
async def tailoredResume():
    pass


class resumeDetails(BaseModel):
    pass


async def generateResumeDetails(user_details, job_details=JOB_DETAILS):

    MESSAGES.append(
        {
            "role": "user",
            "content": f"""
            
            Using the details of the job and the following resume of the user, 
        
            improve it, so that this is much tailored for the job they are applying for, and so that they are much
            likely to receive the job. Make sure to follow the STAR, CAT, etc. formats for the bullet points. Make
            sure to use keywords so that it is easy to scan for the recruiter and ATS.
         
            Ensure to output a JSON, with clean characters, as your outputted text is going to be used by a LaTex Editor.
            
            Here are the job details once more:
            
            {job_details}

            Here is the applicant's resume/details:
            
            {user_details}

            """,
        }
    )

    response = await AsyncClient().chat(
        model="qwen3.5:9b",
        messages=MESSAGES,
        format=resumeDetails.model_json_schema(),
        think=True,
    )

    output_resumeDetails = resumeDetails.model_validate_json(response.message.content)
    return output_resumeDetails


@app.post("/api/fields/")
async def matchField(request_data: matchFieldsRequest):
    MESSAGES = []

    fields_list = request_data.fields

    answers = {}
    for field in fields_list:
        cleaned_field = field.lower()

        match cleaned_field:
            case "first name":
                answers[field] = "Abishan"
            case "last name":
                answers[field] = "Arulselvan"
            case "email":
                answers[field] = "abiarul1016@gmail.com"
            case "github":
                answers[field] = "glitch/something"
            case "linkedin":
                answers[field] = "linkedin/something"
            case _:
                MESSAGES.append({"role": "user", "content": cleaned_field})
                answers[field] = await chat(MESSAGES)

    return answers
