type Props = {
  listRetries: number;
  downloadRetries: number;
  retryDelay: number;
  cooldown: number;
  onlyFailed: boolean;
  failedLog: string;
  onChange: (patch: Partial<Props>) => void;
};

export function RetrySettings(props: Props) {
  return (
    <section className="rounded-lg border border-line bg-white p-5 shadow-sm">
      <h2 className="mb-4 text-base font-semibold text-ink">Retry Settings</h2>
      <div className="grid gap-4 md:grid-cols-4">
        <NumberField label="List retries" value={props.listRetries} onChange={(listRetries) => props.onChange({ listRetries })} />
        <NumberField label="Download retries" value={props.downloadRetries} onChange={(downloadRetries) => props.onChange({ downloadRetries })} />
        <NumberField label="Retry delay" value={props.retryDelay} onChange={(retryDelay) => props.onChange({ retryDelay })} step="0.5" />
        <NumberField label="Cooldown" value={props.cooldown} onChange={(cooldown) => props.onChange({ cooldown })} step="0.1" />
      </div>
      <div className="mt-4 grid gap-3 md:grid-cols-2">
        <label className="inline-flex items-center gap-2 text-sm font-medium text-slate-700">
          <input type="checkbox" checked={props.onlyFailed} onChange={(event) => props.onChange({ onlyFailed: event.target.checked })} />
          Retry only failed
        </label>
        <input className="focus-ring rounded border border-line px-3 py-2 text-sm" value={props.failedLog} onChange={(event) => props.onChange({ failedLog: event.target.value })} placeholder="/output/rawbridge_failed.tsv" />
      </div>
      <p className="mt-3 text-sm text-slate-500">Large cloud folders may occasionally fail during listing or download. Retries and cooldown help complete long jobs safely.</p>
      <p className="mt-1 text-sm text-slate-500">Retry failed only processes files from rawbridge_failed.tsv and keeps existing outputs unchanged.</p>
    </section>
  );
}

function NumberField({ label, value, onChange, step = "1" }: { label: string; value: number; onChange: (value: number) => void; step?: string }) {
  return (
    <label className="text-sm font-medium text-slate-700">
      {label}
      <input className="focus-ring mt-1 w-full rounded border border-line px-3 py-2" type="number" min={0} step={step} value={value} onChange={(event) => onChange(Number(event.target.value))} />
    </label>
  );
}
