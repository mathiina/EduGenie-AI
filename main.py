"""
EduGenie
Google Gemini Powered Learning Assistant

Main FastAPI application.
"""


from pathlib import Path
from typing import Optional


from fastapi import (
    FastAPI,
    Request
)

from fastapi.responses import (
    HTMLResponse,
    JSONResponse
)

from fastapi.templating import (
    Jinja2Templates
)

from fastapi.staticfiles import (
    StaticFiles
)

from pydantic import BaseModel, Field


# EduGenie modules

from qna import answer_question

from explanation_module import (
    explain_topic
)

from quiz_module import (
    generate_quiz
)

from summary_module import (
    summarize_text
)

from learning_path import (
    get_learning_recommendations
)


# ==========================================================
# PROJECT PATH
# ==========================================================

BASE_DIR = Path(
    __file__
).resolve().parent


# ==========================================================
# FASTAPI APP
# ==========================================================

app = FastAPI(

    title="EduGenie",

    description=(
        "Google Gemini Powered "
        "Learning Assistant"
    ),

    version="1.0.0"
)


# ==========================================================
# TEMPLATES
# ==========================================================

templates = Jinja2Templates(

    directory=str(
        BASE_DIR / "templates"
    )
)


# ==========================================================
# STATIC FILES
# ==========================================================

app.mount(

    "/static",

    StaticFiles(
        directory=str(
            BASE_DIR / "static"
        )
    ),

    name="static"
)


# ==========================================================
# REQUEST MODELS
# ==========================================================


class QuestionRequest(BaseModel):

    question: str = Field(
        ...,
        min_length=1
    )


class ExplainRequest(BaseModel):

    topic: str = Field(
        ...,
        min_length=1
    )


class TextRequest(BaseModel):

    text: str = Field(
        ...,
        min_length=1
    )


class LearningPathRequest(BaseModel):

    topic: str = Field(
        ...,
        min_length=1
    )

    level: Optional[str] = Field(
        default="beginner"
    )


# ==========================================================
# HOME PAGE
# ==========================================================


@app.get(
    "/",
    response_class=HTMLResponse
)
async def home(
    request: Request
):

    return templates.TemplateResponse(

        request=request,

        name="index.html",

        context={
            "title": "EduGenie"
        }
    )


# ==========================================================
# HEALTH CHECK
# ==========================================================


@app.get("/health")
async def health():

    return {

        "status": "ok",

        "application": "EduGenie",

        "version": "1.0.0"
    }


# ==========================================================
# Q&A
# ==========================================================


@app.post("/qa")
async def qa(
    request: QuestionRequest
):

    try:

        result = answer_question(
            request.question
        )


        return {

            "success": True,

            "task": "qa",

            "result": result
        }


    except Exception as error:

        return JSONResponse(

            status_code=500,

            content={

                "success": False,

                "error": str(error)
            }
        )


# ==========================================================
# EXPLANATION
# ==========================================================


@app.post("/explain")
async def explain(
    request: ExplainRequest
):

    try:

        result = explain_topic(
            request.topic
        )


        return {

            "success": True,

            "task": "explain",

            "result": result
        }


    except Exception as error:

        return JSONResponse(

            status_code=500,

            content={

                "success": False,

                "error": str(error)
            }
        )


# ==========================================================
# QUIZ
# ==========================================================


@app.post("/quiz")
async def quiz(
    request: TextRequest
):

    try:

        result = generate_quiz(
            request.text
        )

        payload = (
            result.model_dump()
            if hasattr(result, "model_dump")
            else result
        )

        return {

            "success": True,

            "task": "quiz",

            "result": payload
        }


    except Exception as error:

        return JSONResponse(

            status_code=500,

            content={

                "success": False,

                "error": str(error)
            }
        )


# ==========================================================
# SUMMARIZE
# ==========================================================


@app.post("/summarize")
async def summarize(
    request: TextRequest
):

    try:

        result = summarize_text(
            request.text
        )


        return {

            "success": True,

            "task": "summarize",

            "result": result
        }


    except Exception as error:

        return JSONResponse(

            status_code=500,

            content={

                "success": False,

                "error": str(error)
            }
        )


# ==========================================================
# LEARNING PATH
# ==========================================================


@app.post(
    "/learn/recommendations"
)
async def learning_recommendations(
    request: LearningPathRequest
):

    try:

        result = (
            get_learning_recommendations(

                topic=request.topic,

                level=(
                    request.level
                    or "beginner"
                )
            )
        )


        return {

            "success": True,

            "task": "learning_path",

            "result": result
        }


    except Exception as error:

        return JSONResponse(

            status_code=500,

            content={

                "success": False,

                "error": str(error)
            }
        )


# ==========================================================
# RUN APPLICATION
# ==========================================================


if __name__ == "__main__":

    import uvicorn


    uvicorn.run(

        "main:app",

        host="127.0.0.1",

        port=8000,

        reload=True
    )