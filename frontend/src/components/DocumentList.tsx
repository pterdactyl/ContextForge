import { useEffect, useState } from "react";
import { getDocuments, deleteDocument } from "../services/api";
import type { Document } from "../types/document";

interface DocumentListProps {
  refreshKey: number;
}

export default function DocumentList({
  refreshKey,
}: DocumentListProps) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadDocuments() {
    try {
      setError("");
      const data = await getDocuments();
      setDocuments(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load documents"
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadDocuments();
  }, [refreshKey]);

  async function handleDelete(id: number) {
    if (!window.confirm("Delete this document?")) return;

    try {
      await deleteDocument(id);
      setDocuments((prev) => prev.filter((doc) => doc.id !== id));
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to delete document"
      );
    }
  }

  return (
    <section className="panel">
      <div className="panel-header">
        <h3>Your Documents</h3>
        <button
          className="btn btn-ghost"
          onClick={() => void loadDocuments()}
        >
          Refresh
        </button>
      </div>

      {loading && <p className="muted">Loading documents...</p>}
      {error && <p className="alert" role="alert">{error}</p>}

      {!loading && !error && documents.length === 0 && (
        <p className="muted">No documents uploaded yet.</p>
      )}

      <ul className="doc-list">
        {documents.map((doc) => (
          <li className="doc-item" key={doc.id}>
            <span className="doc-name">{doc.filename}</span>
            <button
              className="btn btn-danger"
              onClick={() => void handleDelete(doc.id)}
            >
              Delete
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
