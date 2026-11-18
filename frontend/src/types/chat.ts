export interface ChatSource {
  filename: string;
  chunk_index: number;
  similarity: number;
}

export interface ChatResponse {
  answer: string;
  sources: ChatSource[];
  conversation_id: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sources?: ChatSource[];
}
