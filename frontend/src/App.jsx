import { useState, useEffect, useRef } from "react";
import axios from "axios";
import Sidebar from "./components/Sidebar";
import ChatMessage from "./components/ChatMessage";
import ChatInput from "./components/ChatInput";
import ContextPanel from "./components/ContextPanel";
import "./App.css";
import TypingIndicator from "./components/TypingIndicator";
/**
 * SESSION ID — created once, then REUSED across refreshes.
 *
 * Before: crypto.randomUUID() ran fresh every time the page loaded,
 * so every refresh = a brand new session = backend forgets everything.
 *
 * Now: we check localStorage first (a small storage built into every
 * browser that SURVIVES refreshes, unlike React state). If a session
 * id is already saved there, reuse it. Only generate a new one the
 * very first time this browser ever opens the app.
 */

const API_URL = import.meta.env.VITE_API_URL;

function getOrCreateSessionId() {
  const existing = localStorage.getItem("doc_assistant_session_id");
  if (existing) return existing;

  const fresh = crypto.randomUUID();
  localStorage.setItem("doc_assistant_session_id", fresh);
  return fresh;
}

const sessionId = getOrCreateSessionId();

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
  const [latestChunks, setLatestChunks] = useState(null); // for the context panel

  // used to auto-scroll to the latest message
  const bottomRef = useRef(null);

  // load the document list once when the app first mounts
  useEffect(() => {
    fetchDocuments();
    restoreHistory();
  }, []);

  // auto-scroll whenever a new message is added
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const fetchDocuments = () => {
    axios.get(`${API_URL}/documents`).then((res) => {
      setDocuments(res.data.documents);
    });
  };

  const restoreHistory = async () => {
    try {
      const res = await axios.get(`${API_URL}/history/${sessionId}`);
      // backend stores history as [{role, content, sources?}, ...] -
      // that's already the same shape our messages state uses, so we
      // can drop it straight in, source tags included.
      if (res.data.history && res.data.history.length > 0) {
        setMessages(res.data.history);
      }
      // restore the context panel too, so a refresh doesn't wipe it
      if (res.data.latest_context && res.data.latest_context.length > 0) {
        setLatestChunks(res.data.latest_context);
      }
    } catch (err) {
      // no history yet for this session is expected on first-ever visit
      console.log("no previous history to restore");
    }
  };

const handleUpload = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  setUploading(true);
  try {
    const res = await axios.post(`${API_URL}/upload`, formData, {
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
    const detail = err.response?.data?.detail || `upload failed for "${file.name}". check the backend logs.`;
    setMessages((prev) => [
      ...prev,
      {
        role: "assistant",
        content: detail,
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
      const res = await axios.post(`${API_URL}/chat`, {
        message: text,
        document: selectedDocument || null,
        session_id: sessionId, // tells the backend which conversation this is
      });

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: res.data.response,
          sources: res.data.sources,
        },
      ]);

      // update the context panel with what was retrieved for THIS answer
      setLatestChunks(res.data.retrieved_chunks || []);
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
            {selectedDocument ? selectedDocument : "All Documents"}
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

            {loading && <TypingIndicator />}

            <div ref={bottomRef} />
          </div>
        </div>

        <ChatInput onSend={handleSend} loading={loading} />
      </main>

      <ContextPanel chunks={latestChunks} />
    </div>
  );
}

export default App;
