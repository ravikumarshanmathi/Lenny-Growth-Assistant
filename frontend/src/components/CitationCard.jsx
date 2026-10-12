import React, { useState } from 'react';
import { ChevronDown, ChevronUp, FileText, ExternalLink } from 'lucide-react';

export default function CitationCard({ citation, onViewSource }) {
  const [isOpen, setIsOpen] = useState(false);
  const matchPercentage = Math.round((citation.similarity_score || 0) * 100);

  return (
    <div className="mt-2 text-sm border border-border/80 rounded-lg bg-zinc-900/60 overflow-hidden max-w-2xl transition-all shadow-sm hover:border-zinc-700">
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-2.5 hover:bg-zinc-800/40 transition-colors text-left"
      >
        <div className="flex items-center gap-2 overflow-hidden flex-1 min-w-0 mr-2">
          <FileText className="w-3.5 h-3.5 text-indigo-400 shrink-0" />
          <span className="truncate font-medium text-zinc-300 text-xs">
            {citation.episode_title}
          </span>
          {citation.metadata?.file_name && (
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-zinc-800 text-indigo-300/90 font-mono shrink-0 border border-zinc-700/60">
              {citation.metadata.file_name}
            </span>
          )}
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-zinc-800/90 text-zinc-400 shrink-0 border border-zinc-700/80">
            {matchPercentage}% match
          </span>
        </div>
        {isOpen ? <ChevronUp className="w-4 h-4 text-zinc-400 shrink-0" /> : <ChevronDown className="w-4 h-4 text-zinc-500 shrink-0" />}
      </button>
      
      {isOpen && (
        <div className="p-3 pt-2 border-t border-border/60 bg-zinc-900/90 text-xs text-zinc-400 space-y-2.5">
          <div className="flex items-center justify-between text-[11px] text-zinc-400 border-b border-zinc-800/60 pb-2">
            <div>
              <span className="text-zinc-500 font-medium">Source Document:</span>{' '}
              <span className="text-zinc-300 font-mono">{citation.metadata?.file_name}</span>
            </div>
            {citation.metadata?.guest && (
              <div>
                <span className="text-zinc-500 font-medium">Guest:</span>{' '}
                <span className="text-zinc-300">{citation.metadata.guest}</span>
              </div>
            )}
          </div>

          {citation.metadata?.chunk_content && (
            <div className="p-2.5 rounded bg-zinc-950/80 border border-zinc-800/80 text-xs text-zinc-300 leading-relaxed font-sans whitespace-pre-wrap">
              <span className="text-[10px] text-indigo-400/90 font-semibold uppercase tracking-wider block mb-1">
                Transcript Excerpt
              </span>
              {citation.metadata.chunk_content}
            </div>
          )}

          <div className="flex items-center justify-end pt-1">
            <button
              onClick={(e) => {
                e.stopPropagation();
                onViewSource?.();
              }}
              className="flex items-center gap-1.5 px-3 py-1 text-xs text-indigo-400 hover:text-indigo-300 bg-indigo-500/10 hover:bg-indigo-500/20 rounded-md border border-indigo-500/20 transition-colors font-medium shadow-sm"
              title="Open full document in artifact panel"
            >
              <ExternalLink className="w-3.5 h-3.5" />
              <span>View Source File</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
