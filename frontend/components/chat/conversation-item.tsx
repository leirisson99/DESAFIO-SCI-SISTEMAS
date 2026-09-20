"use client"

import { MoreHorizontal, Pencil, Trash2 } from "lucide-react"
import Link from "next/link"
import { useParams, useRouter } from "next/navigation"
import { useState } from "react"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Input } from "@/components/ui/input"
import {
  SidebarMenuAction,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"
import { useConversationActions } from "@/hooks/use-conversations"
import type { Conversation } from "@/types/chat"

export function ConversationItem({ conversation }: { conversation: Conversation }) {
  const router = useRouter()
  const params = useParams<{ conversationId?: string }>()
  const isActive = params.conversationId === conversation.id

  const { renameConversation, deleteConversation } = useConversationActions()
  const [isRenaming, setIsRenaming] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)
  const [title, setTitle] = useState(conversation.title)

  function handleRenameSubmit() {
    const trimmed = title.trim()
    if (trimmed) renameConversation(conversation.id, trimmed)
    setIsRenaming(false)
  }

  function handleDeleteConfirm() {
    deleteConversation(conversation.id)
    setIsDeleting(false)
    if (isActive) router.push("/chat")
  }

  if (isRenaming) {
    return (
      <SidebarMenuItem>
        <Input
          autoFocus
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          onBlur={handleRenameSubmit}
          onKeyDown={(e) => {
            if (e.key === "Enter") handleRenameSubmit()
            if (e.key === "Escape") {
              setTitle(conversation.title)
              setIsRenaming(false)
            }
          }}
          className="h-8"
        />
      </SidebarMenuItem>
    )
  }

  return (
    <SidebarMenuItem>
      <SidebarMenuButton isActive={isActive} render={<Link href={`/chat/${conversation.id}`} />}>
        <span className="truncate">{conversation.title}</span>
      </SidebarMenuButton>

      <DropdownMenu>
        <DropdownMenuTrigger render={<SidebarMenuAction showOnHover />}>
          <MoreHorizontal />
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" side="right">
          <DropdownMenuItem onClick={() => setIsRenaming(true)}>
            <Pencil className="size-4" />
            Renomear
          </DropdownMenuItem>
          <DropdownMenuItem variant="destructive" onClick={() => setIsDeleting(true)}>
            <Trash2 className="size-4" />
            Excluir
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      <Dialog open={isDeleting} onOpenChange={setIsDeleting}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Excluir conversa</DialogTitle>
            <DialogDescription>
              Essa ação não pode ser desfeita. A conversa &quot;{conversation.title}
              &quot; será excluída permanentemente.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsDeleting(false)}>
              Cancelar
            </Button>
            <Button variant="destructive" onClick={handleDeleteConfirm}>
              Excluir
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </SidebarMenuItem>
  )
}
