import os
import sys
import uuid
import shutil
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Ensure backend directory is in sys.path for direct service imports
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from backend.core.config import settings
from backend.database.database import init_db
from backend.routers.auth import router as auth_router
from backend.routers.documents import router as documents_router

load_dotenv()


# ============================================================
# LIFESPAN & FASTAPI SETUP
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure MongoDB indexes on application startup
    try:
        init_db()
    except Exception:
        pass
    yield


app = FastAPI(
    title="AI Quiz Generator & Auth API",
    description="Production-ready FastAPI backend with MongoDB, JWT authentication, refresh token rotation, document processing, and AI quiz generation.",
    version="1.0.0",
    lifespan=lifespan,
    swagger_ui_parameters={"persistAuthorization": True},
)

# React frontend CORS connection
cors_origins = list(settings.CORS_ORIGINS)
for origin in ["http://localhost:5173", "http://localhost:3000"]:
    if origin not in cors_origins:
        cors_origins.append(origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Authentication & Document Routers
app.include_router(auth_router)
app.include_router(documents_router)


# ============================================================
# FOLDERS & CONFIG
# ============================================================

UPLOAD_FOLDER = os.path.join(str(BACKEND_DIR), "uploads")
VECTOR_FOLDER = os.path.join(str(BACKEND_DIR), "vector_store")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(VECTOR_FOLDER, exist_ok=True)

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
# HEALTH APIS
# ============================================================

@app.get("/", tags=["Health"])
def root():
    return {
        "status": "online",
        "service": "AI Quiz Generator & Auth API",
        "database": "MongoDB",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
def health():
    return {
        "status": "success",
        "message": "Backend is running"
    }


# ============================================================
# UPLOAD DOCUMENT API
# ============================================================

@app.post("/upload-document", tags=["Documents"])
async def upload_document(
    file: UploadFile = File(...)
):
    from services.document_service import extract_text
    from services.chunk_service import create_chunks
    from services.vector_service import create_vector_store

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

        # STEP 1: Extract text
        pages = extract_text(file_path)
        total_text = " ".join(page["text"] for page in pages)

        if len(total_text.strip()) < 20:
            raise HTTPException(
                status_code=400,
                detail="No readable text found in document"
            )

        # STEP 2: Create chunks
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

        # STEP 3 & 4: Generate embeddings & store in FAISS
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

@app.post("/search-document", tags=["Documents"])
def search_document(
    request: SearchRequest
):
    from services.vector_service import search_chunks

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

@app.post("/generate-quiz", tags=["Quiz"])
def generate_quiz_endpoint(
    request: QuizRequest
):
    from services.quiz_service import generate_quiz

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
