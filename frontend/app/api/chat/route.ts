import { NextResponse } from "next/server"
import { z } from "zod"

import { CHAT_API_TIMEOUT_MS } from "@/lib/constants"

const chatRequestSchema = z.object({
  message: z.string().min(1),
})

export async function POST(request: Request) {
  const body = await request.json().catch(() => null)
  const parsed = chatRequestSchema.safeParse(body)
  if (!parsed.success) {
    return NextResponse.json({ error: "invalid_request" }, { status: 400 })
  }

  const backendUrl = process.env.BACKEND_API_URL
  if (!backendUrl) {
    return NextResponse.json({ error: "backend_not_configured" }, { status: 500 })
  }

  let backendResponse: Response
  try {
    backendResponse = await fetch(`${backendUrl}/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: parsed.data.message }),
      signal: AbortSignal.timeout(CHAT_API_TIMEOUT_MS),
    })
  } catch {
    return NextResponse.json({ error: "backend_unreachable" }, { status: 502 })
  }

  if (!backendResponse.ok || !backendResponse.body) {
    return NextResponse.json(
      { error: "backend_error" },
      { status: backendResponse.status === 422 ? 422 : 502 }
    )
  }

  return new Response(backendResponse.body, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache, no-transform",
      "X-Accel-Buffering": "no",
      Connection: "keep-alive",
    },
  })
}
