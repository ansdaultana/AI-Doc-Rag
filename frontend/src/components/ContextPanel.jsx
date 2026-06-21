/**
 * ContextPanel.jsx
 * -----------------
 * Shows the actual document chunks that were retrieved and sent to
 * the AI for the MOST RECENT question. This makes the RAG pipeline's
 * "thinking" visible - instead of just trusting the AI's answer, you
 * can see exactly which pieces of your document it was looking at.
 *
 * Props:
 *   chunks - array of { source, chunk, content } objects, or null if
 *            no question has been asked yet
 */
function ContextPanel({ chunks }) {
  return (
    <aside className="context-panel">
      <div className="context-panel-header">
        <span className="sidebar-logo">▸_</span>
        <span className="context-panel-title">retrieved context</span>
        {chunks && chunks.length > 0 && (
          <span className="context-panel-count">{chunks.length}</span>
        )}
      </div>

      {(!chunks || chunks.length === 0) && (
        <div className="context-empty">
          <p>Ask a question to see which document chunks the AI used to answer!</p>
        </div>
      )}

      <div className="context-list">
        {chunks?.map((item, i) => (
          <div key={i} className="context-card">
            <div className="context-card-header">
              <span className="context-card-arrow">▸</span>
              <span className="context-card-source" title={item.source}>
                {item.source}
              </span>
              <span className="context-card-chunk">#{item.chunk}</span>
            </div>
            <p className="context-card-text">{item.content}</p>
          </div>
        ))}
      </div>
    </aside>
  );
}

export default ContextPanel;