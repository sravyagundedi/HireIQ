import { useState } from "react";
import CandidateInterview from "./pages/CandidateInterview";
import Dashboard from "./pages/Dashboard";

export default function App() {
  const [page, setPage] = useState<"interview" | "dashboard">("interview");

  return (
    <div>
      <header className="topbar">
        <div>
          <h1>HireIQ</h1>
          <span>Multimodal AI Interview Intelligence</span>
        </div>
        <nav>
          <button onClick={() => setPage("interview")}>Candidate</button>
          <button onClick={() => setPage("dashboard")}>Manager Dashboard</button>
        </nav>
      </header>

      <main className="container">
        {page === "interview" ? <CandidateInterview /> : <Dashboard />}
      </main>
    </div>
  );
}
