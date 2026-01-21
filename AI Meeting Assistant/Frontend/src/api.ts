// src/api.ts
export async function sendToRAG(message: string): Promise<string> {
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/rag/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });

    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }

    const data = await res.json();
    return data.answer;
  } catch (err) {
    console.error("Error sending to RAG:", err);
    return "Sorry, could not reach the backend.";
  }
}
