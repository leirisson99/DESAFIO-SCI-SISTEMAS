export interface Source {
  content: string
  similarity: number
}

export type MessageStatus = "pending" | "error"

export interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  createdAt: number
  sources?: Source[]
  status?: MessageStatus
}

export interface Conversation {
  id: string
  title: string
  messages: Message[]
  createdAt: number
  updatedAt: number
}
