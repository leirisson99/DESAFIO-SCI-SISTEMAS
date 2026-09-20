"use client"

import { MessageCircle, Plus } from "lucide-react"
import { useRouter } from "next/navigation"

import { Button } from "@/components/ui/button"
import { useConversationActions } from "@/hooks/use-conversations"

export function EmptyState() {
  const router = useRouter()
  const { createConversation } = useConversationActions()

  function handleNewConversation() {
    const id = createConversation()
    router.push(`/chat/${id}`)
  }

  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-4 p-6 text-center">
      <MessageCircle className="text-muted-foreground size-10" />
      <div className="space-y-1">
        <p className="text-lg font-medium">Nenhuma conversa selecionada</p>
        <p className="text-muted-foreground text-sm">
          Inicie uma nova conversa para falar com o assistente.
        </p>
      </div>
      <Button onClick={handleNewConversation} className="gap-2">
        <Plus className="size-4" />
        Nova conversa
      </Button>
    </div>
  )
}
