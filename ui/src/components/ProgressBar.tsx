type Props = {
  value: number;
};

export function ProgressBar({ value }: Props) {
  const pct = Math.max(0, Math.min(100, Math.round(value * 100)));
  return (
    <div className="h-3 w-full overflow-hidden rounded bg-slate-200">
      <div className="h-full bg-emerald-500 transition-all" style={{ width: `${pct}%` }} />
    </div>
  );
}
