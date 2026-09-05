import faiss
import pickle
import os

from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


VECTOR_FOLDER = "vector_store"

os.makedirs(VECTOR_FOLDER, exist_ok=True)


def _index_path(document_id):
    return os.path.join(VECTOR_FOLDER, f"{document_id}.faiss")


def _metadata_path(document_id):
    return os.path.join(VECTOR_FOLDER, f"{document_id}_metadata.pkl")


def create_vector_store(chunks, document_id):

    if not chunks:
        raise ValueError("No chunks available for vector storage")

    texts = [chunk["text"] for chunk in chunks]

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    embeddings = embeddings.astype("float32")

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)

    index.add(embeddings)

    faiss.write_index(index, _index_path(document_id))

    with open(_metadata_path(document_id), "wb") as file:
        pickle.dump(chunks, file)

    return len(chunks)


def store_chunks(document_id, chunks):
    """Alias for create_vector_store."""
    return create_vector_store(chunks, document_id)


def load_chunks(document_id):

    metadata_path = _metadata_path(document_id)

    if not os.path.exists(metadata_path):
        raise ValueError("Document not found")

    with open(metadata_path, "rb") as file:
        return pickle.load(file)


def search_chunks(document_id, query, top_k=5):

    index_path = _index_path(document_id)
    metadata_path = _metadata_path(document_id)

    if not os.path.exists(index_path) or not os.path.exists(metadata_path):
        raise ValueError("Document not found")

    index = faiss.read_index(index_path)

    with open(metadata_path, "rb") as file:
        chunks = pickle.load(file)

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    query_embedding = query_embedding.astype("float32")

    actual_top_k = min(top_k, len(chunks))

    scores, indices = index.search(query_embedding, actual_top_k)

    results = []

    for score, index_id in zip(scores[0], indices[0]):

        if index_id == -1:
            continue

        chunk = chunks[index_id]

        results.append(
            {
                "chunk_id": chunk["chunk_id"],
                "document_id": chunk["document_id"],
                "filename": chunk["filename"],
                "page": chunk["page"],
                "text": chunk["text"],
                "score": float(score)
            }
        )

    return results
