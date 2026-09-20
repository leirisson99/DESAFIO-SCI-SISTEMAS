import { useMemo } from "react"
import { useShallow } from "zustand/react/shallow"

import { useConversationsStore } from "@/store/conversations-store"

export function useConversationList() {
  const conversations = useConversationsStore((s) => s.conversations)
  return useMemo(
    () => [...conversations].sort((a, b) => b.updatedAt - a.updatedAt),
    [conversations]
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
  return useConversationsStore(
    useShallow((s) => ({
      createConversation: s.createConversation,
      renameConversation: s.renameConversation,
      deleteConversation: s.deleteConversation,
      appendMessage: s.appendMessage,
      updateMessage: s.updateMessage,
      setActive: s.setActive,
    }))
  )
}
