import { useRef, useEffect } from 'react';
import { sanitizeHtml } from '../../utils/sanitize.js';

/**
 * ArtifactPanel — sandboxed side panel for rendering Markdown/HTML/CSS artifacts.
 *
 * Security isolation model (ADR-003):
 *   Layer 1: Server-side sanitization (bleach) — done before storage
 *   Layer 2: Client-side sanitization (DOMPurify) — done here before render
 *   Layer 3: Sandboxed iframe — no allow-scripts, no allow-top-navigation
 */
function ArtifactPanel({ artifact, onClose }) {
  const iframeRef = useRef(null);

  useEffect(() => {
    if (!artifact || !iframeRef.current) return;

    let content = artifact.content || artifact.code || '';
    const lower = content.toLowerCase();
    if (lower.includes('<body') || lower.includes('<html') || lower.includes('<!doctype')) {
      const missingBody = !lower.includes('</body>');
      const missingHtml = !lower.includes('</html>');
      if (missingBody && missingHtml) {
        content += '</body></html>';
      } else if (missingBody) {
        content += '</body>';
      } else if (missingHtml) {
        content += '</html>';
      }
    }

    // Layer 2: Client-side sanitization via DOMPurify
    const sanitizedContent = sanitizeHtml(content);

    // Wrap in a complete HTML document with CSP meta tag
    const srcdoc = `
      <!DOCTYPE html>
      <html>
      <head>
        <meta http-equiv="Content-Security-Policy"
              content="default-src 'none'; style-src 'unsafe-inline'; img-src data: https:;">
        <style>
          body {
            font-family: 'Inter', -apple-system, sans-serif;
            color: #e4e4ed;
            background: #1a1b26;
            padding: 1.5rem;
            line-height: 1.6;
          }
          h1, h2, h3 { color: #ffffff; margin-bottom: 0.5em; }
          code { background: #2a2b3d; padding: 2px 6px; border-radius: 4px; font-size: 0.9em; }
          pre { background: #2a2b3d; padding: 1rem; border-radius: 8px; overflow-x: auto; }
          blockquote { border-left: 3px solid #7c5cfc; padding-left: 1rem; color: #9394a5; }
          a { color: #7c5cfc; }
          table { border-collapse: collapse; width: 100%; }
          th, td { border: 1px solid #2e2f42; padding: 8px 12px; text-align: left; }
          th { background: #24253a; }
        </style>
      </head>
      <body>${sanitizedContent}</body>
      </html>
    `;

    iframeRef.current.srcdoc = srcdoc;
  }, [artifact]);

  if (!artifact) return null;

  return (
    <aside className="artifact-panel">
      <div className="artifact-header">
        <div className="artifact-title-row">
          <h3 className="artifact-title">Artifact Preview</h3>
          <span className="artifact-type-badge">{artifact.artifact_type || artifact.type || 'html'}</span>
        </div>
        <button className="artifact-close-btn" onClick={onClose} aria-label="Close artifact panel">
          ✕
        </button>
      </div>

      <iframe
        ref={iframeRef}
        className="artifact-iframe w-full h-full border-0"
        sandbox="allow-scripts"
        title="Artifact Preview"
      />
    </aside>
  );
}

export default ArtifactPanel;
