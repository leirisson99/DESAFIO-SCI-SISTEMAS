import type { ChatApiResponse } from "@/types/chat"

export class ChatApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

export async function sendChatMessage(message: string): Promise<ChatApiResponse> {
  const response = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  })

  if (!response.ok) {
    throw new ChatApiError(
      response.status,
      "Não foi possível obter resposta do assistente."
    )
  }

  return response.json() as Promise<ChatApiResponse>
}
