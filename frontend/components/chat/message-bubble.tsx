"use client"

import { Bot, RotateCcw, User } from "lucide-react"

import { SourceCitations } from "@/components/chat/source-citations"
import { TypingIndicator } from "@/components/chat/typing-indicator"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import type { Message } from "@/types/chat"

export function MessageBubble({
  message,
  onRetry,
}: {
  message: Message
  onRetry?: () => void
}) {
  const isUser = message.role === "user"

  return (
    <div className={cn("flex gap-3", isUser && "justify-end")}>
      {!isUser && (
        <Avatar className="size-8 shrink-0">
          <AvatarFallback>
            <Bot className="size-4" />
          </AvatarFallback>
        </Avatar>
      )}

      <div className={cn("flex max-w-[75%] flex-col", isUser && "items-end")}>
        <div
          className={cn(
            "rounded-2xl px-3.5 py-2 text-sm",
            isUser ? "bg-primary text-primary-foreground" : "bg-muted"
          )}
        >
          {message.status === "pending" ? (
            <TypingIndicator />
          ) : (
            <p className="whitespace-pre-wrap">{message.content}</p>
          )}
        </div>

        {message.status === "error" && (
          <Button
            variant="ghost"
            size="sm"
            className="text-destructive mt-1 gap-1.5"
            onClick={onRetry}
          >
            <RotateCcw className="size-3.5" />
            Tentar novamente
          </Button>
        )}

        {!isUser && message.sources && message.sources.length > 0 && (
          <SourceCitations sources={message.sources} />
        )}
      </div>

      {isUser && (
        <Avatar className="size-8 shrink-0">
          <AvatarFallback>
            <User className="size-4" />
          </AvatarFallback>
        </Avatar>
      )}
    </div>
  )
}
