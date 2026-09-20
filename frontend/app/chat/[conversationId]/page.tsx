"use client"

import { useParams } from "next/navigation"
import { useEffect } from "react"

import { ChatInput } from "@/components/chat/chat-input"
import { ChatMessages } from "@/components/chat/chat-messages"
import { EmptyState } from "@/components/chat/empty-state"
import { useConversation, useConversationActions } from "@/hooks/use-conversations"
import { useSendMessage } from "@/hooks/use-send-message"

export default function ConversationPage() {
  const params = useParams<{ conversationId: string }>()
  const conversationId = params.conversationId
  const conversation = useConversation(conversationId)
  const { setActive } = useConversationActions()
  const { sendMessage, isSending, retryLast } = useSendMessage(conversationId)

  useEffect(() => {
    setActive(conversationId)
    return () => setActive(null)
  }, [conversationId, setActive])

  if (!conversation) {
    return <EmptyState />
  }

  return (
    <>
      <ChatMessages messages={conversation.messages} onRetry={retryLast} />
      <ChatInput onSend={sendMessage} disabled={isSending} />
    </>
  )
}
