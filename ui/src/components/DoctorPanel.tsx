import type { Health } from "../types";
import { StatusBadge } from "./StatusBadge";

type Props = {
  health?: Health;
};

export function DoctorPanel({ health }: Props) {
  return (
    <section className="rounded-lg border border-line bg-white p-5 shadow-sm">
      <h2 className="text-base font-semibold text-ink">Doctor</h2>
      {!health ? (
        <p className="mt-3 text-sm text-slate-500">Loading health checks.</p>
      ) : (
        <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          <Check label="Python" value={health.python_version} ok={!health.python_version_warning} />
          <Check label="WebP" value={String(health.pillow_webp_support)} ok={health.pillow_webp_support} />
          <Check label="AVIF" value={String(health.pillow_avif_support)} ok={health.pillow_avif_support} />
          <Check label="Dropbox SDK" value={health.dropbox_sdk_version || "missing"} ok={Boolean(health.dropbox_sdk_version)} />
          {Object.entries(health.credentials).map(([key, value]) => <Check key={key} label={`${key} credentials`} value={String(value)} ok={value} />)}
        </div>
      )}
      <p className="mt-3 text-sm text-slate-500">Python 3.11 or 3.12 is recommended. Python 3.14 may cause SSL or dependency compatibility issues.</p>
    </section>
  );
}

function Check({ label, value, ok }: { label: string; value: string; ok: boolean }) {
  return (
    <div className="rounded border border-line bg-slate-50 p-3">
      <div className="text-xs uppercase text-slate-500">{label}</div>
      <div className="mt-2 flex items-center justify-between gap-3">
        <span className="text-sm font-medium text-ink">{value}</span>
        <StatusBadge status={ok ? "ok" : "warning"} />
      </div>
    </div>
  );
}
