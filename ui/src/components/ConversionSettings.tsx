import { PresetSelector } from "./PresetSelector";

type Props = {
  preset: string;
  formats: string[];
  quality: number;
  maxSize: number;
  responsiveSizes: string;
  metadataMode: "strip" | "keep-color" | "keep-all";
  overwrite: boolean;
  resume: boolean;
  onChange: (patch: Partial<Props>) => void;
};

const formats = ["webp", "avif", "jpg", "png"];

export function ConversionSettings(props: Props) {
  return (
    <section className="rounded-lg border border-line bg-white p-5 shadow-sm">
      <h2 className="mb-4 text-base font-semibold text-ink">Conversion Settings</h2>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <PresetSelector preset={props.preset} onChange={(preset) => props.onChange({ preset })} />
        <label className="text-sm font-medium text-slate-700">
          Quality
          <input className="focus-ring mt-1 w-full rounded border border-line px-3 py-2" type="number" min={1} max={100} value={props.quality} onChange={(event) => props.onChange({ quality: Number(event.target.value) })} />
        </label>
        <label className="text-sm font-medium text-slate-700">
          Max long edge
          <input className="focus-ring mt-1 w-full rounded border border-line px-3 py-2" type="number" min={0} value={props.maxSize} onChange={(event) => props.onChange({ maxSize: Number(event.target.value) })} />
        </label>
        <label className="text-sm font-medium text-slate-700">
          Responsive sizes
          <input className="focus-ring mt-1 w-full rounded border border-line px-3 py-2" value={props.responsiveSizes} onChange={(event) => props.onChange({ responsiveSizes: event.target.value })} placeholder="1200,1920,2560" />
        </label>
      </div>
      <div className="mt-4 flex flex-wrap gap-3">
        {formats.map((format) => (
          <label key={format} className="inline-flex items-center gap-2 rounded border border-line px-3 py-2 text-sm">
            <input
              type="checkbox"
              checked={props.formats.includes(format)}
              onChange={(event) => {
                const next = event.target.checked ? [...props.formats, format] : props.formats.filter((item) => item !== format);
                props.onChange({ formats: next });
              }}
            />
            {format.toUpperCase()}
          </label>
        ))}
      </div>
      <div className="mt-4 grid gap-3 md:grid-cols-3">
        <label className="text-sm font-medium text-slate-700">
          Metadata mode
          <select className="focus-ring mt-1 w-full rounded border border-line bg-white px-3 py-2" value={props.metadataMode} onChange={(event) => props.onChange({ metadataMode: event.target.value as Props["metadataMode"] })}>
            <option value="strip">strip</option>
            <option value="keep-color">keep-color</option>
            <option value="keep-all">keep-all</option>
          </select>
        </label>
        <label className="inline-flex items-center gap-2 pt-6 text-sm font-medium text-slate-700">
          <input type="checkbox" checked={props.overwrite} onChange={(event) => props.onChange({ overwrite: event.target.checked })} />
          Overwrite existing files
        </label>
        <label className="inline-flex items-center gap-2 pt-6 text-sm font-medium text-slate-700">
          <input type="checkbox" checked={props.resume} onChange={(event) => props.onChange({ resume: event.target.checked })} />
          Resume mode
        </label>
      </div>
      <p className="mt-3 text-sm text-slate-500">Strip metadata is recommended for public websites. It removes GPS and private camera data.</p>
      <p className="mt-1 text-sm text-slate-500">Resume continues interrupted jobs and skips files that were already processed.</p>
    </section>
  );
}
