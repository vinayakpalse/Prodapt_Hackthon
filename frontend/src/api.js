const API_BASE = "http://localhost:8000";

async function handleResponse(response) {
  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Request failed");
  }

  return data;
}

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE}/upload-document`, {
    method: "POST",
    body: formData,
  });

  return handleResponse(response);
}

export async function generateQuiz(documentId, numQuestions, difficulty) {
  const response = await fetch(`${API_BASE}/generate-quiz`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      document_id: documentId,
      num_questions: numQuestions,
      difficulty,
    }),
  });

  return handleResponse(response);
}
