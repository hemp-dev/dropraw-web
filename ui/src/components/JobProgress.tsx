import { Pause, RotateCcw } from "lucide-react";
import type { JobEvent, JobStatus } from "../types";
import { ProgressBar } from "./ProgressBar";
import { StatusBadge } from "./StatusBadge";

type Props = {
  job?: JobStatus;
  events: JobEvent[];
  onCancel: () => void;
  onResume: () => void;
  onRetryFailed: () => void;
};

export function JobProgress({ job, events, onCancel, onResume, onRetryFailed }: Props) {
  if (!job) {
    return (
      <section className="rounded-lg border border-line bg-white p-5 text-sm text-slate-500 shadow-sm">
        Start a conversion job to see live progress, retry events, and errors.
      </section>
    );
  }
  return (
    <section className="rounded-lg border border-line bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-base font-semibold text-ink">Job Progress</h2>
          <p className="text-sm text-slate-500">{job.job_id}</p>
        </div>
        <StatusBadge status={job.status} />
      </div>
      <div className="mt-4">
        <ProgressBar value={job.progress} />
        <div className="mt-2 grid gap-2 text-sm text-slate-600 md:grid-cols-4">
          <span>Processed: {job.processed_files}</span>
          <span>Skipped: {job.skipped_files}</span>
          <span>Failed: {job.failed_files}</span>
          <span>Total: {job.total_files}</span>
        </div>
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        <button className="focus-ring inline-flex items-center gap-2 rounded border border-line bg-white px-3 py-2 text-sm" onClick={onCancel} type="button">
          <Pause size={16} /> Cancel
        </button>
        <button className="focus-ring inline-flex items-center gap-2 rounded border border-line bg-white px-3 py-2 text-sm" onClick={onResume} type="button">
          <RotateCcw size={16} /> Resume
        </button>
        <button className="focus-ring inline-flex items-center gap-2 rounded bg-red-600 px-3 py-2 text-sm font-medium text-white" onClick={onRetryFailed} type="button">
          <RotateCcw size={16} /> Retry failed
        </button>
      </div>
      <div className="mt-4 max-h-72 overflow-auto rounded border border-line bg-slate-950 p-3 font-mono text-xs text-slate-100">
        {events.length === 0 ? <div>No events yet</div> : events.map((event, index) => <div key={`${event.id || index}-${event.message}`} className={event.level === "error" ? "text-red-300" : event.level === "warning" ? "text-amber-200" : "text-slate-100"}>{event.created_at ? `${event.created_at} ` : ""}{event.message}</div>)}
      </div>
    </section>
  );
}
