import { Download, FolderOpen } from "lucide-react";

type Props = {
  report: Record<string, unknown>;
};

export function ReportPanel({ report }: Props) {
  const paths = (report.paths || {}) as Record<string, string>;
  return (
    <section className="rounded-lg border border-line bg-white p-5 shadow-sm">
      <h2 className="text-base font-semibold text-ink">Reports</h2>
      <div className="mt-4 grid gap-3 md:grid-cols-4">
        <Metric label="Processed" value={String(report.processed ?? 0)} />
        <Metric label="Generated" value={String(report.output_files_count ?? 0)} />
        <Metric label="Errors" value={String(report.failed ?? 0)} />
        <Metric label="Saved bytes" value={String(report.estimated_saved_bytes ?? 0)} />
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        {Object.entries(paths).map(([key, value]) => (
          <span key={key} className="inline-flex items-center gap-2 rounded border border-line px-3 py-2 text-sm text-slate-600">
            {key === "output_dir" ? <FolderOpen size={16} /> : <Download size={16} />}
            {value}
          </span>
        ))}
      </div>
    </section>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded border border-line bg-slate-50 p-3">
      <div className="text-xs uppercase text-slate-500">{label}</div>
      <div className="mt-1 text-lg font-semibold text-ink">{value}</div>
    </div>
  );
}
