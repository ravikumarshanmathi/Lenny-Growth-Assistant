import React, { useRef, useEffect, useState } from 'react';
import { FileCode2, PanelRight, Sparkles, AlertCircle, Copy, Check, RotateCcw } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import CitationCard from './CitationCard';

export const isRefusalMessage = (content) => {
  if (!content || typeof content !== 'string') return false;
  const lower = content.toLowerCase().trim();
  return (
    lower.includes('no relevant podcast transcript found') ||
    lower.includes("couldn't find enough information in lenny's podcast transcripts") ||
    lower.includes("no podcast transcripts found") ||
    lower.includes("unable to find relevant insights on this topic in lenny's podcast transcripts") ||
    lower.includes("unable to find relevant insights")
  );
};

export default function ChatFeed({ 
  messages = [], 
  isLoading, 
  onOpenArtifact, 
  isArtifactOpen, 
  toggleArtifactPanel,
  onEditPrompt
}) {
  const endOfMessagesRef = useRef(null);
  const [copiedKey, setCopiedKey] = useState(null);

  // Guarantee that refusal messages are ONLY rendered when directly preceded by a valid user prompt
  const displayMessages = messages.filter((msg, idx, arr) => {
    if (msg.role === 'assistant' && isRefusalMessage(msg.content)) {
      // Must be preceded by a valid user question
      return idx > 0 && arr[idx - 1]?.role === 'user' && Boolean(arr[idx - 1]?.content?.trim());
    }
    return true;
  });

  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [displayMessages, isLoading]);

  const normalizeMarkdown = (content) => {
    if (!content) return '';
    // Ensure lists have clear paragraph separation so bolding and indentation render cleanly
    return content.replace(/([^\n])\n([*-]|\d+\.) /g, '$1\n\n$2 ');
  };

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6 scroll-smooth relative z-10 bg-transparent">
      <div className="max-w-3xl mx-auto space-y-8">
        
        {displayMessages.length === 0 ? (
          <div className="h-[40vh] flex flex-col items-center justify-center text-center px-4">
            <div className="w-12 h-12 bg-indigo-500/10 rounded-xl flex items-center justify-center mb-4 border border-indigo-500/20 shadow-inner">
              <Sparkles className="w-6 h-6 text-indigo-400" />
            </div>
            <h2 className="text-xl font-semibold text-zinc-200 mb-2">Welcome!</h2>
            <p className="text-sm text-zinc-500 max-w-md leading-relaxed">
              I'm glad you're here. Ask me anything about product strategy, growth loops, and frameworks from Lenny's Podcast.
            </p>
          </div>
        ) : (
          displayMessages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} group/msg`}>
              
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-white shrink-0 mr-3 mt-1 shadow-md">
                  <Sparkles className="w-4 h-4" />
                </div>
              )}

              <div className={`max-w-[85%] relative ${msg.role === 'user' ? 'bg-zinc-800 text-zinc-100 rounded-2xl rounded-tr-sm px-4 py-3 shadow-sm' : 'text-zinc-200 flex-1 min-w-0'}`}>
                
                {msg.role === 'user' ? (
                  <div className="space-y-1.5">
                    {/* User Prompt Header Row with Copy and Edit Actions */}
                    <div className="flex items-center justify-between border-b border-zinc-700/60 pb-1 mb-1.5 gap-4">
                      <span className="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider">You</span>
                      <div className="flex items-center gap-1.5">
                        {onEditPrompt && (
                          <button
                            onClick={() => onEditPrompt(msg.content)}
                            className="flex items-center gap-1 px-1.5 py-0.5 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-700/70 rounded transition-all text-xs"
                            title="Edit / reuse prompt"
                          >
                            <RotateCcw className="w-3 h-3" />
                            <span className="text-[11px]">Edit</span>
                          </button>
                        )}
                        <button
                          onClick={() => {
                            navigator.clipboard.writeText(msg.content);
                            setCopiedKey(`user-${idx}`);
                            setTimeout(() => setCopiedKey(null), 1800);
                          }}
                          className="flex items-center gap-1 px-1.5 py-0.5 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-700/70 rounded transition-all text-xs"
                          title="Copy prompt"
                        >
                          {copiedKey === `user-${idx}` ? (
                            <>
                              <Check className="w-3 h-3 text-emerald-400" />
                              <span className="text-[11px] text-emerald-400 font-medium">Copied!</span>
                            </>
                          ) : (
                            <>
                              <Copy className="w-3 h-3" />
                              <span className="text-[11px]">Copy</span>
                            </>
                          )}
                        </button>
                      </div>
                    </div>
                    <div className="whitespace-pre-wrap text-sm leading-relaxed">{msg.content}</div>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {/* Aligned Assistant Header Row with Copy Action */}
                    <div className="flex items-center justify-between border-b border-zinc-800/60 pb-1.5 mb-2">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-semibold text-zinc-300">Lenny Assistant</span>
                        {msg.active_provider && (
                          <span className="text-[10px] px-1.5 py-0.5 rounded bg-zinc-800/90 text-zinc-400 font-medium border border-zinc-700/60">
                            {msg.active_provider === 'ollama' ? 'Local' : msg.active_provider === 'anthropic' ? 'Claude' : msg.active_provider === 'openai' ? 'GPT-4o' : msg.active_provider}
                          </span>
                        )}
                      </div>
                      <button 
                        onClick={() => {
                          navigator.clipboard.writeText(msg.content);
                          setCopiedKey(`asst-${idx}`);
                          setTimeout(() => setCopiedKey(null), 1800);
                        }}
                        className="flex items-center gap-1.5 px-2 py-0.5 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 rounded transition-all text-xs"
                        title="Copy response"
                      >
                        {copiedKey === `asst-${idx}` ? (
                          <>
                            <Check className="w-3.5 h-3.5 text-emerald-400" />
                            <span className="text-[11px] text-emerald-400 font-medium">Copied!</span>
                          </>
                        ) : (
                          <>
                            <Copy className="w-3.5 h-3.5" />
                            <span className="text-[11px] text-zinc-400">Copy</span>
                          </>
                        )}
                      </button>
                    </div>

                    {/* Main Content with Enhanced Markdown Parsing or Refusal Banner */}
                    {isRefusalMessage(msg.content) ? (
                      <div className="flex items-start gap-2.5 p-3 rounded-lg bg-zinc-850/80 border border-zinc-800 text-zinc-300 text-sm">
                        <AlertCircle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                        <div className="leading-relaxed">{msg.content}</div>
                      </div>
                    ) : (
                      <div className="prose prose-invert prose-p:leading-relaxed text-sm max-w-none">
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          components={{
                            strong: ({node, ...props}) => <strong className="font-bold text-zinc-100" {...props} />,
                            p: ({node, ...props}) => <p className="mb-2.5 last:mb-0 leading-relaxed text-zinc-200" {...props} />,
                            ul: ({node, ...props}) => <ul className="my-2.5 space-y-1.5 list-disc list-inside text-zinc-200 pl-1" {...props} />,
                            ol: ({node, ...props}) => <ol className="my-2.5 space-y-1.5 list-decimal list-inside text-zinc-200 pl-1" {...props} />,
                            li: ({node, ...props}) => <li className="text-zinc-200 leading-relaxed" {...props} />,
                            code: ({node, className, children, ...props}) => {
                              const match = /language-(\w+)/.exec(className || '');
                              const isMultiLine = typeof children === 'string' && children.includes('\n');
                              return !match && !isMultiLine ? (
                                <code className="bg-zinc-800 text-indigo-300 px-1.5 py-0.5 rounded text-xs font-mono inline" {...props}>
                                  {children}
                                </code>
                              ) : (
                                <code className="block bg-zinc-900 border border-zinc-800 p-3 rounded-lg text-xs font-mono overflow-x-auto text-zinc-200 my-2" {...props}>
                                  {children}
                                </code>
                              );
                            }
                          }}
                        >
                          {normalizeMarkdown(msg.content)}
                        </ReactMarkdown>
                      </div>
                    )}

                    {/* Artifact Trigger Card */}
                    {msg.artifact && (
                      <div 
                        onClick={() => onOpenArtifact(msg.artifact)}
                        className="mt-4 border border-indigo-500/30 bg-indigo-500/5 rounded-lg p-3 flex items-center justify-between cursor-pointer hover:bg-indigo-500/10 transition-colors w-72 shadow-sm group"
                      >
                        <div className="flex items-center gap-3 overflow-hidden">
                          <div className="bg-indigo-500/20 p-2 rounded-md">
                            <FileCode2 className="w-4 h-4 text-indigo-400 shrink-0" />
                          </div>
                          <div className="flex flex-col overflow-hidden">
                            <span className="text-[10px] font-bold text-indigo-300 uppercase tracking-wider">{msg.artifact.type}</span>
                            <span className="text-sm text-zinc-200 truncate group-hover:text-indigo-200 transition-colors">{msg.artifact.title}</span>
                          </div>
                        </div>
                        <PanelRight className="w-4 h-4 text-zinc-500 group-hover:text-indigo-300 transition-colors" />
                      </div>
                    )}

                    {/* Fallback Warning */}
                    {msg.fallback_triggered && (
                      <div className="mt-2 flex items-center gap-1.5 text-xs text-orange-400 bg-orange-500/10 py-1.5 px-2.5 rounded-md border border-orange-500/20 w-max shadow-sm">
                        <AlertCircle className="w-3.5 h-3.5" />
                        <span>Cloud API unavailable. Answered via local fallback.</span>
                      </div>
                    )}

                    {/* Citations */}
                    {msg.citations && msg.citations.length > 0 && (
                      <div className="mt-4 pt-3 border-t border-border/80">
                        <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider mb-1.5 block">Sources</span>
                        <div className="flex flex-col gap-1.5">
                          {msg.citations.map((cite, i) => (
                            <CitationCard 
                              key={i} 
                              citation={cite}
                              onViewSource={() => onOpenArtifact({
                                type: 'markdown',
                                title: cite.episode_title,
                                content: `# ${cite.episode_title}\n\n**Source File:** \`${cite.metadata?.file_name || 'transcript.txt'}\`\n**Guest:** ${cite.metadata?.guest || 'Guest'}\n**Relevance Score:** ${Math.round((cite.similarity_score || 0) * 100)}%\n\n---\n\n### Ingested Transcript Segment\n\n> ${cite.metadata?.chunk_content || 'Transcript excerpt retrieved from database.'}`
                              })}
                            />
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-white shrink-0 mr-3 shadow-md">
              <Sparkles className="w-4 h-4" />
            </div>
            <div className="flex items-center gap-1.5 mt-2 bg-zinc-800/50 px-3 py-2 rounded-2xl rounded-tl-sm w-max border border-zinc-700/50">
              <div className="w-1.5 h-1.5 bg-zinc-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="w-1.5 h-1.5 bg-zinc-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
              <div className="w-1.5 h-1.5 bg-zinc-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
          </div>
        )}
        <div ref={endOfMessagesRef} className="h-4"></div>
      </div>
    </div>
  );
}
