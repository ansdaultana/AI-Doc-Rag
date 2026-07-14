import { useRef, useState } from "react";

const MAX_FILE_SIZE_MB = 10;
const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;

function Sidebar({
  documents,
  selectedDocument,
  onSelectDocument,
  onUpload,
  uploading,
  isOpen,
  onClose,
}) {
  const fileInputRef = useRef(null);
  const [uploadError, setUploadError] = useState(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    e.target.value = "";
    if (!file) return;
    if (file.type !== "application/pdf") {
      setUploadError("only PDF files are supported.");
      return;
    }
    if (file.size > MAX_FILE_SIZE_BYTES) {
      setUploadError(`file is too large. maximum size is ${MAX_FILE_SIZE_MB}MB.`);
      return;
    }
    setUploadError(null);
    onUpload(file);
  };

  return (
    <aside className={`sidebar ${isOpen ? "sidebar--open" : ""}`}>
      <div className="sidebar-header">
        <span className="sidebar-logo">▸_</span>
        <span className="sidebar-title">Doc Assistant</span>
        <button className="sidebar-close-btn" onClick={onClose}>✕</button>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept="application/pdf"
        onChange={handleFileChange}
        style={{ display: "none" }}
      />

      <button
        className="upload-btn"
        onClick={() => { setUploadError(null); fileInputRef.current.click(); }}
        disabled={uploading}
      >
        {uploading ? <><span className="spinner" /> indexing...</> : <>+ Upload PDF</>}
      </button>

      {uploadError && <div className="upload-error">{uploadError}</div>}

      <div className="sidebar-section-label">documents</div>

      <div className="doc-list">
        <button
          className={`doc-item ${selectedDocument === "" ? "active" : ""}`}
          onClick={() => onSelectDocument("")}
        >
          <span className="doc-icon">◆</span>
          All Documents
        </button>

        {documents.length === 0 && <div className="doc-empty">no documents yet</div>}

        {documents.map((doc) => (
          <button
            key={doc}
            className={`doc-item ${selectedDocument === doc ? "active" : ""}`}
            onClick={() => onSelectDocument(doc)}
            title={doc}
          >
            <span className="doc-icon">▪</span>
            <span className="doc-name">{doc}</span>
          </button>
        ))}
      </div>
    </aside>
  );
}

export default Sidebar;