import { useState, useEffect } from "react";

const MESSAGES = [
  "Analyzing your question...",
  "Searching through documents...",
  "Finding relevant context...",
  "Reranking results...",
  "Generating your answer...",
  "Almost There...",
];

function TypingIndicator() {
  const [msgIndex, setMsgIndex] = useState(0);

  useEffect(() => {
  const interval = setInterval(() => {
    setMsgIndex((prev) => {
      if (prev >= MESSAGES.length - 1) {
        clearInterval(interval); // stop the interval entirely
        return prev;
      }
      return prev + 1;
    });
  }, 2000);

  return () => clearInterval(interval);
}, []);


  return (
    <div className="message-row assistant">
      <div className="message-avatar">ai</div>
      <div className="message-bubble typing-bubble">
        <div className="typing-dots">
          <span className="typing-dot" />
          <span className="typing-dot" />
          <span className="typing-dot" />
        </div>
        <span className="typing-status">{MESSAGES[msgIndex]}</span>
      </div>
    </div>
  );
}

export default TypingIndicator;