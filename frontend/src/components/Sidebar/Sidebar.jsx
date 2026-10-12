import { useState } from 'react';

/**
 * Sidebar — session list, new chat action, and provider badge.
 */
function Sidebar({ activeSession, onSelectSession, providerInfo }) {
  const [sessions] = useState([]);

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <h1 className="sidebar-title">Lenny Assistant</h1>
        <span className="sidebar-version">{providerInfo?.version || '—'}</span>
      </div>

      <button
        className="new-chat-btn"
        onClick={() => onSelectSession(null)}
      >
        + New Chat
      </button>

      <nav className="session-list">
        {sessions.length === 0 ? (
          <p className="session-empty">No conversations yet</p>
        ) : (
          sessions.map((s) => {
            const title = (s.title && s.title.trim()) || 'Untitled';
            const disambiguationMatch = title.match(/^(.*?)\s*(\(\d+\))$/);
            return (
              <button
                key={s.id}
                className={`session-item ${activeSession === s.id ? 'active' : ''}`}
                onClick={() => onSelectSession(s.id)}
                title={title}
              >
                {disambiguationMatch ? (
                  <span className="session-title-wrap">
                    <span className="session-title-text">{disambiguationMatch[1]}</span>
                    <span className="session-disambiguation-badge">{disambiguationMatch[2]}</span>
                  </span>
                ) : (
                  title
                )}
              </button>
            );
          })
        )}
      </nav>

      {/* Provider Badge */}
      <div className="provider-badge">
        <span className={`badge-dot ${providerInfo?.provider === 'offline' ? 'offline' : 'online'}`} />
        <span className="badge-label">
          {providerInfo?.provider || 'connecting...'}
        </span>
      </div>
    </aside>
  );
}

export default Sidebar;
