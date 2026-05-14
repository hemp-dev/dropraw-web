export type ProviderId = "auto" | "local" | "dropbox" | "google-drive" | "s3" | "onedrive" | "yadisk" | "box";

export type ProviderInfo = {
  id: string;
  label: string;
  status: string;
  implemented: boolean;
};

export type Health = {
  status: string;
  version: string;
  python_version: string;
  python_version_warning?: string | null;
  recommended_python: string;
  available_providers: ProviderInfo[];
  pillow_webp_support: boolean;
  pillow_avif_support: boolean;
  dropbox_sdk_version?: string | null;
  credentials: Record<string, boolean>;
};

export type ScanRequest = {
  source: string;
  provider: ProviderId;
  list_retries: number;
  download_retries: number;
  retry_delay: number;
  cooldown: number;
};

export type FilePreview = {
  path: string;
  name: string;
  size?: number | null;
  provider: string;
};

export type ScanResponse = {
  job_preview_id: string;
  provider: string;
  files_count: number;
  total_size: number;
  folders_count: number;
  first_files: FilePreview[];
  unsupported_files_count: number;
  warnings: string[];
};

export type JobRequest = ScanRequest & {
  output_dir: string;
  preset: string;
  formats: string[] | null;
  quality: number | null;
  max_size: number | null;
  responsive_sizes: number[] | null;
  overwrite: boolean;
  resume: boolean;
  only_failed?: string | null;
  metadata_mode: "strip" | "keep-color" | "keep-all";
};

export type JobStatus = {
  job_id: string;
  status: string;
  source?: string | null;
  provider?: string | null;
  output_dir?: string | null;
  total_files: number;
  processed_files: number;
  skipped_files: number;
  failed_files: number;
  started_at?: string | null;
  finished_at?: string | null;
  current_file?: string | null;
  progress: number;
};

export type JobEvent = {
  id?: number | null;
  level: string;
  message: string;
  payload: Record<string, unknown>;
  created_at?: string | null;
};
