const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API}${path}`, options);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `HTTP ${response.status}`);
  }
  return response.json();
}

export async function downloadReport(interviewId: number) {
  const response = await fetch(`${API}/api/dashboard/interviews/${interviewId}/report`);
  if (!response.ok) throw new Error("Could not generate report");
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `hireiq-report-${interviewId}.pdf`;
  a.click();
  URL.revokeObjectURL(url);
}
