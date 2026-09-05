import os
import pymupdf
import pytesseract

from docx import Document
from PIL import Image


# ============================================================
# MAIN TEXT EXTRACTION FUNCTION
# ============================================================

def extract_text(file_path: str) -> list[dict]:

    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".txt":
        return extract_txt(file_path)

    elif extension == ".pdf":
        return extract_pdf(file_path)

    elif extension == ".docx":
        return extract_docx(file_path)

    elif extension in [".jpg", ".jpeg", ".png"]:
        return extract_image(file_path)

    else:
        raise ValueError("Unsupported file format")


# ============================================================
# TXT
# ============================================================

def extract_txt(file_path):

    with open(
        file_path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as file:

        text = file.read()

    return [
        {
            "text": text,
            "page": 1
        }
    ]


# ============================================================
# PDF
# ============================================================

def extract_pdf(file_path):

    document = pymupdf.open(file_path)

    pages = []

    try:

        for page_number, page in enumerate(document):

            # First try normal PDF text extraction
            text = page.get_text("text")

            # ------------------------------------------------
            # OCR FALLBACK
            # ------------------------------------------------
            # If very little text was extracted,
            # assume that the page may be scanned.
            # ------------------------------------------------

            if len(text.strip()) < 20:

                # Render page at higher resolution
                # for better OCR accuracy
                matrix = pymupdf.Matrix(2, 2)

                pix = page.get_pixmap(
                    matrix=matrix,
                    alpha=False
                )

                image = Image.frombytes(
                    "RGB",
                    [pix.width, pix.height],
                    pix.samples
                )

                text = pytesseract.image_to_string(
                    image
                )

                image.close()

            pages.append(
                {
                    "text": text,
                    "page": page_number + 1
                }
            )

    finally:

        document.close()

    return pages


# ============================================================
# DOCX
# ============================================================

def extract_docx(file_path):

    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:

        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    full_text = "\n".join(paragraphs)

    return [
        {
            "text": full_text,
            "page": 1
        }
    ]


# ============================================================
# IMAGE
# ============================================================

def extract_image(file_path):

    with Image.open(file_path) as image:

        # Convert to RGB for consistent OCR processing
        image = image.convert("RGB")

        text = pytesseract.image_to_string(
            image
        )

    return [
        {
            "text": text,
            "page": 1
        }
    ]