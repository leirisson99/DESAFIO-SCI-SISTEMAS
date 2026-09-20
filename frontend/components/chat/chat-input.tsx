"use client"

import { SendHorizontal } from "lucide-react"
import { useState } from "react"

import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { useAutoResizeTextarea } from "@/hooks/use-auto-resize-textarea"

export function ChatInput({
  onSend,
  disabled,
}: {
  onSend: (message: string) => void
  disabled?: boolean
}) {
  const [value, setValue] = useState("")
  const textareaRef = useAutoResizeTextarea(value)

  function handleSubmit() {
    const trimmed = value.trim()
    if (!trimmed || disabled) return
    onSend(trimmed)
    setValue("")
  }

  return (
    <div className="flex items-end gap-2 border-t p-4">
      <Textarea
        ref={textareaRef}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault()
            handleSubmit()
          }
        }}
        placeholder="Digite sua mensagem..."
        rows={1}
        disabled={disabled}
        className="max-h-50 min-h-10 resize-none"
      />
      <Button
        size="icon"
        onClick={handleSubmit}
        disabled={disabled || !value.trim()}
        aria-label="Enviar mensagem"
      >
        <SendHorizontal className="size-4" />
      </Button>
    </div>
  )
}
