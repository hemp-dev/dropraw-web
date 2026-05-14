import type { Health, JobEvent, JobRequest, JobStatus, ProviderInfo, ScanRequest, ScanResponse } from "./types";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options?.headers || {}) },
    ...options,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || response.statusText);
  }
  return response.json() as Promise<T>;
}

export const api = {
  health: () => request<Health>("/api/health"),
  providers: () => request<ProviderInfo[]>("/api/providers"),
  scan: (payload: ScanRequest) => request<ScanResponse>("/api/scan", { method: "POST", body: JSON.stringify(payload) }),
  createJob: (payload: JobRequest) => request<{ job_id: string; status: string }>("/api/jobs", { method: "POST", body: JSON.stringify(payload) }),
  jobs: () => request<JobStatus[]>("/api/jobs"),
  job: (jobId: string) => request<JobStatus>(`/api/jobs/${jobId}`),
  events: (jobId: string) => request<JobEvent[]>(`/api/jobs/${jobId}/events`),
  failed: (jobId: string) => request<Array<{ rel_path: string; error: string }>>(`/api/jobs/${jobId}/failed`),
  report: (jobId: string) => request<Record<string, unknown>>(`/api/jobs/${jobId}/report`),
  cancel: (jobId: string) => request<Record<string, unknown>>(`/api/jobs/${jobId}/cancel`, { method: "POST" }),
  resume: (jobId: string) => request<Record<string, unknown>>(`/api/jobs/${jobId}/resume`, { method: "POST" }),
  retryFailed: (jobId: string) => request<Record<string, unknown>>(`/api/jobs/${jobId}/retry-failed`, { method: "POST" }),
};
