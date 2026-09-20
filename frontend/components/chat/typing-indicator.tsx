export function TypingIndicator() {
  return (
    <div className="flex items-center gap-1 px-1 py-2">
      <span className="bg-muted-foreground/50 size-1.5 animate-bounce rounded-full [animation-delay:-0.3s]" />
      <span className="bg-muted-foreground/50 size-1.5 animate-bounce rounded-full [animation-delay:-0.15s]" />
      <span className="bg-muted-foreground/50 size-1.5 animate-bounce rounded-full" />
    </div>
  )
}
