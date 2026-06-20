import { useRef } from "react";

/**
 * Sidebar.jsx
 * ------------
 * Shows the list of uploaded documents (like a file tree) and the
 * upload control. This is a SEPARATE component from App.jsx so each
 * file has one clear job - Sidebar only cares about documents and
 * uploading, it doesn't know anything about chat messages.
 *
 * Props (data passed in from the parent component, App.jsx):
 *   documents        - array of filenames already uploaded
 *   selectedDocument - the filename currently selected as a filter ("" = all)
 *   onSelectDocument - function to call when the user picks a different doc
 *   onUpload         - function to call with the chosen file when "Upload" is clicked
 *   uploading        - true while an upload is in progress (shows a spinner state)
 */
function Sidebar({
  documents,
  selectedDocument,
  onSelectDocument,
  onUpload,
  uploading,
}) {
  // a ref lets us click a hidden <input type="file"> programmatically
  // when the user clicks our custom-styled "Upload" button
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      onUpload(file);
    }
    // reset so the same file can be re-selected later if needed
    e.target.value = "";
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <span className="sidebar-logo">▸_</span>
        <span className="sidebar-title">doc-assistant</span>
      </div>

      {/* hidden native file input, triggered by the styled button below */}
      <input
        ref={fileInputRef}
        type="file"
        accept="application/pdf"
        onChange={handleFileChange}
        style={{ display: "none" }}
      />

      <button
        className="upload-btn"
        onClick={() => fileInputRef.current.click()}
        disabled={uploading}
      >
        {uploading ? (
          <>
            <span className="spinner" /> indexing...
          </>
        ) : (
          <>+ upload pdf</>
        )}
      </button>

      <div className="sidebar-section-label">documents</div>

      <div className="doc-list">
        <button
          className={`doc-item ${selectedDocument === "" ? "active" : ""}`}
          onClick={() => onSelectDocument("")}
        >
          <span className="doc-icon">◆</span>
          all documents
        </button>

        {documents.length === 0 && (
          <div className="doc-empty">no documents yet</div>
        )}

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
