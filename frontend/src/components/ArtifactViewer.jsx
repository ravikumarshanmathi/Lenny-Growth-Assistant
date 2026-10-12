import React, { useState, useEffect } from 'react';
import { X, Code, Eye, Copy, Download } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

function prepareArtifactCode(content) {
  if (!content || !content.trim()) {
    return `<!DOCTYPE html><html><body style="background:#0f172a;color:#94a3b8;font-family:sans-serif;padding:2rem;text-align:center;">No HTML content available to preview.</body></html>`;
  }

  let code = content;

  // Fallback Parsing for Incomplete Streams:
  // If artifactCode is missing closing </body> or </html> tags during streaming,
  // automatically append </body></html> dynamically so the browser renders the partial HTML live instead of showing a blank screen.
  const lower = code.toLowerCase();
  const hasBody = lower.includes('<body');
  const hasHtml = lower.includes('<html') || lower.includes('<!doctype');

  if (hasBody || hasHtml) {
    const missingBody = !lower.includes('</body>');
    const missingHtml = !lower.includes('</html>');
    if (missingBody && missingHtml) {
      code += '</body></html>';
    } else if (missingBody) {
      code += '</body>';
    } else if (missingHtml) {
      code += '</html>';
    }
    return code;
  }

  // If it's a component fragment or snippet without document wrapper, wrap in complete HTML document
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    * { box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background-color: #0f172a;
      color: #f8fafc;
      padding: 1.5rem;
      line-height: 1.6;
      margin: 0;
    }
  </style>
</head>
<body>
  ${code}
</body>
</html>`;
}

export default function ArtifactViewer({ artifact, onClose }) {
  const [viewMode, setViewMode] = useState('preview'); // 'preview' or 'code'
  const [previewKey, setPreviewKey] = useState(0);

  // Tab State Check: Ensure switching between the <> Code tab and Preview tab re-triggers the iframe srcDoc render
  useEffect(() => {
    if (viewMode === 'preview') {
      setPreviewKey(prev => prev + 1);
    }
  }, [viewMode]);

  const handleTabSwitch = (mode) => {
    setViewMode(mode);
    if (mode === 'preview') {
      setPreviewKey(prev => prev + 1);
    }
  };

  if (!artifact) return null;

  const isHtml = artifact.type === 'html' || artifact.artifact_type === 'html';
  const rawCode = artifact.code || artifact.content || (typeof artifact === 'string' ? artifact : '') || '';
  const artifactCode = prepareArtifactCode(rawCode);

  const handleCopy = () => {
    navigator.clipboard.writeText(rawCode);
  };

  const handleDownload = () => {
    const blob = new Blob([rawCode], { type: isHtml ? 'text/html' : 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `artifact.${isHtml ? 'html' : 'md'}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="h-full w-full min-w-0 flex flex-col bg-surface border-l border-border shadow-2xl animate-in slide-in-from-right duration-300">
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-border shrink-0 bg-zinc-950/60 backdrop-blur-sm">
        <div className="flex items-center gap-3 overflow-hidden">
          <div className="px-2 py-1 rounded bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-[10px] font-semibold uppercase tracking-wider shrink-0">
            {artifact.type || artifact.artifact_type || 'html'}
          </div>
          <h2 className="text-sm font-medium text-zinc-200 truncate">
            {artifact.title || 'Artifact Preview'}
          </h2>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <div className="flex bg-zinc-900 rounded-md p-0.5 border border-border">
            <button
              onClick={() => handleTabSwitch('preview')}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-sm text-xs font-medium transition-colors ${
                viewMode === 'preview' ? 'bg-zinc-800 text-zinc-100 shadow-sm' : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              <Eye className="w-3.5 h-3.5" /> Preview
            </button>
            <button
              onClick={() => handleTabSwitch('code')}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-sm text-xs font-medium transition-colors ${
                viewMode === 'code' ? 'bg-zinc-800 text-zinc-100 shadow-sm' : 'text-zinc-400 hover:text-zinc-200'
              }`}
            >
              <Code className="w-3.5 h-3.5" /> &lt;&gt; Code
            </button>
          </div>

          <div className="w-px h-4 bg-border mx-1"></div>

          <button onClick={handleCopy} className="p-1.5 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 rounded transition-colors" title="Copy code">
            <Copy className="w-4 h-4" />
          </button>
          <button onClick={handleDownload} className="p-1.5 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 rounded transition-colors" title="Download">
            <Download className="w-4 h-4" />
          </button>
          <button onClick={onClose} className="p-1.5 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 rounded transition-colors" title="Close panel">
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Body */}
      <div className="flex-1 overflow-auto bg-[#0a0a0c]">
        {viewMode === 'code' ? (
          <pre className="p-4 text-xs font-mono text-zinc-300 whitespace-pre-wrap selection:bg-indigo-500/30">
            {rawCode}
          </pre>
        ) : (
          <div className="h-full w-full p-4">
            {isHtml ? (
              <div className="w-full h-full bg-[#0f172a] rounded-lg overflow-hidden border border-zinc-800 shadow-xl">
                <iframe
                  key={`preview-${previewKey}`}
                  srcDoc={artifactCode}
                  title="Artifact Preview"
                  sandbox="allow-scripts"
                  className="w-full h-full border-0"
                />
              </div>
            ) : (
              <div className="prose prose-invert max-w-3xl mx-auto p-4">
                <ReactMarkdown>{rawCode}</ReactMarkdown>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
