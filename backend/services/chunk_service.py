import re


def clean_text(text: str) -> str:
    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def create_chunks(
    pages,
    document_id,
    filename,
    chunk_size=1000,
    overlap=200
):
    chunks = []
    chunk_id = 0

    for page in pages:
        text = clean_text(page["text"])

        if not text:
            continue

        start = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk_text = text[start:end]

            if len(chunk_text.strip()) > 20:
                chunks.append(
                    {
                        "chunk_id": chunk_id,
                        "document_id": document_id,
                        "filename": filename,
                        "page": page["page"],
                        "text": chunk_text
                    }
                )
                chunk_id += 1

            if end == len(text):
                break

            start += chunk_size - overlap

    return chunks


def chunk_pages(pages, document_id="default", filename="document", chunk_size=1000, overlap=200):
    """Alias for create_chunks to support standard chunking interfaces."""
    return create_chunks(
        pages=pages,
        document_id=document_id,
        filename=filename,
        chunk_size=chunk_size,
        overlap=overlap,
    )
