import json
import re

from gemini_client import generate_text


def clean_json_block(text: str) -> str:
    """
    Remove Markdown code fences and extract the JSON object.
    """
    text = text.strip()

    # Remove ```json or ``` from the beginning
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)

    # Remove ``` from the end
    text = re.sub(r"\s*```$", "", text)

    # Find the JSON object
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1:
        text = text[start:end + 1]

    return text.strip()


def generate_quiz(topic: str):
    """
    Generate exactly 3 multiple-choice questions
    with exactly 4 options for the given topic.
    """

    prompt = f"""
You are an educational quiz generator.

Create a beginner-friendly quiz about:

{topic}

IMPORTANT REQUIREMENTS:

1. Generate EXACTLY 3 questions.
2. Each question must have EXACTLY 4 options.
3. Options must be A, B, C and D.
4. Only ONE answer must be correct for each question.
5. Questions must be directly related to the topic.
6. Do not repeat questions.
7. Keep questions simple and clear.
8. Provide a short explanation for every answer.
9. Return ONLY valid JSON.
10. Do NOT return Markdown.
11. Do NOT return ```json.
12. Do NOT add any text outside the JSON.

Use this EXACT structure:

{{
    "title": "Quick Quiz on {topic}",
    "questions": [
        {{
            "question": "Question 1",
            "options": [
                "A. Option 1",
                "B. Option 2",
                "C. Option 3",
                "D. Option 4"
            ],
            "answer": "A. Option 1",
            "explanation": "Short explanation of the correct answer."
        }},
        {{
            "question": "Question 2",
            "options": [
                "A. Option 1",
                "B. Option 2",
                "C. Option 3",
                "D. Option 4"
            ],
            "answer": "B. Option 2",
            "explanation": "Short explanation of the correct answer."
        }},
        {{
            "question": "Question 3",
            "options": [
                "A. Option 1",
                "B. Option 2",
                "C. Option 3",
                "D. Option 4"
            ],
            "answer": "C. Option 3",
            "explanation": "Short explanation of the correct answer."
        }}
    ]
}}

Remember:
- EXACTLY 3 questions.
- EXACTLY 4 options per question.
- Only one correct answer.
- Valid JSON only.
"""

    try:
        # Ask Gemini to generate the quiz
        raw_response = generate_text(prompt)

        # Clean Gemini response
        cleaned_response = clean_json_block(raw_response)

        # Convert JSON text into Python dictionary
        quiz = json.loads(cleaned_response)

        # Check questions field
        if "questions" not in quiz:
            raise ValueError(
                "Quiz response does not contain a questions field."
            )

        questions = quiz["questions"]

        # Make sure there are exactly 3 questions
        if len(questions) != 3:
            raise ValueError(
                f"Expected exactly 3 questions, but received {len(questions)}."
            )

        # Validate every question
        for index, question in enumerate(questions, start=1):

            required_fields = [
                "question",
                "options",
                "answer",
                "explanation"
            ]

            for field in required_fields:
                if field not in question:
                    raise ValueError(
                        f"Question {index} is missing '{field}'."
                    )

            # Exactly 4 options
            if len(question["options"]) != 4:
                raise ValueError(
                    f"Question {index} must contain exactly 4 options."
                )

            # Make sure answer is one of the options
            if question["answer"] not in question["options"]:
                raise ValueError(
                    f"Question {index} has an answer that is not in its options."
                )

        return quiz

    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "Gemini returned an invalid quiz format. Please try again."
        ) from exc

    except Exception as exc:
        raise RuntimeError(
            f"Quiz generation failed: {exc}"
        ) from exc