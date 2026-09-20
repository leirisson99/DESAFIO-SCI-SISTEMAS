"use client"

import { useEffect } from "react"

import { LOCAL_STORAGE_USER_KEY } from "@/lib/constants"
import { useConversationsStore } from "@/store/conversations-store"

export function ConversationsHydrator() {
  const hydrate = useConversationsStore((s) => s.hydrate)

  useEffect(() => {
    hydrate(LOCAL_STORAGE_USER_KEY)
  }, [hydrate])

  return null
}
