import { useEffect, useState } from "react";
import { API_URL } from "./services/api";

export default function App() {
  const [status, setStatus] = useState("Checking backend...");

  useEffect(() => {
    fetch(`${API_URL}/health`)
      .then((response) => {
        if (!response.ok) {
          throw new Error("Backend unavailable");
        }
        return response.json();
      })
      .then((data) => setStatus(data.status))
      .catch(() => setStatus("Connection failed"));
  }, []);

  return (
    <main style={{ padding: "40px" }}>
      <h1>KnowledgeForge AI</h1>
      <p>Backend status: {status}</p>
    </main>
  );
}