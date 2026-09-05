from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import os
import uuid
import shutil

from dotenv import load_dotenv

from services.document_service import extract_text
from services.chunk_service import create_chunks
from services.vector_service import create_vector_store, search_chunks
from services.quiz_service import generate_quiz


load_dotenv()


# ============================================================
# FASTAPI SETUP
# ============================================================

app = FastAPI(
    title="AI Quiz Generator API",
    version="1.0"
)


# React frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# FOLDERS
# ============================================================

UPLOAD_FOLDER = "uploads"
VECTOR_FOLDER = "vector_store"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VECTOR_FOLDER, exist_ok=True)


# ============================================================
# CONFIG
# ============================================================

ALLOWED_EXTENSIONS = {
    ".txt",
    ".pdf",
    ".docx",
    ".jpg",
    ".jpeg",
    ".png"
}


# ============================================================
# REQUEST MODELS
# ============================================================

class SearchRequest(BaseModel):
    document_id: str
    query: str
    top_k: int = 5


class QuizRequest(BaseModel):
    document_id: str
    num_questions: int = 5
    difficulty: str = "medium"


# ============================================================
# HEALTH API
# ============================================================

@app.get("/")
def root():

    return {
        "message": "AI Quiz Generator Backend Running"
    }


@app.get("/health")
def health():

    return {
        "status": "success",
        "message": "Backend is running"
    }


# ============================================================
# UPLOAD DOCUMENT API
# ============================================================

@app.post("/upload-document")
async def upload_document(
    file: UploadFile = File(...)
):

    extension = os.path.splitext(file.filename)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file format. "
                "Supported formats: TXT, PDF, DOCX, JPG, JPEG, PNG"
            )
        )

    document_id = str(uuid.uuid4())

    file_path = os.path.join(
        UPLOAD_FOLDER,
        f"{document_id}{extension}"
    )

    try:

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # ----------------------------------------
        # STEP 1: Extract text
        # ----------------------------------------

        pages = extract_text(file_path)

        total_text = " ".join(page["text"] for page in pages)

        if len(total_text.strip()) < 20:

            raise HTTPException(
                status_code=400,
                detail="No readable text found in document"
            )

        # ----------------------------------------
        # STEP 2: Create chunks
        # ----------------------------------------

        chunks = create_chunks(
            pages=pages,
            document_id=document_id,
            filename=file.filename,
            chunk_size=1000,
            overlap=200
        )

        if not chunks:

            raise HTTPException(
                status_code=400,
                detail="Could not create chunks from document"
            )

        # ----------------------------------------
        # STEP 3: Generate embeddings
        # STEP 4: Store in FAISS
        # ----------------------------------------

        total_chunks = create_vector_store(chunks, document_id)

        return {
            "message": "Document processed successfully",
            "document_id": document_id,
            "filename": file.filename,
            "pages_processed": len(pages),
            "chunks_created": total_chunks
        }

    except HTTPException:
        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ============================================================
# RETRIEVAL / SEARCH API
# ============================================================

@app.post("/search-document")
def search_document(
    request: SearchRequest
):

    if not request.query.strip():

        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty"
        )

    try:

        results = search_chunks(
            document_id=request.document_id,
            query=request.query,
            top_k=request.top_k
        )

        return {
            "document_id": request.document_id,
            "query": request.query,
            "results_count": len(results),
            "results": results
        }

    except ValueError as error:

        raise HTTPException(status_code=404, detail=str(error))

    except Exception as error:

        raise HTTPException(status_code=500, detail=str(error))


# ============================================================
# QUIZ GENERATION API
# ============================================================

@app.post("/generate-quiz")
def generate_quiz_endpoint(
    request: QuizRequest
):

    if request.num_questions < 1 or request.num_questions > 20:

        raise HTTPException(
            status_code=400,
            detail="num_questions must be between 1 and 20"
        )

    try:

        questions = generate_quiz(
            document_id=request.document_id,
            num_questions=request.num_questions,
            difficulty=request.difficulty
        )

        return {
            "document_id": request.document_id,
            "num_questions": len(questions),
            "difficulty": request.difficulty,
            "questions": questions
        }

    except ValueError as error:

        raise HTTPException(status_code=400, detail=str(error))

    except Exception as error:

        raise HTTPException(status_code=500, detail=str(error))


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
