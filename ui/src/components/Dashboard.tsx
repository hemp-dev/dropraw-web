import type { ReactNode } from "react";
import type { Health, JobStatus } from "../types";
import { StatusBadge } from "./StatusBadge";

type Props = {
  health?: Health;
  jobs: JobStatus[];
  failedCount: number;
};

export function Dashboard({ health, jobs, failedCount }: Props) {
  const last = jobs[0];
  const totals = jobs.reduce(
    (acc, job) => {
      acc.raw += job.processed_files + job.skipped_files + job.failed_files;
      acc.errors += job.failed_files;
      return acc;
    },
    { raw: 0, errors: 0 },
  );
  const metrics = [
    ["Total jobs", jobs.length],
    ["Last job status", last ? <StatusBadge status={last.status} /> : "No jobs"],
    ["RAW processed", totals.raw],
    ["Output files", jobs.reduce((acc, job) => acc + job.processed_files, 0)],
    ["Space saved", "See reports"],
    ["Errors", totals.errors],
    ["Failed files pending retry", failedCount],
  ] satisfies Array<[string, ReactNode]>;
  return (
    <section className="grid gap-3 md:grid-cols-3 xl:grid-cols-7">
      {metrics.map(([label, value]) => (
        <div key={String(label)} className="rounded-lg border border-line bg-white p-4 shadow-sm">
          <div className="text-xs font-medium uppercase text-slate-500">{label}</div>
          <div className="mt-2 min-h-8 text-2xl font-semibold text-ink">{value}</div>
        </div>
      ))}
      {health?.python_version_warning ? (
        <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800 md:col-span-3 xl:col-span-7">
          {health.python_version_warning}
        </div>
      ) : null}
    </section>
  );
}
