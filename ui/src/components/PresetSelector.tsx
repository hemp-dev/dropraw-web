type Props = {
  preset: string;
  onChange: (value: string) => void;
};

const presets = ["web", "preview", "retina", "lossless_web", "tilda", "wordpress", "custom"];

export function PresetSelector({ preset, onChange }: Props) {
  return (
    <label className="text-sm font-medium text-slate-700">
      Preset
      <select className="focus-ring mt-1 w-full rounded border border-line bg-white px-3 py-2" value={preset} onChange={(event) => onChange(event.target.value)}>
        {presets.map((item) => (
          <option key={item} value={item}>
            {item}
          </option>
        ))}
      </select>
    </label>
  );
}
