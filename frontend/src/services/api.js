export const API_URL =
  import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_URL}/documents/upload`, {
    method: "POST",
    body: formData,
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : "Document upload failed"
    );
  }

  return data;
}

export async function askQuestion(question, topK = 3) {
  const response = await fetch(`${API_URL}/rag/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question,
      top_k: topK,
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : "Unable to generate an answer"
    );
  }

  return data;
}


export async function getDocuments() {
  const response = await fetch(`${API_URL}/documents/`);

  if (!response.ok) {
    throw new Error("Unable to load documents");
  }

  return response.json();
}

export async function deleteDocument(documentId) {
  const response = await fetch(
    `${API_URL}/documents/${documentId}`,
    {
      method: "DELETE",
    }
  );

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));

    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : "Unable to delete document"
    );
  }

  return response.json();
}