import type { Source } from "@/types/chat"

export class ChatApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

type StreamEvent =
  | { type: "delta"; text: string }
  | { type: "done"; sources: Source[] }
  | { type: "error"; message: string }

interface StreamChatMessageResult {
  answer: string
  sources: Source[]
}

export async function streamChatMessage(
  message: string,
  onDelta: (text: string) => void
): Promise<StreamChatMessageResult> {
  const response = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  })

  if (!response.ok || !response.body) {
    throw new ChatApiError(
      response.status,
      "Não foi possível obter resposta do assistente."
    )
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ""
  let answer = ""
  let sources: Source[] = []

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const frames = buffer.split("\n\n")
    buffer = frames.pop() ?? ""

    for (const frame of frames) {
      const line = frame.trim()
      if (!line.startsWith("data:")) continue

      const payload = line.slice("data:".length).trim()
      if (!payload) continue

      const event = JSON.parse(payload) as StreamEvent

      if (event.type === "delta") {
        answer += event.text
        onDelta(event.text)
      } else if (event.type === "done") {
        sources = event.sources
      } else if (event.type === "error") {
        throw new ChatApiError(502, event.message)
      }
    }
  }

  return { answer, sources }
}
