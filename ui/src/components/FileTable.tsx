type Row = {
  source_path: string;
  status: string;
  formats: string;
  input_size: number;
  output_size: number;
  error: string;
};

type Props = {
  files: Row[];
};

export function FileTable({ files }: Props) {
  return (
    <div className="mt-4 overflow-auto rounded border border-line">
      <table className="min-w-full divide-y divide-line text-sm">
        <thead className="bg-slate-100 text-left text-xs uppercase text-slate-500">
          <tr>
            <th className="px-3 py-2">Source path</th>
            <th className="px-3 py-2">Status</th>
            <th className="px-3 py-2">Formats</th>
            <th className="px-3 py-2">Input size</th>
            <th className="px-3 py-2">Output size</th>
            <th className="px-3 py-2">Error</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100 bg-white">
          {files.slice(0, 100).map((file) => (
            <tr key={`${file.source_path}-${file.status}`}>
              <td className="max-w-md truncate px-3 py-2">{file.source_path}</td>
              <td className="px-3 py-2">{file.status}</td>
              <td className="px-3 py-2">{file.formats}</td>
              <td className="px-3 py-2">{file.input_size}</td>
              <td className="px-3 py-2">{file.output_size}</td>
              <td className="max-w-md truncate px-3 py-2 text-red-700">{file.error}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
