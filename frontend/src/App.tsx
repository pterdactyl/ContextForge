import { useState } from "react";
import DocumentUpload from "./components/DocumentUpload";
import DocumentList from "./components/DocumentList";
import Chat from "./components/Chat";
import "./App.css";

function App() {
  const [refreshKey, setRefreshKey] = useState(0);

  function handleUploadSuccess() {
    setRefreshKey((prev) => prev + 1);
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <h2>ContextForge</h2>
        <p className="subtitle">Document Workspace</p>

        <DocumentUpload onUploadSuccess={handleUploadSuccess} />

        <hr className="divider" />

        <DocumentList refreshKey={refreshKey} />
      </aside>

      <main className="main-content">
        <header className="chat-header">
          <h1>Ask ContextForge</h1>
          <p>Ask questions about your uploaded documents.</p>
        </header>

        <Chat />
      </main>
    </div>
  );
}

export default App;
