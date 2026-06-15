import { useState, useEffect } from "react";
import axios from "axios";

function App() {
  const [messages, setMessages] = useState([]);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false); // track API request state
  const [documents, setDocuments] = useState([]);
  const [selectedDocument, setSelectedDocument] = useState("");
  const [response, setResponse] = useState("");
  // load documents
  useEffect(() => {
    axios.get("http://localhost:8000/documents")
      .then((res) => {
        setDocuments(res.data.documents);
      });
  }, []);

const sendMessage = async () => {

  if (!message.trim()) return;

  const userMessage = {
    role: "user",
    content: message
  };

  setMessages(prev => [...prev, userMessage]);

  setMessage("");

  try {

    setLoading(true); // show loading indicator

    const res = await axios.post(
      "http://localhost:8000/chat",
      {
        message,
        document: selectedDocument || null
      }
    );

    const aiMessage = {
      role: "assistant",
      content: res.data.response,
      sources: res.data.sources
    };

    setMessages(prev => [...prev, aiMessage]);

  } catch (err) {

    console.error(err);

  } finally {

    setLoading(false); // hide loading indicator

  }
};

  return (
    <div style={{ padding: "20px" }}>

      <h1>AI Docs Assistant</h1>

      {/* document selector */}
      <select
        value={selectedDocument}
        onChange={(e) => setSelectedDocument(e.target.value)}
      >
        <option value="">All Documents</option>

        {documents.map((doc) => (
          <option key={doc} value={doc}>
            {doc}
          </option>
        ))}
      </select>

      <br /><br />

      {/* question input */}

        <div className="input-container">

  <textarea
    rows={3}
    value={message}
    onChange={(e) => setMessage(e.target.value)}
    placeholder="Ask a question..."
  />

<button
  onClick={sendMessage}
  disabled={loading}
>
  {loading ? "Thinking..." : "Send"}
</button>

</div>

      <br />


      <hr />

<div className="chat-container">

  {messages.map((msg, index) => (
    <div
      key={index}
      className={
        msg.role === "user"
          ? "user-message"
          : "assistant-message"
      }
    >
      <strong>
        {msg.role === "user" ? "You" : "AI"}
      </strong>

      <p>{msg.content}</p>

      {msg.sources && (
        <div>
          {msg.sources.map(source => (
            <span
              key={source}
              className="source-badge"
            >
              {source}
            </span>
          ))}
        </div>
      )}
    </div>
  ))}

  {/* Loading indicator */}
  {loading && (
    <div className="assistant-message">
      <strong>AI</strong>
      <p>Thinking...</p>
    </div>
  )}

</div>

    </div>
  );
}

export default App;