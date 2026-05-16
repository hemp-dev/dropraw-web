export function SettingsPanel() {
  return (
    <section className="rounded-lg border border-line bg-white p-5 shadow-sm">
      <h2 className="text-base font-semibold text-ink">Settings</h2>
      <div className="mt-4 grid gap-4 md:grid-cols-2">
        <label className="text-sm font-medium text-slate-700">
          Default output dir
          <input className="focus-ring mt-1 w-full rounded border border-line px-3 py-2" defaultValue="web_export" />
        </label>
        <label className="text-sm font-medium text-slate-700">
          Default preset
          <input className="focus-ring mt-1 w-full rounded border border-line px-3 py-2" defaultValue="web" />
        </label>
        <label className="text-sm font-medium text-slate-700">
          Temp dir
          <input className="focus-ring mt-1 w-full rounded border border-line px-3 py-2" placeholder=".rawbridge_tmp" />
        </label>
        <label className="text-sm font-medium text-slate-700">
          Max temp size
          <input className="focus-ring mt-1 w-full rounded border border-line px-3 py-2" placeholder="not enforced yet" />
        </label>
      </div>
    </section>
  );
}
