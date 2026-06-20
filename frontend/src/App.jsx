import { useState, useEffect, useRef } from "react";
import axios from "axios";
import Sidebar from "./components/Sidebar";
import ChatMessage from "./components/ChatMessage";
import ChatInput from "./components/ChatInput";
import "./App.css";

/**
 * App.jsx
 * --------
 * The top-level component. It holds the STATE (messages, documents,
 * loading flags) and passes pieces of it down to the smaller
 * components (Sidebar, ChatMessage, ChatInput) as props.
 *
 * Think of this file as the "brain" - it decides WHAT happens.
 * The components decide HOW it looks.
 */
function App() {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [selectedDocument, setSelectedDocument] = useState("");

  // used to auto-scroll to the latest message
  const bottomRef = useRef(null);

  // load the document list once when the app first mounts
  useEffect(() => {
    fetchDocuments();
  }, []);

  // auto-scroll whenever a new message is added
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const fetchDocuments = () => {
    axios.get("http://localhost:8000/documents").then((res) => {
      setDocuments(res.data.documents);
    });
  };

  const handleUpload = async (file) => {
    const formData = new FormData();
    formData.append("file", file);

    setUploading(true);
    try {
      const res = await axios.post("http://localhost:8000/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      // refresh the sidebar's document list so the new file shows up
      fetchDocuments();

      // drop a small system-style note into the chat confirming the upload
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `indexed "${file.name}" — ${res.data.chunks} chunks ready to search.`,
        },
      ]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `upload failed for "${file.name}". check the backend logs.`,
        },
      ]);
    } finally {
      setUploading(false);
    }
  };

  const handleSend = async (text) => {
    const userMessage = { role: "user", content: text };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const res = await axios.post("http://localhost:8000/chat", {
        message: text,
        document: selectedDocument || null,
      });

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: res.data.response,
          sources: res.data.sources,
        },
      ]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "something went wrong — check the backend is running." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <Sidebar
        documents={documents}
        selectedDocument={selectedDocument}
        onSelectDocument={setSelectedDocument}
        onUpload={handleUpload}
        uploading={uploading}
      />

      <main className="chat-pane">
        <div className="chat-topbar">
          <span className="chat-topbar-label">
            {selectedDocument ? selectedDocument : "all documents"}
          </span>
        </div>

        <div className="chat-scroll">
          <div className="chat-scroll-inner">
            {messages.length === 0 && (
              <div className="empty-state">
                <p className="empty-state-title">no messages yet</p>
                <p className="empty-state-sub">
                  upload a pdf on the left, then ask a question about it.
                </p>
              </div>
            )}

            {messages.map((msg, i) => (
              <ChatMessage
                key={i}
                role={msg.role}
                content={msg.content}
                sources={msg.sources}
              />
            ))}

            {loading && (
              <ChatMessage role="assistant" content="thinking..." />
            )}

            <div ref={bottomRef} />
          </div>
        </div>

        <ChatInput onSend={handleSend} loading={loading} />
      </main>
    </div>
  );
}

export default App;
