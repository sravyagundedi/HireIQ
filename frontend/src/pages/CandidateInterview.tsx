import { useEffect, useRef, useState } from "react";
import { api } from "../api";

type Question = {
  id: number;
  text: string;
  question_type: string;
  order_index: number;
};

type StartResponse = {
  interview: any;
  session_id: number;
  questions: Question[];
};

export default function CandidateInterview() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [started, setStarted] = useState(false);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [interviewId, setInterviewId] = useState<number | null>(null);
  const [index, setIndex] = useState(0);
  const [recording, setRecording] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [message, setMessage] = useState("");
  const [transcript, setTranscript] = useState("");
  const [seconds, setSeconds] = useState(120);
  const recorder = useRef<MediaRecorder | null>(null);
  const chunks = useRef<Blob[]>([]);
  const timer = useRef<number | undefined>(undefined);

  const current = questions[index];

  useEffect(() => {
    if (!started || processing) return;
    timer.current = window.setInterval(() => {
      setSeconds((s) => (s > 0 ? s - 1 : 0));
    }, 1000);
    return () => window.clearInterval(timer.current);
  }, [started, processing, index]);

  async function startInterview() {
    if (!name || !email) {
      setMessage("Enter your name and email.");
      return;
    }
    try {
      const candidate = await api<any>("/api/candidates", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email }),
      });

      const interview = await api<any>("/api/interviews", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ candidate_id: candidate.id, title: "AI Technical Interview" }),
      });

      const data = await api<StartResponse>(`/api/interviews/${interview.id}/start`, {
        method: "POST",
      });

      setInterviewId(interview.id);
      setSessionId(data.session_id);
      setQuestions(data.questions);
      setStarted(true);
      setMessage("");
      setSeconds(120);
    } catch (e: any) {
      setMessage(e.message);
    }
  }

  async function startRecording() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mime = MediaRecorder.isTypeSupported("audio/webm")
        ? "audio/webm"
        : "";
      const mr = new MediaRecorder(stream, mime ? { mimeType: mime } : undefined);
      chunks.current = [];
      mr.ondataavailable = (e) => {
        if (e.data.size > 0) chunks.current.push(e.data);
      };
      mr.onstop = () => stream.getTracks().forEach((t) => t.stop());
      recorder.current = mr;
      mr.start();
      setRecording(true);
      setMessage("Recording...");
    } catch {
      setMessage("Microphone permission is required.");
    }
  }

  function stopRecording() {
    recorder.current?.stop();
    setRecording(false);
    setMessage("Recording stopped. Click Submit Answer.");
  }

  async function submitAnswer() {
    if (!sessionId || !current || chunks.current.length === 0) {
      setMessage("Record an answer first.");
      return;
    }

    const blob = new Blob(chunks.current, { type: "audio/webm" });
    const form = new FormData();
    form.append("audio", blob, "answer.webm");

    setProcessing(true);
    setMessage("Uploading and processing with Whisper...");
    try {
      const result = await api<any>(
        `/api/sessions/${sessionId}/responses?question_id=${current.id}`,
        { method: "POST", body: form }
      );

      let done = false;
      while (!done) {
        await new Promise((r) => setTimeout(r, 2000));
        const status = await api<any>(`/api/responses/${result.response_id}`);
        setTranscript(status.transcript || "");
        if (status.status === "completed") {
          done = true;
          setMessage("Answer evaluated successfully.");
        } else if (status.status === "failed") {
          throw new Error("Audio transcription/evaluation failed. Please retry.");
        } else {
          setMessage(`Processing: ${status.status}...`);
        }
      }

      chunks.current = [];
      if (index + 1 < questions.length) {
        setIndex(index + 1);
        setSeconds(120);
        setTranscript("");
        setMessage("Next question.");
      } else {
        await api(`/api/sessions/${sessionId}/finish`, { method: "POST" });
        setMessage("Interview completed. Your evaluation is being finalized.");
        setStarted(false);
      }
    } catch (e: any) {
      setMessage(e.message);
    } finally {
      setProcessing(false);
    }
  }

  if (!started) {
    return (
      <section className="card hero">
        <h2>AI Interview</h2>
        <p>Answer each question using your microphone.</p>
        <input placeholder="Full name" value={name} onChange={(e) => setName(e.target.value)} />
        <input placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
        <button className="primary" onClick={startInterview}>Start Interview</button>
        {message && <p className="message">{message}</p>}
      </section>
    );
  }

  return (
    <section className="card">
      <div className="row space">
        <div>
          <p className="muted">Question {index + 1} of {questions.length}</p>
          <h2>{current?.text}</h2>
          <span className="badge">{current?.question_type}</span>
        </div>
        <div className="timer">{Math.floor(seconds / 60)}:{String(seconds % 60).padStart(2, "0")}</div>
      </div>

      <div className="recorder">
        {!recording ? (
          <button className="primary" disabled={processing} onClick={startRecording}>🎙 Start Recording</button>
        ) : (
          <button className="danger" onClick={stopRecording}>⏹ Stop Recording</button>
        )}
        <button disabled={recording || processing} onClick={submitAnswer}>Submit Answer</button>
      </div>

      {transcript && (
        <div className="transcript">
          <strong>Transcript</strong>
          <p>{transcript}</p>
        </div>
      )}

      {message && <p className="message">{message}</p>}
    </section>
  );
}
