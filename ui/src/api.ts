import type { Health, JobEvent, JobRequest, JobStatus, ProviderInfo, ScanRequest, ScanResponse } from "./types";

const demoProviders: ProviderInfo[] = [
  { id: "local", label: "Local folder", status: "ok", implemented: true },
  { id: "dropbox", label: "Dropbox", status: "ok", implemented: true },
  { id: "google-drive", label: "Google Drive", status: "ok", implemented: true },
  { id: "s3", label: "S3 / R2", status: "ok", implemented: true },
  { id: "onedrive", label: "OneDrive", status: "planned", implemented: false },
  { id: "yadisk", label: "Yandex Disk", status: "planned", implemented: false },
  { id: "box", label: "Box", status: "planned", implemented: false },
];

const demoHealth: Health = {
  status: "ok",
  version: "0.1.0",
  python_version: "3.12.11",
  recommended_python: "3.11 or 3.12",
  available_providers: demoProviders,
  pillow_webp_support: true,
  pillow_avif_support: true,
  dropbox_sdk_version: "12.0.2",
  credentials: {
    dropbox: true,
    google_drive: true,
    s3: true,
  },
};

const demoJobs: JobStatus[] = [
  {
    job_id: "demo-job-20260516",
    status: "running",
    source: "https://www.dropbox.com/scl/fo/demo-raw-shoot",
    provider: "dropbox",
    output_dir: "web_export",
    total_files: 128,
    processed_files: 84,
    skipped_files: 9,
    failed_files: 2,
    started_at: "2026-05-16T13:42:00Z",
    current_file: "campaign/hero/DSC04218.ARW",
    progress: 66,
  },
];

const demoEvents: JobEvent[] = [
  { id: 1, level: "info", message: "Detected Dropbox folder and started scan.", payload: {}, created_at: "13:42:01" },
  { id: 2, level: "info", message: "Converted DSC04192.CR3 to webp and jpg.", payload: {}, created_at: "13:43:18" },
  { id: 3, level: "warning", message: "Retrying DSC04207.NEF after transient download error.", payload: {}, created_at: "13:44:03" },
  { id: 4, level: "info", message: "Generated responsive variants for campaign/hero/DSC04218.ARW.", payload: {}, created_at: "13:45:27" },
];

const demoScan: ScanResponse = {
  job_preview_id: "demo-preview",
  provider: "dropbox",
  files_count: 128,
  total_size: 18432000000,
  folders_count: 7,
  unsupported_files_count: 3,
  warnings: ["3 sidecar files will be skipped because they are not supported RAW formats."],
  first_files: [
    { path: "campaign/hero/DSC04192.CR3", name: "DSC04192.CR3", size: 62200000, provider: "dropbox" },
    { path: "campaign/hero/DSC04218.ARW", name: "DSC04218.ARW", size: 48700000, provider: "dropbox" },
    { path: "lookbook/set-02/IMG_2814.NEF", name: "IMG_2814.NEF", size: 54100000, provider: "dropbox" },
  ],
};

const demoReport: Record<string, unknown> = {
  processed: 84,
  output_files_count: 168,
  failed: 2,
  estimated_saved_bytes: 4928300000,
  paths: {
    output_dir: "web_export",
    manifest: "web_export/rawbridge_manifest.json",
    failed_tsv: "web_export/rawbridge_failed.tsv",
    errors_csv: "web_export/errors.csv",
  },
};

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

const liveApi = {
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

const demoApi = {
  health: async () => demoHealth,
  providers: async () => demoProviders,
  scan: async (_payload: ScanRequest) => demoScan,
  createJob: async (_payload: JobRequest) => ({ job_id: demoJobs[0].job_id, status: demoJobs[0].status }),
  jobs: async () => demoJobs,
  job: async (_jobId: string) => demoJobs[0],
  events: async (_jobId: string) => demoEvents,
  failed: async (_jobId: string) => [
    { rel_path: "lookbook/set-04/IMG_3321.RAF", error: "Unsupported compression mode" },
    { rel_path: "campaign/backup/DSC03988.CR2", error: "Checksum mismatch after download retry" },
  ],
  report: async (_jobId: string) => demoReport,
  cancel: async (_jobId: string) => ({ status: "cancelled" }),
  resume: async (_jobId: string) => ({ status: "running" }),
  retryFailed: async (_jobId: string) => ({ status: "queued" }),
};

export const api = import.meta.env.VITE_DEMO_MODE === "true" ? demoApi : liveApi;
