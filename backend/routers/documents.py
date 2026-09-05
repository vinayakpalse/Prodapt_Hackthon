from datetime import datetime, timezone
from pathlib import Path

from bson import ObjectId
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from backend.core.config import settings
from backend.database.database import get_db
from backend.schemas.document import DocumentPublic
from backend.utils.ownership import parse_object_id
from backend.core.dependencies import get_current_user_id

router = APIRouter(prefix="/api/documents", tags=["documents"])


def _public(doc: dict) -> DocumentPublic:
    return DocumentPublic(
        id=str(doc["_id"]),
        title=doc["title"],
        createdAt=doc["createdAt"],
        updatedAt=doc["updatedAt"],
    )


@router.get("", response_model=list[DocumentPublic])
def list_documents(user_id: str = Depends(get_current_user_id)):
    docs = get_db().documents.find({"userId": ObjectId(user_id)}).sort("createdAt", -1)
    return [_public(d) for d in docs]


@router.get("/{document_id}", response_model=DocumentPublic)
def get_document(document_id: str, user_id: str = Depends(get_current_user_id)):
    oid = parse_object_id(document_id, "documentId")
    doc = get_db().documents.find_one({"_id": oid, "userId": ObjectId(user_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return _public(doc)


@router.post("", response_model=DocumentPublic)
def upload_document(file: UploadFile = File(...), user_id: str = Depends(get_current_user_id)):
    from services.document_service import extract_text
    from services.chunk_service import chunk_pages
    from services.vector_service import store_chunks

    if not file.filename:
        raise HTTPException(status_code=400, detail="A file is required")
    data = file.file.read()
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(data) > max_bytes:
        raise HTTPException(status_code=400, detail=f"File exceeds {settings.max_upload_mb} MB")

    title = Path(file.filename).stem or "Untitled notes"
    now = datetime.now(timezone.utc)
    db = get_db()
    inserted = db.documents.insert_one(
        {
            "userId": ObjectId(user_id),
            "title": title,
            "originalFilename": file.filename,
            "createdAt": now,
            "updatedAt": now,
        }
    )
    document_id = str(inserted.inserted_id)

    upload_root = Path(settings.upload_dir)
    upload_root.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename).suffix.lower() or ".bin"
    saved = upload_root / f"{document_id}{suffix}"
    saved.write_bytes(data)

    try:
        extracted = extract_text(str(saved))
        pages = extracted[1] if isinstance(extracted, tuple) else extracted
        chunks = chunk_pages(pages, document_id=document_id, filename=file.filename)
        store_chunks(document_id, chunks)
    except HTTPException:
        db.documents.delete_one({"_id": inserted.inserted_id})
        saved.unlink(missing_ok=True)
        raise
    except Exception as exc:
        db.documents.delete_one({"_id": inserted.inserted_id})
        saved.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="Failed to process this document.") from exc

    db.documents.update_one(
        {"_id": inserted.inserted_id},
        {"$set": {"updatedAt": datetime.now(timezone.utc), "chunkCount": len(chunks)}},
    )
    doc = db.documents.find_one({"_id": inserted.inserted_id})
    return _public(doc)
