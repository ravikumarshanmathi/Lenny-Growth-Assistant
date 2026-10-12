import React from 'react';
import { Plus, MessageSquare, Trash2, Settings, Podcast, Search, X } from 'lucide-react';

export default function Sidebar({ 
  sessions, 
  currentSessionId, 
  onNewChat, 
  onSelectSession, 
  onDeleteSession, 
  activeProvider, 
  user, 
  onProfileClick,
  searchQuery,
  setSearchQuery
}) {
  return (
    <div className="w-[260px] h-full bg-surface border-r border-border flex flex-col shrink-0 flex-none">
      {/* Top Section */}
      <div className="p-3">
        <div className="flex items-center gap-2 px-2 py-2 mb-4">
          <div className="w-6 h-6 rounded bg-indigo-500 flex items-center justify-center text-white shrink-0 shadow-sm shadow-indigo-500/30">
            <Podcast className="w-4 h-4" />
          </div>
          <span className="font-semibold text-zinc-100 tracking-tight text-sm">Lenny Growth Assistant</span>
        </div>

        <button 
          onClick={onNewChat}
          className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-700 text-white px-3 py-2 rounded-lg transition-colors text-sm font-medium shadow-sm mb-3"
        >
          <Plus className="w-4 h-4" />
          New Chat
        </button>

        {/* Search Bar for Chats */}
        <div className="relative">
          <Search className="w-3.5 h-3.5 text-zinc-500 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            value={searchQuery || ''}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search chats..."
            className="w-full bg-zinc-900/90 border border-zinc-800/80 focus:border-indigo-500/60 focus:bg-zinc-900 rounded-lg pl-8 pr-7 py-1.5 text-xs text-zinc-200 placeholder-zinc-500 focus:outline-none transition-all shadow-inner"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-zinc-300 p-0.5 rounded transition-colors"
              title="Clear search"
            >
              <X className="w-3 h-3" />
            </button>
          )}
        </div>
      </div>

      {/* Session List */}
      <div className="flex-1 overflow-y-auto px-2 py-1 scrollbar-thin scrollbar-thumb-zinc-800">
        <div className="flex items-center justify-between px-2 mb-1.5">
          <span className="text-[11px] font-semibold text-zinc-500 uppercase tracking-wider">
            {searchQuery ? 'Search Results' : 'History'}
          </span>
          {searchQuery && (
            <span className="text-[10px] text-zinc-500">
              {sessions.length} found
            </span>
          )}
        </div>

        <div className="space-y-1">
          {sessions.length === 0 ? (
            <div className="px-3 py-8 text-center text-zinc-500 text-xs">
              {searchQuery ? (
                <>
                  <p>No chats found matching</p>
                  <p className="text-zinc-400 font-medium truncate mt-0.5">"{searchQuery}"</p>
                  <button
                    onClick={() => setSearchQuery('')}
                    className="mt-2.5 text-indigo-400 hover:text-indigo-300 text-[11px] font-medium transition-colors"
                  >
                    Clear search
                  </button>
                </>
              ) : (
                'No previous chats yet'
              )}
            </div>
          ) : (
            sessions.map(session => (
              <div 
                key={session.id}
                onClick={() => onSelectSession(session.id)}
                className={`group flex items-center justify-between px-2.5 py-2 rounded-lg cursor-pointer transition-all text-sm ${
                  currentSessionId === session.id 
                    ? 'bg-zinc-800/90 text-zinc-100 font-medium shadow-sm' 
                    : 'text-zinc-400 hover:bg-zinc-800/40 hover:text-zinc-200'
                }`}
              >
                <div className="flex items-center gap-2 overflow-hidden flex-1 min-w-0 pr-1">
                  <MessageSquare className={`w-3.5 h-3.5 shrink-0 ${currentSessionId === session.id ? 'text-indigo-400' : 'text-zinc-500'}`} />
                  {(() => {
                    const title = (session.title && session.title.trim()) || 'New Chat';
                    const disambiguationMatch = title.match(/^(.*?)\s*(\(\d+\))$/);
                    const isActive = currentSessionId === session.id;

                    if (disambiguationMatch) {
                      const [, baseText, countTag] = disambiguationMatch;
                      return (
                        <div className="truncate text-xs flex items-center gap-1.5 min-w-0 flex-1" title={title}>
                          <span className="truncate">{baseText}</span>
                          <span className={`text-[10px] font-mono shrink-0 px-1.5 py-0.5 rounded border leading-none transition-colors ${
                            isActive
                              ? 'bg-indigo-950/80 text-indigo-300 border-indigo-700/60 font-semibold'
                              : 'bg-zinc-800/90 text-zinc-400 border-zinc-700/60 group-hover:border-zinc-600'
                          }`}>
                            {countTag}
                          </span>
                        </div>
                      );
                    }
                    return <span className="truncate text-xs" title={title}>{title}</span>;
                  })()}
                </div>
                <button 
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteSession(session.id);
                  }}
                  title="Delete chat"
                  className={`p-1 text-zinc-500 hover:text-red-400 hover:bg-red-500/10 rounded transition-all shrink-0 ${
                    currentSessionId === session.id ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'
                  }`}
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-border bg-zinc-900/30">
        <div 
          onClick={onProfileClick}
          className="flex items-center justify-between px-2 py-2 cursor-pointer hover:bg-zinc-800 rounded-md transition-colors"
        >
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-zinc-800 flex items-center justify-center border border-zinc-700 overflow-hidden">
              {user ? (
                <span className="text-xs font-semibold text-zinc-300">{user.email.substring(0, 2).toUpperCase()}</span>
              ) : (
                <span className="text-xs font-semibold text-zinc-300">ME</span>
              )}
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-medium text-zinc-200">
                {user ? user.email.split('@')[0] : 'Sign In'}
              </span>
              <span className="text-[10px] text-zinc-500 flex items-center gap-1 uppercase tracking-wide mt-0.5">
                <span className={`w-1.5 h-1.5 rounded-full ${activeProvider === 'ollama' ? 'bg-orange-500' : 'bg-green-500'}`}></span>
                {activeProvider === 'ollama' ? 'Local' : 'Cloud API'}
              </span>
            </div>
          </div>
          <button className="text-zinc-400 transition-colors p-1 rounded">
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
