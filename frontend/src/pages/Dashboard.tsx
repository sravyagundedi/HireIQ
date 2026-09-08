import { useEffect, useState } from "react";
import { api, downloadReport } from "../api";

export default function Dashboard() {
  const [data, setData] = useState<any>({ items: [], total: 0 });
  const [selected, setSelected] = useState<any>(null);
  const [error, setError] = useState("");

  async function load() {
    try {
      setData(await api("/api/dashboard/candidates?page=1&page_size=20"));
    } catch (e: any) {
      setError(e.message);
    }
  }

  async function select(id: number) {
    try {
      setSelected(await api(`/api/dashboard/interviews/${id}`));
    } catch (e: any) {
      setError(e.message);
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <section>
      <div className="row space">
        <div>
          <h2>Hiring Manager Dashboard</h2>
          <p className="muted">Candidate comparison and evaluation review.</p>
        </div>
        <button onClick={load}>Refresh</button>
      </div>

      {error && <p className="message">{error}</p>}

      <div className="card table-wrap">
        <table>
          <thead>
            <tr>
              <th>Candidate</th>
              <th>Email</th>
              <th>Status</th>
              <th>Score</th>
              <th>Recommendation</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {data.items.map((x: any) => (
              <tr key={x.interview_id}>
                <td>{x.candidate_name}</td>
                <td>{x.email}</td>
                <td>{x.status}</td>
                <td>{x.score == null ? "—" : `${x.score.toFixed(2)}/10`}</td>
                <td><span className="badge">{x.recommendation || "Pending"}</span></td>
                <td><button onClick={() => select(x.interview_id)}>View</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selected && (
        <div className="card detail">
          <div className="row space">
            <div>
              <h2>{selected.interview.candidate}</h2>
              <p>{selected.interview.email}</p>
            </div>
            <button onClick={() => downloadReport(selected.interview.id)}>Download PDF</button>
          </div>

          <div className="score-box">
            <strong>Overall: {selected.interview.score?.toFixed(2) ?? "Pending"}/10</strong>
            <span>{selected.interview.recommendation || "Pending"}</span>
          </div>

          {selected.responses.map((r: any, i: number) => (
            <article className="response" key={r.id}>
              <h3>Question {i + 1}</h3>
              <p><strong>{r.question}</strong></p>
              <p><strong>Transcript:</strong> {r.transcript || "Processing..."}</p>
              <div className="chips">
                {(r.keywords || []).map((k: string) => <span key={k}>{k}</span>)}
              </div>
              <p>Score: {r.score == null ? "Pending" : `${r.score}/10`} · Confidence signal: {r.confidence ?? "—"}</p>
              <p>Sentiment: {JSON.stringify(r.sentiment)}</p>
              <p><strong>Strengths:</strong> {(r.strengths || []).join(", ") || "—"}</p>
              <p><strong>Weaknesses:</strong> {(r.weaknesses || []).join(", ") || "—"}</p>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
