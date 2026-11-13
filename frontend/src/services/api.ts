import type { ChatResponse } from "../types/chat";
import type { Document } from "../types/document";

const API_BASE_URL = "http://127.0.0.1:8000";

export async function uploadDocument(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(
    `${API_BASE_URL}/documents/upload`,
    {
      method: "POST",
      body: formData,
    }
  );

  if (!response.ok) {
    throw new Error("Document upload failed");
  }

  return response.json();
}

export async function askQuestion(
  question: string
): Promise<ChatResponse> {
  const response = await fetch(
    `${API_BASE_URL}/chat/ask`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        query: question,
        top_k: 5,
      }),
    }
  );

  if (!response.ok) {
    throw new Error("Failed to generate answer");
  }

  return response.json();
}

export async function getDocuments(): Promise<Document[]> {
  const response = await fetch(`${API_BASE_URL}/documents`);

  if (!response.ok) {
    throw new Error("Failed to fetch documents");
  }

  return response.json();
}

export async function deleteDocument(id: number): Promise<void> {
  const response = await fetch(
    `${API_BASE_URL}/documents/${id}`,
    {
      method: "DELETE",
    }
  );

  if (!response.ok) {
    throw new Error("Failed to delete document");
  }
}
