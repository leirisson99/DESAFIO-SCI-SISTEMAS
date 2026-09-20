import { NextResponse } from "next/server"
import { z } from "zod"

import { auth } from "@/auth"
import { CHAT_API_TIMEOUT_MS } from "@/lib/constants"

const chatRequestSchema = z.object({
  message: z.string().min(1),
})

const sourceSchema = z.object({
  content: z.string(),
  similarity: z.number(),
})

const chatResponseSchema = z.object({
  answer: z.string(),
  sources: z.array(sourceSchema),
})

export async function POST(request: Request) {
  const session = await auth()
  if (!session?.user) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 })
  }

  const body = await request.json().catch(() => null)
  const parsed = chatRequestSchema.safeParse(body)
  if (!parsed.success) {
    return NextResponse.json({ error: "invalid_request" }, { status: 400 })
  }

  const backendUrl = process.env.BACKEND_API_URL
  if (!backendUrl) {
    return NextResponse.json({ error: "backend_not_configured" }, { status: 500 })
  }

  try {
    const backendResponse = await fetch(`${backendUrl}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: parsed.data.message }),
      signal: AbortSignal.timeout(CHAT_API_TIMEOUT_MS),
    })

    if (!backendResponse.ok) {
      return NextResponse.json(
        { error: "backend_error" },
        { status: backendResponse.status === 422 ? 422 : 502 }
      )
    }

    const data = await backendResponse.json().catch(() => null)
    const parsedResponse = chatResponseSchema.safeParse(data)
    if (!parsedResponse.success) {
      return NextResponse.json({ error: "backend_invalid_response" }, { status: 502 })
    }

    return NextResponse.json(parsedResponse.data)
  } catch {
    return NextResponse.json({ error: "backend_unreachable" }, { status: 502 })
  }
}
