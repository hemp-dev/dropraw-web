import type { ScanResponse } from "../types";
import { FileTable } from "./FileTable";
import type { ReactNode } from "react";

type Props = {
  scan?: ScanResponse;
};

export function ScanResults({ scan }: Props) {
  if (!scan) {
    return (
      <section className="rounded-lg border border-line bg-white p-5 text-sm text-slate-500 shadow-sm">
        Scan results will appear here after source validation.
      </section>
    );
  }
  return (
    <section className="rounded-lg border border-line bg-white p-5 shadow-sm">
      <h2 className="text-base font-semibold text-ink">Scan Results</h2>
      <div className="mt-4 grid gap-3 md:grid-cols-4">
        <Metric label="RAW files" value={scan.files_count} />
        <Metric label="Total size" value={`${Math.round(scan.total_size / 1024 / 1024)} MB`} />
        <Metric label="Folders" value={scan.folders_count} />
        <Metric label="Unsupported" value={scan.unsupported_files_count} />
      </div>
      {scan.warnings.map((warning) => (
        <p key={warning} className="mt-3 rounded border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">
          {warning}
        </p>
      ))}
      <FileTable files={scan.first_files.map((file) => ({ source_path: file.path, status: "pending", formats: "", input_size: file.size || 0, output_size: 0, error: "" }))} />
    </section>
  );
}

function Metric({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="rounded border border-line bg-slate-50 p-3">
      <div className="text-xs uppercase text-slate-500">{label}</div>
      <div className="mt-1 text-lg font-semibold text-ink">{value}</div>
    </div>
  );
}
