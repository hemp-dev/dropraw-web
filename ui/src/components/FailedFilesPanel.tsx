import { FileWarning, RotateCcw } from "lucide-react";

type Props = {
  failed: Array<{ rel_path: string; error: string }>;
  failedLogPath?: string;
  errorsPath?: string;
  onRetryFailed: () => void;
};

export function FailedFilesPanel({ failed, failedLogPath, errorsPath, onRetryFailed }: Props) {
  return (
    <section className="rounded-lg border border-line bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between gap-3">
        <h2 className="inline-flex items-center gap-2 text-base font-semibold text-ink"><FileWarning size={18} /> Failed Files</h2>
        <button className="focus-ring inline-flex items-center gap-2 rounded bg-red-600 px-3 py-2 text-sm font-medium text-white" onClick={onRetryFailed} type="button">
          <RotateCcw size={16} /> Retry failed only
        </button>
      </div>
      <p className="mt-2 text-sm text-slate-500">Failed count: {failed.length}</p>
      <div className="mt-3 grid gap-2 text-sm text-slate-600">
        <div>dropraw_failed.tsv: {failedLogPath || "Not generated yet"}</div>
        <div>errors.csv: {errorsPath || "Not generated yet"}</div>
      </div>
      <div className="mt-4 max-h-56 overflow-auto rounded border border-line">
        {failed.length === 0 ? (
          <p className="p-3 text-sm text-slate-500">No failed files.</p>
        ) : (
          failed.map((item) => (
            <div key={item.rel_path} className="border-b border-slate-100 p-3 text-sm">
              <div className="font-medium text-ink">{item.rel_path}</div>
              <div className="text-red-700">{item.error}</div>
            </div>
          ))
        )}
      </div>
    </section>
  );
}
