/**
 * ChatMessage.jsx
 * ----------------
 * Renders ONE message in the conversation - either from "you" or "ai".
 * Splitting this out means App.jsx doesn't need to know how a message
 * looks, it just hands over the data.
 *
 * Props:
 *   role    - "user" or "assistant"
 *   content - the message text
 *   sources - optional array of source document names (only assistant
 *             messages have these - they show which PDF the answer
 *             came from, which is the whole point of a RAG app)
 */
function ChatMessage({ role, content, sources }) {
  const isUser = role === "user";

  return (
    <div className={`message-row ${isUser ? "user" : "assistant"}`}>
      <div className="message-avatar">{isUser ? "you" : "ai"}</div>

      <div className="message-bubble">
        <p className="message-text">{content}</p>

        {/* Source tags - styled like terminal file references, e.g. ▸ manual.pdf
            This is the signature visual element: it makes the "grounded in
            your documents" promise of RAG visible, not just claimed. */}
        {sources && sources.length > 0 && (
          <div className="source-tags">
            {sources.map((src) => (
              <span key={src} className="source-tag" title={src}>
                <span className="source-tag-arrow">▸</span>
                <span className="source-tag-name">{src}</span>
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default ChatMessage;
