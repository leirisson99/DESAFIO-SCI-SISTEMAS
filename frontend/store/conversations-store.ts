import { create } from "zustand"

import {
  CONVERSATION_TITLE_MAX_LENGTH,
  DEFAULT_CONVERSATION_TITLE,
} from "@/lib/constants"
import { loadConversations, saveConversations } from "@/lib/storage"
import type { Conversation, Message } from "@/types/chat"

interface ConversationsState {
  userKey: string | null
  conversations: Conversation[]
  activeId: string | null
  hydrate: (userKey: string) => void
  createConversation: () => string
  renameConversation: (id: string, title: string) => void
  deleteConversation: (id: string) => void
  appendMessage: (conversationId: string, message: Message) => void
  updateMessage: (
    conversationId: string,
    messageId: string,
    patch: Partial<Message>
  ) => void
  setActive: (id: string | null) => void
}

function persist(userKey: string | null, conversations: Conversation[]) {
  if (!userKey) return
  saveConversations(userKey, conversations)
}

function titleFromMessage(content: string) {
  const trimmed = content.trim()
  if (trimmed.length <= CONVERSATION_TITLE_MAX_LENGTH) return trimmed
  return `${trimmed.slice(0, CONVERSATION_TITLE_MAX_LENGTH)}…`
}

export const useConversationsStore = create<ConversationsState>((set, get) => ({
  userKey: null,
  conversations: [],
  activeId: null,

  hydrate: (userKey) => {
    if (get().userKey === userKey) return
    const conversations = loadConversations(userKey)
    set({ userKey, conversations, activeId: null })
  },

  createConversation: () => {
    const now = Date.now()
    const conversation: Conversation = {
      id: crypto.randomUUID(),
      title: DEFAULT_CONVERSATION_TITLE,
      messages: [],
      createdAt: now,
      updatedAt: now,
    }

    set((state) => {
      const conversations = [conversation, ...state.conversations]
      persist(state.userKey, conversations)
      return { conversations, activeId: conversation.id }
    })

    return conversation.id
  },

  renameConversation: (id, title) => {
    set((state) => {
      const conversations = state.conversations.map((c) =>
        c.id === id ? { ...c, title, updatedAt: Date.now() } : c
      )
      persist(state.userKey, conversations)
      return { conversations }
    })
  },

  deleteConversation: (id) => {
    set((state) => {
      const conversations = state.conversations.filter((c) => c.id !== id)
      persist(state.userKey, conversations)
      const activeId = state.activeId === id ? null : state.activeId
      return { conversations, activeId }
    })
  },

  appendMessage: (conversationId, message) => {
    set((state) => {
      const conversations = state.conversations.map((c) => {
        if (c.id !== conversationId) return c

        const isFirstUserMessage =
          c.title === DEFAULT_CONVERSATION_TITLE && message.role === "user"

        return {
          ...c,
          title: isFirstUserMessage ? titleFromMessage(message.content) : c.title,
          messages: [...c.messages, message],
          updatedAt: Date.now(),
        }
      })
      persist(state.userKey, conversations)
      return { conversations }
    })
  },

  updateMessage: (conversationId, messageId, patch) => {
    set((state) => {
      const conversations = state.conversations.map((c) => {
        if (c.id !== conversationId) return c
        return {
          ...c,
          messages: c.messages.map((m) =>
            m.id === messageId ? { ...m, ...patch } : m
          ),
          updatedAt: Date.now(),
        }
      })
      persist(state.userKey, conversations)
      return { conversations }
    })
  },

  setActive: (id) => set({ activeId: id }),
}))
