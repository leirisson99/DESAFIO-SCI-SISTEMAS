"use client"

import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip"
import type { Source } from "@/types/chat"

export function SourceCitations({ sources }: { sources: Source[] }) {
  if (sources.length === 0) return null

  return (
    <div className="mt-1.5 flex flex-wrap items-center gap-1">
      {sources.map((source, index) => (
        <Tooltip key={index}>
          <TooltipTrigger
            className="bg-accent text-accent-foreground hover:bg-primary hover:text-primary-foreground flex size-5 shrink-0 items-center justify-center rounded-full text-[11px] font-medium transition-colors"
            aria-label={`Ver fonte ${index + 1}`}
          >
            {index + 1}
          </TooltipTrigger>
          <TooltipContent className="w-80 max-w-sm flex-col items-start gap-0.5 bg-popover text-popover-foreground border p-3">
            <span className="text-muted-foreground text-[11px]">
              Fonte {index + 1}
            </span>
            <span className="text-muted-foreground text-[11px]">
              {Math.round(source.similarity * 100)}% similaridade
            </span>
            <p className="line-clamp-6 mt-1.5 text-xs whitespace-pre-wrap">
              {source.content}
            </p>
          </TooltipContent>
        </Tooltip>
      ))}
    </div>
  )
}
