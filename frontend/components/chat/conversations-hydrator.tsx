"use client"

import { useEffect } from "react"
import { useSession } from "next-auth/react"

import { useConversationsStore } from "@/store/conversations-store"

export function ConversationsHydrator() {
  const { data: session, status } = useSession()
  const hydrate = useConversationsStore((s) => s.hydrate)

  const userKey = session?.user?.id ?? session?.user?.email ?? null

  useEffect(() => {
    if (status !== "authenticated" || !userKey) return
    hydrate(userKey)
  }, [status, userKey, hydrate])

  return null
}
