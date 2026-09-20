"use client"

import { useRouter } from "next/navigation"
import { useCallback, useRef, useState } from "react"
import { toast } from "sonner"

import { useConversationActions } from "@/hooks/use-conversations"
import { ChatApiError, sendChatMessage } from "@/lib/chat-api"
import type { Message } from "@/types/chat"

interface PendingRequest {
  userContent: string
  assistantMessageId: string
}

export function useSendMessage(conversationId: string) {
  const router = useRouter()
  const { appendMessage, updateMessage } = useConversationActions()
  const [isSending, setIsSending] = useState(false)
  const lastRequestRef = useRef<PendingRequest | null>(null)

  const runRequest = useCallback(
    async (userContent: string, assistantMessageId: string) => {
      lastRequestRef.current = { userContent, assistantMessageId }
      setIsSending(true)
      updateMessage(conversationId, assistantMessageId, {
        status: "pending",
        content: "",
      })

      try {
        const response = await sendChatMessage(userContent)
        updateMessage(conversationId, assistantMessageId, {
          content: response.answer,
          sources: response.sources,
          status: undefined,
        })
      } catch (error) {
        updateMessage(conversationId, assistantMessageId, { status: "error" })

        if (error instanceof ChatApiError && error.status === 401) {
          toast.error("Sua sessão expirou. Faça login novamente.")
          router.push("/login")
          return
        }

        toast.error("Não foi possível obter resposta. Tente novamente.")
      } finally {
        setIsSending(false)
      }
    },
    [conversationId, updateMessage, router]
  )

  const sendMessage = useCallback(
    (content: string) => {
      const trimmed = content.trim()
      if (!trimmed || isSending) return

      const now = Date.now()
      const userMessage: Message = {
        id: crypto.randomUUID(),
        role: "user",
        content: trimmed,
        createdAt: now,
      }
      appendMessage(conversationId, userMessage)

      const assistantMessageId = crypto.randomUUID()
      appendMessage(conversationId, {
        id: assistantMessageId,
        role: "assistant",
        content: "",
        createdAt: now + 1,
        status: "pending",
      })

      void runRequest(trimmed, assistantMessageId)
    },
    [conversationId, appendMessage, isSending, runRequest]
  )

  const retryLast = useCallback(() => {
    if (!lastRequestRef.current || isSending) return
    void runRequest(
      lastRequestRef.current.userContent,
      lastRequestRef.current.assistantMessageId
    )
  }, [runRequest, isSending])

  return { sendMessage, isSending, retryLast }
}
