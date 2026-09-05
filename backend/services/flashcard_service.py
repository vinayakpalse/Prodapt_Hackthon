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

    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    return json.loads(text)


def generate_flashcards(document_id, num_cards=10):

    _ensure_configured()

    context = _build_context(document_id)

    prompt = f"""You are an AI educational assistant.

Based ONLY on the document content below, create {num_cards}
useful flashcards for a student.

Rules:
- Generate exactly {num_cards} flashcards.
- Each flashcard should focus on one important concept.
- The front should contain a clear question.
- The back should contain a concise and accurate answer.
- Include the topic.
- Avoid duplicate questions.
- Use ONLY information from the document.
- Do not use outside knowledge.

Return STRICT JSON only in this exact shape:

[
  {{
    "front": "string",
    "back": "string",
    "topic": "string"
  }}
]

Document content:
\"\"\"
{context}
\"\"\"
"""

    model = genai.GenerativeModel(GEMINI_MODEL)

    response = model.generate_content(prompt)

    try:
        flashcards = _extract_json(response.text)

    except (json.JSONDecodeError, AttributeError) as error:
        raise ValueError(
            f"Failed to parse flashcard response from model: {error}"
        )

    return flashcards