interface TypewriterOptions {
  onUpdate: (text: string) => void
  tickMs?: number
  revealFraction?: number
  minChars?: number
}

export interface Typewriter {
  push: (text: string) => void
  finish: (finalText: string) => Promise<void>
  stop: () => void
}

/**
 * Drips buffered text out at a steady cadence instead of dumping it onscreen
 * the instant each network chunk arrives. Reveal speed scales with how much
 * is queued, so it keeps pace with long chunks without lagging behind.
 */
export function createTypewriter({
  onUpdate,
  tickMs = 20,
  revealFraction = 0.25,
  minChars = 1,
}: TypewriterOptions): Typewriter {
  let buffer = ""
  let displayed = ""
  let timer: ReturnType<typeof setInterval> | null = null

  function stop() {
    if (timer) {
      clearInterval(timer)
      timer = null
    }
  }

  function tick() {
    const take = Math.max(minChars, Math.ceil(buffer.length * revealFraction))
    displayed += buffer.slice(0, take)
    buffer = buffer.slice(take)
    onUpdate(displayed)

    if (buffer.length === 0) stop()
  }

  function push(text: string) {
    if (!text) return
    buffer += text
    if (!timer) timer = setInterval(tick, tickMs)
  }

  function finish(finalText: string): Promise<void> {
    return new Promise((resolve) => {
      const waitForDrain = () => {
        if (buffer.length === 0) {
          stop()
          displayed = finalText
          onUpdate(displayed)
          resolve()
          return
        }
        setTimeout(waitForDrain, tickMs)
      }
      waitForDrain()
    })
  }

  return { push, finish, stop }
}
