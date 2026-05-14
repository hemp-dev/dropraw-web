import { Activity, FileWarning, Gauge, HardDrive, Settings } from "lucide-react";
import type { ReactNode } from "react";

type Props = {
  children: ReactNode;
};

export function Layout({ children }: Props) {
  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-line bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4">
          <div>
            <h1 className="text-xl font-semibold tracking-normal text-ink">DropRaw Web</h1>
            <p className="text-sm text-slate-500">Local RAW conversion dashboard</p>
          </div>
          <nav className="hidden items-center gap-2 text-sm text-slate-600 md:flex">
            <span className="inline-flex items-center gap-1"><Gauge size={16} /> Jobs</span>
            <span className="inline-flex items-center gap-1"><Activity size={16} /> Progress</span>
            <span className="inline-flex items-center gap-1"><FileWarning size={16} /> Failed</span>
            <span className="inline-flex items-center gap-1"><HardDrive size={16} /> Reports</span>
            <span className="inline-flex items-center gap-1"><Settings size={16} /> Settings</span>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-7xl px-5 py-6">{children}</main>
    </div>
  );
}
