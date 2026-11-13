import { useState } from "react";
import type { ChangeEvent } from "react";
import { uploadDocument } from "../services/api";

interface DocumentUploadProps {
  onUploadSuccess: () => void;
}

export default function DocumentUpload({
  onUploadSuccess,
}: DocumentUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState("");
  const [tone, setTone] = useState<"info" | "success" | "error">("info");
  const [loading, setLoading] = useState(false);

  function handleFileChange(
    event: ChangeEvent<HTMLInputElement>
  ) {
    const selectedFile = event.target.files?.[0];

    if (selectedFile) {
      setFile(selectedFile);
      setStatus("");
    }
  }

  async function handleUpload() {
    if (!file) return;

    setLoading(true);
    setTone("info");
    setStatus("Uploading document...");

    try {
      await uploadDocument(file);
      setTone("success");
      setStatus("Document uploaded successfully!");
      setFile(null);
      onUploadSuccess();
    } catch (error) {
      setTone("error");
      setStatus(
        error instanceof Error
          ? error.message
          : "Upload failed"
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="panel">
      <h3>Upload Document</h3>

      <div className="upload-form">
        <input
          type="file"
          accept=".pdf,.txt"
          onChange={handleFileChange}
        />

        <button
          className="btn btn-primary"
          onClick={handleUpload}
          disabled={!file || loading}
        >
          {loading ? "Uploading..." : "Upload"}
        </button>
      </div>

      {status && (
        <p className={`status status-${tone}`}>{status}</p>
      )}
    </div>
  );
}
