import { useState } from 'react';

/**
 * ChatPanel — main conversational interface.
 *
 * Displays message history and an input area.
 * Streams assistant responses via SSE (Phase 2).
 */
function ChatPanel({ sessionId, onArtifactSelect }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    // TODO (Phase 2): Send to /api/chat via SSE and stream response
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Chat endpoint is not yet connected. Backend implementation coming in Phase 2.',
        },
      ]);
      setIsLoading(false);
    }, 800);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const [copiedKey, setCopiedKey] = useState(null);

  const isRefusal = (text) => {
    if (!text || typeof text !== 'string') return false;
    const lower = text.toLowerCase();
    return lower.includes('no relevant podcast transcript found') ||
           lower.includes("couldn't find enough information in lenny's podcast transcripts");
  };

  const displayMessages = messages.filter((msg, i, arr) => {
    if (msg.role === 'assistant' && isRefusal(msg.content)) {
      return i > 0 && arr[i - 1]?.role === 'user' && Boolean(arr[i - 1]?.content?.trim());
    }
    return true;
  });

  const handleCopy = (text, key) => {
    if (navigator?.clipboard?.writeText) {
      navigator.clipboard.writeText(text);
      setCopiedKey(key);
      setTimeout(() => setCopiedKey(null), 1800);
    }
  };

  return (
    <main className="chat-panel">
      {/* Message list */}
      <div className="message-list">
        {displayMessages.length === 0 ? (
          <div className="chat-empty-state">
            <h2>Ask Lenny's Podcast</h2>
            <p>Ask product & growth questions grounded in expert insights, or generate long-form essays.</p>
          </div>
        ) : (
          displayMessages.map((msg, i) => (
            <div key={i} className={`message-bubble ${msg.role}`}>
              <div className="message-bubble-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px', fontSize: '11px', opacity: 0.8 }}>
                <span>{msg.role === 'user' ? 'You' : 'Lenny Assistant'}</span>
                <div style={{ display: 'flex', gap: '6px' }}>
                  {msg.role === 'user' && (
                    <button
                      type="button"
                      className="edit-prompt-btn"
                      onClick={() => setInput(msg.content)}
                      title="Edit prompt"
                      style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'inherit', fontSize: '11px' }}
                    >
                      Edit
                    </button>
                  )}
                  <button
                    type="button"
                    className="copy-btn"
                    onClick={() => handleCopy(msg.content, `${msg.role}-${i}`)}
                    title="Copy text"
                    style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'inherit', fontSize: '11px' }}
                  >
                    {copiedKey === `${msg.role}-${i}` ? 'Copied!' : 'Copy'}
                  </button>
                </div>
              </div>
              <div className="message-content">{msg.content}</div>
              {msg.citations && msg.citations.length > 0 && (
                <div className="citation-list">
                  {msg.citations.map((c, j) => (
                    <span key={j} className="citation-chip">{c.episode_title}</span>
                  ))}
                </div>
              )}
            </div>
          ))
        )}
        {isLoading && (
          <div className="message-bubble assistant loading">
            <span className="typing-indicator">
              <span></span><span></span><span></span>
            </span>
          </div>
        )}
      </div>

      {/* Input area */}
      <div className="chat-input-area">
        <textarea
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about product strategy, growth frameworks, or request an essay..."
          rows={1}
          disabled={isLoading}
        />
        <button
          className="send-btn"
          onClick={handleSend}
          disabled={!input.trim() || isLoading}
        >
          Send
        </button>
      </div>
    </main>
  );
}

export default ChatPanel;
