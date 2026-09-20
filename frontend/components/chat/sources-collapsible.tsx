"use client"

import { ChevronDown } from "lucide-react"

import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible"
import type { Source } from "@/types/chat"

export function SourcesCollapsible({ sources }: { sources: Source[] }) {
  if (sources.length === 0) return null

  return (
    <Collapsible className="mt-2">
      <CollapsibleTrigger className="group text-muted-foreground hover:text-foreground flex items-center gap-1 text-xs">
        <ChevronDown className="size-3 transition-transform group-data-[panel-open]:rotate-180" />
        Ver fontes consultadas ({sources.length})
      </CollapsibleTrigger>
      <CollapsibleContent className="mt-2 space-y-2 overflow-hidden">
        {sources.map((source, index) => (
          <div key={index} className="bg-muted/50 rounded-md border p-2 text-xs">
            <div className="text-muted-foreground mb-1 flex items-center justify-between">
              <span>Fonte {index + 1}</span>
              <span>{Math.round(source.similarity * 100)}% similaridade</span>
            </div>
            <p className="line-clamp-3">{source.content}</p>
          </div>
        ))}
      </CollapsibleContent>
    </Collapsible>
  )
}
