import { Search, Wifi } from "lucide-react";
import type { ProviderId, ProviderInfo, ScanRequest } from "../types";
import { StatusBadge } from "./StatusBadge";

type Props = {
  providers: ProviderInfo[];
  value: ScanRequest;
  outputDir: string;
  onChange: (next: ScanRequest) => void;
  onOutputDirChange: (value: string) => void;
  onScan: () => void;
  onCreateJob: () => void;
  busy: boolean;
};

export function SourceForm({ providers, value, outputDir, onChange, onOutputDirChange, onScan, onCreateJob, busy }: Props) {
  return (
    <section className="rounded-lg border border-line bg-white p-5 shadow-sm">
      <div className="mb-4">
        <h2 className="text-base font-semibold text-ink">New Job</h2>
        <p className="text-sm text-slate-500">Choose where your RAW files are stored.</p>
      </div>
      <div className="grid gap-4 lg:grid-cols-3">
        <label className="text-sm font-medium text-slate-700">
          Source type
          <select
            className="focus-ring mt-1 w-full rounded border border-line bg-white px-3 py-2"
            value={value.provider}
            onChange={(event) => onChange({ ...value, provider: event.target.value as ProviderId })}
          >
            <option value="auto">Auto detect</option>
            {providers.map((provider) => (
              <option key={provider.id} value={provider.id}>
                {provider.label}
              </option>
            ))}
          </select>
        </label>
        <label className="text-sm font-medium text-slate-700 lg:col-span-2">
          Source URL or path
          <input
            className="focus-ring mt-1 w-full rounded border border-line px-3 py-2"
            value={value.source}
            onChange={(event) => onChange({ ...value, source: event.target.value })}
            placeholder="/photos/raw or https://www.dropbox.com/scl/fo/..."
          />
        </label>
        <label className="text-sm font-medium text-slate-700 lg:col-span-2">
          Output folder
          <input
            className="focus-ring mt-1 w-full rounded border border-line px-3 py-2"
            value={outputDir}
            onChange={(event) => onOutputDirChange(event.target.value)}
            placeholder="web_export"
          />
        </label>
        <div className="flex items-end gap-2">
          <button className="focus-ring inline-flex h-10 items-center gap-2 rounded bg-slate-800 px-4 text-sm font-medium text-white" type="button" onClick={onScan} disabled={busy}>
            <Search size={16} /> Scan source
          </button>
          <button className="focus-ring inline-flex h-10 items-center gap-2 rounded bg-emerald-600 px-4 text-sm font-medium text-white" type="button" onClick={onCreateJob} disabled={busy}>
            <Wifi size={16} /> Start
          </button>
        </div>
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        {providers.map((provider) => (
          <span key={provider.id} className="inline-flex items-center gap-2 text-xs text-slate-600">
            {provider.label} <StatusBadge status={provider.status} />
          </span>
        ))}
      </div>
      {(value.provider === "dropbox" || value.source.includes("dropbox.com")) && (
        <p className="mt-3 rounded border border-sky-200 bg-sky-50 p-3 text-sm text-sky-800">
          Dropbox folders are scanned through the API. RawBridge does not download the whole folder as ZIP.
        </p>
      )}
      <p className="mt-3 text-sm text-slate-500">Optimized images will be saved locally. Original RAW files are only downloaded temporarily.</p>
    </section>
  );
}
