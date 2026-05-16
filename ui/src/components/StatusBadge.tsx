type Props = {
  status: string;
};

export function StatusBadge({ status }: Props) {
  const tone =
    status.includes("error") || status.includes("failed")
      ? "bg-red-50 text-red-700 border-red-200"
      : status.includes("running") || status.includes("queued")
        ? "bg-sky-50 text-sky-700 border-sky-200"
        : status.includes("soon")
          ? "bg-slate-100 text-slate-600 border-slate-200"
          : "bg-emerald-50 text-emerald-700 border-emerald-200";
  return <span className={`inline-flex items-center rounded border px-2 py-1 text-xs font-medium ${tone}`}>{status}</span>;
}
