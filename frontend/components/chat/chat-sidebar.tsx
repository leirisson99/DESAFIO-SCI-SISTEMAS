"use client"

import { Plus } from "lucide-react"
import { useRouter } from "next/navigation"

import { ConversationItem } from "@/components/chat/conversation-item"
import { Button } from "@/components/ui/button"
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarMenu,
} from "@/components/ui/sidebar"
import { useConversationActions, useConversationList } from "@/hooks/use-conversations"

export function ChatSidebar() {
  const router = useRouter()
  const conversations = useConversationList()
  const { createConversation } = useConversationActions()

  function handleNewConversation() {
    const id = createConversation()
    router.push(`/chat/${id}`)
  }

  return (
    <Sidebar>
      <SidebarHeader>
        <Button className="w-full justify-start gap-2" onClick={handleNewConversation}>
          <Plus className="size-4" />
          Nova conversa
        </Button>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              {conversations.map((conversation) => (
                <ConversationItem key={conversation.id} conversation={conversation} />
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  )
}
