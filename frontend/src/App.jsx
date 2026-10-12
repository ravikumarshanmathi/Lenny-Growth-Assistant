import React, { useState, useRef, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import ChatFeed from './components/ChatFeed';
import ArtifactViewer from './components/ArtifactViewer';
import LoginModal from './components/LoginModal';
import ProfileModal from './components/ProfileModal';
import ProviderDropdown from './components/ProviderDropdown';
import { PanelRightClose, PanelRightOpen, CornerDownLeft, ShieldCheck, Paperclip, Mic, AudioLines } from 'lucide-react';

export default function App() {
  const [sessions, setSessions] = useState([]);
  const [currentSessionId, setCurrentSessionId] = useState('new');
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [provider, setProvider] = useState('ollama'); // 'ollama', 'anthropic', 'openai'
  const [isLoading, setIsLoading] = useState(false);
  const [activeArtifact, setActiveArtifact] = useState(null);
  const [isArtifactPanelOpen, setIsArtifactPanelOpen] = useState(false);
  const [user, setUser] = useState(null);
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);
  
  const [attachedFile, setAttachedFile] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Resizable split-screen layout state
  const [chatPercent, setChatPercent] = useState(50); // Default 50% / 50% split
  const [isDragging, setIsDragging] = useState(false);
  const splitContainerRef = useRef(null);

  const textareaRef = useRef(null);
  const fileInputRef = useRef(null);
  const recognitionRef = useRef(null);

  // Drag-to-resize listener
  useEffect(() => {
    if (!isDragging) return;

    const handlePointerMove = (e) => {
      if (!splitContainerRef.current) return;
      const rect = splitContainerRef.current.getBoundingClientRect();
      if (rect.width <= 0) return;

      const rawChatPercent = ((e.clientX - rect.left) / rect.width) * 100;
      // Constraints: Chat min 30%, max 70% (which also ensures Artifact is min 30%, max 70%)
      const clampedChatPercent = Math.min(Math.max(rawChatPercent, 30), 70);
      setChatPercent(clampedChatPercent);
    };

    const handlePointerUp = () => {
      setIsDragging(false);
    };

    window.addEventListener('pointermove', handlePointerMove);
    window.addEventListener('pointerup', handlePointerUp);

    // Prevent text selection while dragging
    document.body.style.userSelect = 'none';
    document.body.style.cursor = 'col-resize';

    return () => {
      window.removeEventListener('pointermove', handlePointerMove);
      window.removeEventListener('pointerup', handlePointerUp);
      document.body.style.userSelect = '';
      document.body.style.cursor = '';
    };
  }, [isDragging]);

  // Initialize Speech Recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;

      recognitionRef.current.onresult = (event) => {
        let finalTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
          }
        }
        if (finalTranscript) {
          setInput((prev) => prev + (prev ? ' ' : '') + finalTranscript);
        }
      };

      recognitionRef.current.onerror = (event) => {
        console.error("Speech recognition error", event.error);
        setIsRecording(false);
      };

      recognitionRef.current.onend = () => {
        setIsRecording(false);
      };
    }
  }, []);

  const toggleRecording = () => {
    if (isRecording) {
      recognitionRef.current?.stop();
      setIsRecording(false);
    } else {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.start();
          setIsRecording(true);
        } catch (e) {
          console.error("Microphone access denied or error:", e);
        }
      } else {
        alert("Speech recognition is not supported in this browser.");
      }
    }
  };

  // Fetch sessions (supports keyword search)
  const fetchSessions = async (query = searchQuery) => {
    try {
      const url = query && query.trim()
        ? `http://localhost:8000/api/sessions/?q=${encodeURIComponent(query.trim())}`
        : 'http://localhost:8000/api/sessions/';
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setSessions(data);
      }
    } catch (err) {
      console.error("Failed to load sessions", err);
    }
  };

  // Debounce search input for real-time keyword search
  useEffect(() => {
    const handler = setTimeout(() => {
      fetchSessions(searchQuery);
    }, 200);
    return () => clearTimeout(handler);
  }, [searchQuery]);

  // Permanently delete a chat session from database & state
  const handleDeleteSession = async (id) => {
    // 1. Optimistically remove from UI
    setSessions(prev => prev.filter(s => s.id !== id));

    // 2. If the active chat is deleted, reset view to a clean new chat
    if (currentSessionId === id) {
      setCurrentSessionId('new');
      setMessages([]);
      setActiveArtifact(null);
      setIsArtifactPanelOpen(false);
    }

    // 3. Persist deletion in PostgreSQL
    try {
      const res = await fetch(`http://localhost:8000/api/sessions/${id}`, {
        method: 'DELETE'
      });
      if (!res.ok) {
        console.error("Failed to delete session on server", await res.text());
        fetchSessions(searchQuery);
      }
    } catch (err) {
      console.error("Network error deleting session", err);
      fetchSessions(searchQuery);
    }
  };

  // Fetch history when a session is selected
  useEffect(() => {
    if (currentSessionId === 'new') {
      setMessages([]);
    } else if (currentSessionId) {
      fetch(`http://localhost:8000/api/sessions/${currentSessionId}/history`)
        .then(res => res.json())
        .then(data => {
          const rawMessages = data.messages || [];
          const isRefusal = (content) => {
            if (!content || typeof content !== 'string') return false;
            const lower = content.toLowerCase();
            return lower.includes('no relevant podcast transcript found') || 
                   lower.includes("couldn't find enough information in lenny's podcast transcripts");
          };
          // Filter out orphan refusal messages on session initialization
          const validMessages = rawMessages.filter((msg, idx, arr) => {
            if (msg.role === 'assistant' && isRefusal(msg.content)) {
              return idx > 0 && arr[idx - 1]?.role === 'user' && Boolean(arr[idx - 1]?.content?.trim());
            }
            return true;
          });
          setMessages(validMessages);
        })
        .catch(err => {
          console.error("Failed to load history", err);
          setMessages([]);
        });
    }
  }, [currentSessionId]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [input]);

  const handleNewChat = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/sessions/', { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });
      if (res.ok) {
        const newSession = await res.json();
        setSessions(prev => [newSession, ...prev]);
        setCurrentSessionId(newSession.id);
        setMessages([]);
        setIsArtifactPanelOpen(false);
      }
    } catch (err) {
      console.error("Failed to create new session", err);
    }
  };

  const handleSend = async () => {
    if ((!input.trim() && !attachedFile) || isLoading) return;
    
    let activeSessionId = currentSessionId;
    
    // Auto-create session if sending first message
    if (activeSessionId === 'new') {
      try {
        const res = await fetch('http://localhost:8000/api/sessions/', { 
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({})
        });
        if (res.ok) {
          const newSession = await res.json();
          setSessions(prev => [newSession, ...prev]);
          activeSessionId = newSession.id;
          setCurrentSessionId(activeSessionId);
        } else {
          let errMsg = "Failed to create a new session on the backend.";
          try {
            const errData = await res.json();
            errMsg = errData.detail || errMsg;
          } catch (_) {}
          setMessages(prev => [...prev, 
            { role: 'user', content: input.trim() }, 
            { role: 'assistant', content: `⚠️ **Database Error (${res.status}):** ${errMsg}\n\n**Fix:** Open Docker Desktop and run \`docker compose up db -d\` in the project folder.` }
          ]);
          setInput('');
          setAttachedFile(null);
          return;
        }
      } catch (err) {
        console.error("Network error auto-creating session:", err);
        setMessages(prev => [...prev, { role: 'user', content: input.trim() }, { role: 'assistant', content: "⚠️ **Network Error:** Could not reach the backend server to create a session. Please ensure your backend is running." }]);
        setInput('');
        setAttachedFile(null);
        return;
      }
    }
    
    let userMessage = input.trim();
    if (attachedFile) {
      userMessage = `[Attached File: ${attachedFile.name} (${Math.round(attachedFile.size / 1024)}KB)]\n\n${userMessage}`;
    }

    // Create local message for optimistic UI
    const newUserMsg = { role: 'user', content: userMessage };
    setMessages(prev => [...prev, newUserMsg]);
    setInput('');
    setAttachedFile(null);
    setIsLoading(true);

    try {
      const res = await fetch('http://localhost:8000/api/chat/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: activeSessionId,
          message: userMessage,
          provider_override: provider
        })
      });

      if (res.ok) {
        const data = await res.json();
        
        // Immediately update session title in state so sidebar re-renders instantly
        if (data.session_title) {
          setSessions(prev => prev.map(s => 
            s.id === activeSessionId ? { ...s, title: data.session_title } : s
          ));
        }

        const newAssistantMsg = {
          role: 'assistant',
          content: data.answer,
          artifact: data.artifact,
          citations: data.citations || [],
          active_provider: data.active_provider,
          fallback_triggered: data.fallback_triggered
        };

        // Client-side artifact interception safety net:
        // If backend didn't extract an artifact but the answer contains HTML code blocks,
        // extract and route them to the artifact panel automatically.
        if (!newAssistantMsg.artifact && newAssistantMsg.content) {
          const htmlBlockRegex = /```html\s*\n([\s\S]*?)```/;
          const match = newAssistantMsg.content.match(htmlBlockRegex);
          if (match) {
            const htmlContent = match[1].trim();
            // Try to extract title from <!-- Artifact: Title --> comment
            const titleMatch = htmlContent.match(/<!--\s*Artifact:\s*(.+?)\s*-->/);
            const artifactTitle = titleMatch ? titleMatch[1].trim() : 'Generated HTML Artifact';
            
            newAssistantMsg.artifact = {
              type: 'html',
              title: artifactTitle,
              content: htmlContent
            };
            // Replace the code block in the chat message with a clean summary
            newAssistantMsg.content = newAssistantMsg.content
              .replace(htmlBlockRegex, '')
              .trim() || `I've rendered the requested **${artifactTitle}** in the artifact viewer.`;
          }
        }
        
        setMessages(prev => [...prev, newAssistantMsg]);
        
        // Auto-open artifact if generated
        if (newAssistantMsg.artifact) {
          setActiveArtifact(newAssistantMsg.artifact);
          setIsArtifactPanelOpen(true);
        }
      } else {
        let errorDetail = "An error occurred while generating the response.";
        try {
          const errData = await res.json();
          errorDetail = errData.detail || errorDetail;
        } catch (_) {
          try { errorDetail = await res.text(); } catch (__) {}
        }
        console.error("Chat API error:", errorDetail);
        setMessages(prev => [...prev, { role: 'assistant', content: `⚠️ **Error (${res.status}):** ${errorDetail}` }]);
      }
    } catch (err) {
      console.error("Network error during chat:", err);
      setMessages(prev => [...prev, { role: 'assistant', content: "Network error occurred." }]);
    } finally {
      setIsLoading(false);
      // Refresh session list to get updated titles
      fetchSessions();
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const openArtifact = (artifact) => {
    setActiveArtifact(artifact);
    setIsArtifactPanelOpen(true);
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-background">
      <Sidebar 
        sessions={sessions}
        currentSessionId={currentSessionId}
        onNewChat={handleNewChat}
        onSelectSession={(id) => setCurrentSessionId(id)}
        onDeleteSession={handleDeleteSession}
        activeProvider={provider}
        user={user}
        onProfileClick={() => user ? setIsProfileModalOpen(true) : setIsLoginModalOpen(true)}
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
      />
      
      <div ref={splitContainerRef} className={`flex flex-1 overflow-hidden relative ${isDragging ? 'select-none' : ''}`}>
        {/* Aurora Background */}
        <div className="absolute inset-0 z-0 pointer-events-none overflow-hidden">
          <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-pink-600/20 blur-[120px] rounded-full mix-blend-screen"></div>
          <div className="absolute top-[10%] right-[-10%] w-[50%] h-[50%] bg-blue-600/20 blur-[120px] rounded-full mix-blend-screen"></div>
          <div className="absolute bottom-[-10%] left-[20%] w-[60%] h-[50%] bg-purple-600/20 blur-[120px] rounded-full mix-blend-screen"></div>
        </div>

        {/* Main Chat Panel */}
        <div 
          className={`flex flex-col h-full overflow-hidden relative z-10 ${
            isDragging ? '' : 'transition-[width] duration-150 ease-out'
          }`}
          style={{
            width: isArtifactPanelOpen ? `${chatPercent}%` : '100%',
            minWidth: isArtifactPanelOpen ? '30%' : '100%',
            maxWidth: isArtifactPanelOpen ? '70%' : '100%'
          }}
        >
          {/* Top Bar */}
          <header className="h-14 bg-background/50 backdrop-blur-md border-b border-border flex items-center justify-between px-4 shrink-0 z-10">
            <div className="flex items-center gap-3">
              <span className="font-medium text-zinc-200 text-sm">{currentSessionId === 'new' ? 'New Conversation' : 'Current Session'}</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-medium tracking-wide bg-zinc-800 text-zinc-300 border border-zinc-700 shadow-sm">
                {provider === 'ollama' ? 'Local' : provider === 'anthropic' ? 'Claude' : provider === 'openai' ? 'GPT-4o' : provider}
              </span>
            </div>
            {messages.some(m => m.artifact) && (
              <button 
                onClick={() => setIsArtifactPanelOpen(!isArtifactPanelOpen)}
                className="p-1.5 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 rounded transition-colors flex items-center gap-2 text-xs font-medium"
                title={isArtifactPanelOpen ? "Close Artifacts" : "Open Artifacts"}
              >
                {isArtifactPanelOpen ? (
                  <>Close Panel <PanelRightClose className="w-4 h-4" /></>
                ) : (
                  <>Open Panel <PanelRightOpen className="w-4 h-4" /></>
                )}
              </button>
            )}
          </header>

          {/* Chat Feed (overflow-y-auto is inside ChatFeed) */}
          <ChatFeed 
            messages={messages} 
            isLoading={isLoading} 
            onOpenArtifact={openArtifact}
            isArtifactOpen={isArtifactPanelOpen}
            toggleArtifactPanel={() => setIsArtifactPanelOpen(!isArtifactPanelOpen)}
            onEditPrompt={(promptText) => {
              setInput(promptText);
              if (textareaRef.current) {
                textareaRef.current.focus();
              }
            }}
          />

          {/* Composer */}
          <div className="p-6 shrink-0 z-10 flex flex-col items-center bg-background/50 backdrop-blur-sm">
            <div className="w-full max-w-2xl relative group">
              
              {/* File Attachment Badge */}
              {attachedFile && (
                <div className="absolute -top-10 left-4 bg-zinc-800 border border-zinc-700 rounded-md px-3 py-1.5 flex items-center gap-2 text-xs text-zinc-300 shadow-lg z-20">
                  <Paperclip className="w-3.5 h-3.5" />
                  <span className="truncate max-w-[200px]">{attachedFile.name}</span>
                  <button 
                    onClick={() => setAttachedFile(null)}
                    className="ml-2 text-zinc-500 hover:text-red-400"
                  >
                    ×
                  </button>
                </div>
              )}

              <div className="absolute -inset-[1px] bg-gradient-to-r from-pink-500 via-purple-500 to-blue-500 rounded-full opacity-70 blur-sm group-hover:opacity-100 transition duration-500"></div>
              <div className="relative flex items-center bg-zinc-950 rounded-full px-2 py-1 border border-zinc-800 shadow-2xl">
                
                {/* Hidden file input */}
                <input 
                  type="file" 
                  ref={fileInputRef}
                  className="hidden" 
                  onChange={(e) => {
                    const file = e.target.files[0];
                    if (file) {
                      setAttachedFile(file);
                    }
                  }}
                />
                <button 
                  onClick={() => fileInputRef.current?.click()}
                  className="p-3 text-zinc-400 hover:text-zinc-200 transition-colors rounded-full" 
                  title="Attach file"
                >
                  <Paperclip className="w-5 h-5" />
                </button>
                <div className="w-[1px] h-6 bg-zinc-800 mx-2"></div>
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder={isRecording ? "Listening..." : " Let's have discussion"}
                  className="flex-1 bg-transparent border-none outline-none text-zinc-100 placeholder:text-zinc-500 px-2 py-3 text-base font-medium"
                />
                <div className="flex items-center gap-1 pr-1">
                  <button 
                    onClick={toggleRecording}
                    className={`p-3 transition-colors rounded-full ${isRecording ? 'text-red-500 animate-pulse bg-red-500/10' : 'text-zinc-400 hover:text-zinc-200'}`}
                    title={isRecording ? "Stop recording" : "Start recording"}
                  >
                    <Mic className="w-5 h-5" />
                  </button>
                  <button 
                    onClick={handleSend}
                    disabled={(!input.trim() && !attachedFile) || isLoading}
                    className="bg-blue-600 hover:bg-blue-500 disabled:bg-zinc-800 disabled:text-zinc-600 text-white rounded-full p-2.5 transition-colors"
                  >
                    <AudioLines className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
            
            <div className="mt-4 text-center flex items-center justify-center gap-4 text-[10px] text-zinc-500 font-medium tracking-wide">
              <ProviderDropdown provider={provider} setProvider={setProvider} />
              <span>•</span>
              <div className="flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5" />
                Grounded on Lenny's Transcripts
              </div>
            </div>
          </div>
        </div>

        {/* Resizer Divider Bar between Chat and Artifact Panel */}
        {isArtifactPanelOpen && (
          <div
            onPointerDown={(e) => {
              e.preventDefault();
              setIsDragging(true);
            }}
            className={`w-1.5 shrink-0 cursor-col-resize relative z-30 transition-colors select-none group flex items-center justify-center ${
              isDragging ? 'bg-indigo-500 shadow-md shadow-indigo-500/50' : 'bg-zinc-800/80 hover:bg-indigo-500'
            }`}
            title="Drag to resize panels (30% - 70%)"
          >
            {/* Visual handle indicator dots */}
            <div className="w-0.5 h-6 rounded-full bg-zinc-600 group-hover:bg-white transition-colors" />
          </div>
        )}

        {/* Resizable Artifact Panel Wrapper */}
        {isArtifactPanelOpen && (
          <div 
            className={`h-full flex overflow-hidden relative z-20 ${
              isDragging ? '' : 'transition-[width] duration-150 ease-out'
            }`}
            style={{
              width: `${100 - chatPercent}%`,
              minWidth: '30%',
              maxWidth: '70%'
            }}
          >
            <ArtifactViewer 
              artifact={activeArtifact} 
              onClose={() => setIsArtifactPanelOpen(false)} 
            />
          </div>
        )}
      </div>

      <LoginModal 
        isOpen={isLoginModalOpen} 
        onClose={() => setIsLoginModalOpen(false)} 
        onLogin={(userData) => setUser(userData)} 
      />
      
      <ProfileModal 
        isOpen={isProfileModalOpen} 
        onClose={() => setIsProfileModalOpen(false)} 
        user={user} 
        onLogout={() => setUser(null)} 
      />
    </div>
  );
}
