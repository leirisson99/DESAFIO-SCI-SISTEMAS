"use client"

import { useEffect, useRef } from "react"

import { MessageBubble } from "@/components/chat/message-bubble"
import { ScrollArea } from "@/components/ui/scroll-area"
import type { Message } from "@/types/chat"

export function ChatMessages({
  messages,
  onRetry,
}: {
  messages: Message[]
  onRetry: () => void
}) {
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  return (
    <ScrollArea className="flex-1">
      <div className="mx-auto flex max-w-3xl flex-col gap-6 p-4" aria-live="polite">
        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message}
            onRetry={message.status === "error" ? onRetry : undefined}
          />
        ))}
        <div ref={bottomRef} />
      </div>
    </ScrollArea>
  )
}
