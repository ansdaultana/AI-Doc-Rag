import { useState } from "react";

/**
 * ChatInput.jsx
 * --------------
 * The text box + send button at the bottom of the chat.
 * Keeps its OWN local state for what's currently typed (draft text),
 * and only hands the finished message up to App.jsx when "Send" is clicked.
 *
 * Props:
 *   onSend  - function called with the message text when the user sends
 *   loading - true while waiting for the AI's response (disables input)
 */
function ChatInput({ onSend, loading }) {
  const [draft, setDraft] = useState("");

  const handleSend = () => {
    if (!draft.trim()) return;
    onSend(draft);
    setDraft("");
  };

  // Enter sends, Shift+Enter makes a new line - standard chat-app behavior
  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-input-bar">
      <textarea
        className="chat-input"
        rows={1}
        placeholder="ask something about your documents..."
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={loading}
      />
      <button
        className="send-btn"
        onClick={handleSend}
        disabled={loading || !draft.trim()}
      >
        {loading ? <span className="spinner" /> : "Send ↵"}
      </button>
    </div>
  );
}

export default ChatInput;
