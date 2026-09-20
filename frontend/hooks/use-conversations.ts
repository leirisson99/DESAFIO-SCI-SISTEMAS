import { useConversationsStore } from "@/store/conversations-store"

export function useConversationList() {
  return useConversationsStore((s) =>
    [...s.conversations].sort((a, b) => b.updatedAt - a.updatedAt)
  )
}

export function useConversation(id: string | undefined) {
  return useConversationsStore((s) =>
    id ? s.conversations.find((c) => c.id === id) : undefined
  )
}

export function useActiveConversationId() {
  return useConversationsStore((s) => s.activeId)
}

export function useConversationActions() {
  return useConversationsStore((s) => ({
    createConversation: s.createConversation,
    renameConversation: s.renameConversation,
    deleteConversation: s.deleteConversation,
    appendMessage: s.appendMessage,
    updateMessage: s.updateMessage,
    setActive: s.setActive,
  }))
}
