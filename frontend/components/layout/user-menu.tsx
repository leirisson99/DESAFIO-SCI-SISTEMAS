"use client"

import { LogOut } from "lucide-react"
import { signOut, useSession } from "next-auth/react"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

export function UserMenu() {
  const { data: session } = useSession()
  const user = session?.user

  if (!user) return null

  const initials = (user.name ?? user.email ?? "?").slice(0, 2).toUpperCase()

  return (
    <DropdownMenu>
      <DropdownMenuTrigger render={<Button variant="ghost" className="gap-2 px-2" />}>
        <Avatar className="size-7">
          <AvatarImage src={user.image ?? undefined} alt={user.name ?? ""} />
          <AvatarFallback>{initials}</AvatarFallback>
        </Avatar>
        <span className="hidden text-sm font-medium sm:inline">{user.name}</span>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuLabel className="truncate">{user.email}</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={() => signOut({ redirectTo: "/login" })}>
          <LogOut className="size-4" />
          Sair
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
