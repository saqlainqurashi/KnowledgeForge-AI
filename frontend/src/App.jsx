
import { useEffect, useState } from "react";
import logo from "./assets/knowledgeforge-logo.png";
import {
  askQuestion,
  uploadDocument,
  getDocuments,
  deleteDocument,
} from "./services/api";
import "./App.css";

export default function App() {
  const [documents, setDocuments] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [loadingDocuments, setLoadingDocuments] = useState(true);
  const [deletingId, setDeletingId] = useState(null);

  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [asking, setAsking] = useState(false);
  const [chatError, setChatError] = useState("");

  // Load stored documents when the dashboard opens.
  useEffect(() => {
    let active = true;

    async function loadDocuments() {
      try {
        const data = await getDocuments();

        if (active) {
          setDocuments(
            data.documents.map((document) => ({
              id: document.id,
              filename: document.filename,
              chunks: document.total_chunks,
            }))
          );
        }
      } catch (error) {
        if (active) {
          setUploadError(error.message);
        }
      } finally {
        if (active) {
          setLoadingDocuments(false);
        }
      }
    }

    loadDocuments();

    return () => {
      active = false;
    };
  }, []);

  // Upload a PDF or TXT document.
  async function handleUpload(event) {
    event.preventDefault();

    if (!selectedFile || uploading) return;

    setUploading(true);
    setUploadError("");

    try {
      const result = await uploadDocument(selectedFile);

      setDocuments((previous) => [
        {
          id: result.document_id,
          filename: result.filename,
          chunks: result.total_chunks,
        },
        ...previous.filter(
          (document) => document.id !== result.document_id
        ),
      ]);

      setSelectedFile(null);
      event.currentTarget.reset();
    } catch (error) {
      setUploadError(error.message);
    } finally {
      setUploading(false);
    }
  }

  // Delete a document and its stored chunks.
  async function handleDelete(documentId) {
    const confirmed = window.confirm(
      "Delete this document and all its stored chunks?"
    );

    if (!confirmed) return;

    setDeletingId(documentId);
    setUploadError("");

    try {
      await deleteDocument(documentId);

      setDocuments((previous) =>
        previous.filter(
          (document) => document.id !== documentId
        )
      );
    } catch (error) {
      setUploadError(error.message);
    } finally {
      setDeletingId(null);
    }
  }

  // Ask a question using the RAG backend.
  async function handleAsk(event) {
    event.preventDefault();

    const currentQuestion = question.trim();

    if (!currentQuestion || asking) return;

    setQuestion("");
    setChatError("");
    setAsking(true);

    setMessages((previous) => [
      ...previous,
      {
        id: crypto.randomUUID(),
        role: "user",
        content: currentQuestion,
      },
    ]);

    try {
      const result = await askQuestion(currentQuestion);

      setMessages((previous) => [
        ...previous,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content: result.answer,
          sources: result.sources || [],
        },
      ]);
    } catch (error) {
      setChatError(error.message);
    } finally {
      setAsking(false);
    }
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        {/* Branding */}
        <div className="brand">
          <img
            src={logo}
            alt="KnowledgeForge AI logo"
            className="brand-logo"
          />

          <div>
            <strong>KnowledgeForge AI</strong>
            <small>Knowledge Workspace</small>
          </div>
        </div>

        {/* Document upload */}
        <div className="sidebar-section">
          <h2>Documents</h2>
          <p>Upload knowledge sources for your assistant.</p>

          <form
            onSubmit={handleUpload}
            className="upload-form"
          >
            <label className="file-picker">
              <span>Choose PDF or TXT</span>

              <input
                type="file"
                accept=".pdf,.txt"
                onChange={(event) =>
                  setSelectedFile(
                    event.target.files?.[0] || null
                  )
                }
              />
            </label>

            {selectedFile && (
              <p className="selected-file">
                {selectedFile.name}
              </p>
            )}

            <button
              type="submit"
              disabled={!selectedFile || uploading}
              className="primary-button"
            >
              {uploading
                ? "Processing document..."
                : "Upload Document"}
            </button>
          </form>

          {uploadError && (
            <p
              className="error-message"
              role="alert"
            >
              {uploadError}
            </p>
          )}
        </div>

        {/* Persistent document list */}
        <div className="sidebar-section document-list">
          <h3>Knowledge Base Documents</h3>

          {loadingDocuments ? (
            <p className="muted">
              Loading documents...
            </p>
          ) : documents.length === 0 ? (
            <p className="muted">
              No documents uploaded yet.
            </p>
          ) : (
            documents.map((document) => (
              <div
                className="document-item"
                key={document.id}
              >
                <span className="document-icon">
                  📄
                </span>

                <div className="document-details">
                  <strong>
                    {document.filename}
                  </strong>

                  <small>
                    {document.chunks} chunks indexed
                  </small>
                </div>

                <button
                  type="button"
                  className="delete-button"
                  disabled={
                    deletingId !== null
                  }
                  onClick={() =>
                    handleDelete(document.id)
                  }
                  aria-label={
                    `Delete ${document.filename}`
                  }
                >
                  {deletingId === document.id
                    ? "Deleting..."
                    : "Delete"}
                </button>
              </div>
            ))
          )}
        </div>
      </aside>

      {/* Main workspace */}
      <main className="workspace">
        <header className="workspace-header">
          <div>
            <h1>Ask your knowledge base</h1>
            <p>
              Get answers grounded in your
              uploaded documents.
            </p>
          </div>

          <span className="status-pill">
            RAG Assistant
          </span>
        </header>

        <section
          className="chat-area"
          aria-label="Conversation"
        >
          {messages.length === 0 && (
            <div className="welcome-state">
              <div className="welcome-icon">
                ✦
              </div>

              <h2>
                What would you like to know?
              </h2>

              <p>
                Upload a document and ask a question.
                KnowledgeForge will retrieve relevant
                passages and generate an answer.
              </p>
            </div>
          )}

          {messages.map((message) => (
            <article
              key={message.id}
              className={
                `message message-${message.role}`
              }
            >
              <div className="message-label">
                {message.role === "user"
                  ? "You"
                  : "KnowledgeForge AI"}
              </div>

              <div className="message-content">
                {message.content}
              </div>

              {message.sources?.length > 0 && (
                <div className="sources">
                  <h4>Retrieved sources</h4>

                  {message.sources.map(
                    (source) => (
                      <details
                        key={
                          `${message.id}-${source.source_number}`
                        }
                        className="source-item"
                      >
                        <summary>
                          [{source.source_number}]{" "}
                          {source.filename}

                          <span>
                            {Math.round(
                              source.similarity * 100
                            )}
                            % similarity
                          </span>
                        </summary>

                        <p>
                          {source.snippet ||
                            "Preview unavailable."}
                        </p>
                      </details>
                    )
                  )}
                </div>
              )}
            </article>
          ))}

          {asking && (
            <div
              className="thinking-state"
              role="status"
            >
              Searching documents and generating
              an answer...
            </div>
          )}

          {chatError && (
            <p
              className="error-message"
              role="alert"
            >
              {chatError}
            </p>
          )}
        </section>

        {/* Chat input */}
        <form
          className="chat-composer"
          onSubmit={handleAsk}
        >
          <input
            type="text"
            value={question}
            onChange={(event) =>
              setQuestion(event.target.value)
            }
            placeholder={
              "Ask a question about your documents..."
            }
            disabled={asking}
            aria-label="Your question"
          />

          <button
            type="submit"
            className="primary-button"
            disabled={
              !question.trim() || asking
            }
          >
            {asking ? "Thinking..." : "Ask"}
          </button>
        </form>
      </main>
    </div>
  );
}
