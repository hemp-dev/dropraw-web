type Props = {
  error?: string;
};

export function ErrorPanel({ error }: Props) {
  if (!error) return null;
  return <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800">{error}</div>;
}
