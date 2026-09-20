import type { Conversation } from "@/types/chat"

function storageKey(userKey: string) {
  return `chat:${userKey}:conversations`
}

export function loadConversations(userKey: string): Conversation[] {
  if (typeof window === "undefined") return []

  try {
    const raw = window.localStorage.getItem(storageKey(userKey))
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? (parsed as Conversation[]) : []
  } catch {
    return []
  }
}

export function saveConversations(userKey: string, conversations: Conversation[]) {
  if (typeof window === "undefined") return

  try {
    window.localStorage.setItem(storageKey(userKey), JSON.stringify(conversations))
  } catch {
    // localStorage indisponível (modo privado, cota excedida, etc.) — falha silenciosa
  }
}
