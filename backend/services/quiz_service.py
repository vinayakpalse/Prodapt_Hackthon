import json
import os
import re

import google.generativeai as genai

from services.vector_service import load_chunks


GEMINI_MODEL = "gemini-3.6-flash"

_configured = False


def _ensure_configured():

    global _configured

    if _configured:
        return

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not set. Add it to your .env file."
        )

    genai.configure(api_key=api_key)

    _configured = True


def _build_context(document_id, max_chars=8000):

    chunks = load_chunks(document_id)

    if not chunks:
        raise ValueError("No content available for this document")

    # Evenly sample chunks across the document so the quiz covers
    # the whole document instead of just the first chunks.
    total_chars = sum(len(chunk["text"]) for chunk in chunks)

    if total_chars <= max_chars:
        selected = chunks

    else:
        step = max(1, len(chunks) // max(1, max_chars // 500))
        selected = chunks[::step]

    context = "\n\n".join(chunk["text"] for chunk in selected)

    return context[:max_chars]


def _extract_json(raw_text):

    text = raw_text.strip()

    # Strip markdown code fences if present
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    return json.loads(text)


def generate_quiz(document_id, num_questions=5, difficulty="medium"):

    _ensure_configured()

    context = _build_context(document_id)

    prompt = f"""You are a quiz generator. Based ONLY on the document
content below, create {num_questions} multiple-choice questions at
{difficulty} difficulty.

Return STRICT JSON only (no markdown, no commentary) in this exact
shape:

[
  {{
    "question": "string",
    "options": ["string", "string", "string", "string"],
    "correct_answer": "string (must exactly match one of the options)",
    "explanation": "string (why the correct answer is right)",
    "wrong_feedback": {{
      "<incorrect option text>": "string (why this specific option is wrong)"
    }},
    "hints": ["string (subtle hint, does not reveal the answer)", "string (bigger hint, still does not reveal the answer)"]
  }}
]

Rules:
- "wrong_feedback" must contain exactly one entry for every option that is
  NOT the correct_answer, keyed by the exact option text.
- Provide exactly 2 "hints" per question, ordered from subtle to more
  revealing. Never state the answer in a hint.

Document content:
\"\"\"
{context}
\"\"\"
"""

    model = genai.GenerativeModel(GEMINI_MODEL)

    # response_mime_type skips markdown-fence wrapping so the model can
    # return JSON directly, and a lower temperature keeps generation fast
    # and deterministic for a structured task like this.
    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.4,
            "response_mime_type": "application/json",
        },
    )

    try:
        questions = _extract_json(response.text)

    except (json.JSONDecodeError, AttributeError) as error:
        raise ValueError(
            f"Failed to parse quiz response from model: {error}"
        )

    return questions
