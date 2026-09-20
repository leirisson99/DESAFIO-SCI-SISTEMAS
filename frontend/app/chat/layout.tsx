import { ChatSidebar } from "@/components/chat/chat-sidebar"
import { ConversationsHydrator } from "@/components/chat/conversations-hydrator"
import { AppHeader } from "@/components/layout/app-header"
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar"

export default function ChatLayout({ children }: LayoutProps<"/chat">) {
  return (
    <SidebarProvider>
      <ConversationsHydrator />
      <ChatSidebar />
      <SidebarInset>
        <AppHeader />
        <div className="flex flex-1 flex-col overflow-hidden">{children}</div>
      </SidebarInset>
    </SidebarProvider>
  )
}
