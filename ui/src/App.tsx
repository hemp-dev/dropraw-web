import { useEffect, useMemo, useState } from "react";
import { api } from "./api";
import { ConversionSettings } from "./components/ConversionSettings";
import { Dashboard } from "./components/Dashboard";
import { DoctorPanel } from "./components/DoctorPanel";
import { ErrorPanel } from "./components/ErrorPanel";
import { FailedFilesPanel } from "./components/FailedFilesPanel";
import { JobProgress } from "./components/JobProgress";
import { Layout } from "./components/Layout";
import { ReportPanel } from "./components/ReportPanel";
import { RetrySettings } from "./components/RetrySettings";
import { ScanResults } from "./components/ScanResults";
import { SettingsPanel } from "./components/SettingsPanel";
import { SourceForm } from "./components/SourceForm";
import type { Health, JobEvent, JobRequest, JobStatus, ProviderInfo, ScanRequest, ScanResponse } from "./types";

const initialScan: ScanRequest = {
  source: "",
  provider: "auto",
  list_retries: 8,
  download_retries: 8,
  retry_delay: 3,
  cooldown: 0.3,
};

export default function App() {
  const [health, setHealth] = useState<Health>();
  const [providers, setProviders] = useState<ProviderInfo[]>([]);
  const [jobs, setJobs] = useState<JobStatus[]>([]);
  const [activeJobId, setActiveJobId] = useState<string>();
  const [activeJob, setActiveJob] = useState<JobStatus>();
  const [events, setEvents] = useState<JobEvent[]>([]);
  const [failed, setFailed] = useState<Array<{ rel_path: string; error: string }>>([]);
  const [report, setReport] = useState<Record<string, unknown>>({});
  const [scanRequest, setScanRequest] = useState<ScanRequest>(initialScan);
  const [scan, setScan] = useState<ScanResponse>();
  const [outputDir, setOutputDir] = useState("web_export");
  const [preset, setPreset] = useState("web");
  const [formats, setFormats] = useState(["webp", "jpg"]);
  const [quality, setQuality] = useState(88);
  const [maxSize, setMaxSize] = useState(2560);
  const [responsiveSizes, setResponsiveSizes] = useState("");
  const [metadataMode, setMetadataMode] = useState<"strip" | "keep-color" | "keep-all">("strip");
  const [overwrite, setOverwrite] = useState(false);
  const [resume, setResume] = useState(true);
  const [onlyFailed, setOnlyFailed] = useState(false);
  const [failedLog, setFailedLog] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string>();

  useEffect(() => {
    void refreshStatic();
  }, []);

  useEffect(() => {
    if (!activeJobId) return;
    const timer = window.setInterval(() => {
      void refreshJob(activeJobId);
    }, 1500);
    void refreshJob(activeJobId);
    return () => window.clearInterval(timer);
  }, [activeJobId]);

  const jobPayload = useMemo<JobRequest>(() => ({
    ...scanRequest,
    output_dir: outputDir,
    preset,
    formats: formats.length ? formats : null,
    quality,
    max_size: maxSize || null,
    responsive_sizes: parseSizes(responsiveSizes),
    overwrite,
    resume,
    only_failed: onlyFailed && failedLog ? failedLog : null,
    metadata_mode: metadataMode,
  }), [scanRequest, outputDir, preset, formats, quality, maxSize, responsiveSizes, overwrite, resume, onlyFailed, failedLog, metadataMode]);

  async function refreshStatic() {
    try {
      const [nextHealth, nextProviders, nextJobs] = await Promise.all([api.health(), api.providers(), api.jobs()]);
      setHealth(nextHealth);
      setProviders(nextProviders);
      setJobs(nextJobs);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }

  async function refreshJob(jobId: string) {
    try {
      const [job, nextEvents, nextFailed, nextReport, nextJobs] = await Promise.all([
        api.job(jobId),
        api.events(jobId),
        api.failed(jobId),
        api.report(jobId),
        api.jobs(),
      ]);
      setActiveJob(job);
      setEvents(nextEvents);
      setFailed(nextFailed);
      setReport(nextReport);
      setJobs(nextJobs);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }

  async function scanSource() {
    setBusy(true);
    setError(undefined);
    try {
      setScan(await api.scan(scanRequest));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  async function createJob() {
    setBusy(true);
    setError(undefined);
    try {
      const created = await api.createJob(jobPayload);
      setActiveJobId(created.job_id);
      await refreshJob(created.job_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  async function action(kind: "cancel" | "resume" | "retry") {
    if (!activeJobId) return;
    if (kind === "cancel") await api.cancel(activeJobId);
    if (kind === "resume") await api.resume(activeJobId);
    if (kind === "retry") await api.retryFailed(activeJobId);
    await refreshJob(activeJobId);
  }

  const paths = (report.paths || {}) as Record<string, string>;

  return (
    <Layout>
      <div className="grid gap-5">
        <Dashboard health={health} jobs={jobs} failedCount={failed.length} />
        <ErrorPanel error={error} />
        <div className="grid gap-5 xl:grid-cols-[1.3fr_0.9fr]">
          <div className="grid gap-5">
            <SourceForm providers={providers} value={scanRequest} outputDir={outputDir} onChange={setScanRequest} onOutputDirChange={setOutputDir} onScan={scanSource} onCreateJob={createJob} busy={busy} />
            <ConversionSettings
              preset={preset}
              formats={formats}
              quality={quality}
              maxSize={maxSize}
              responsiveSizes={responsiveSizes}
              metadataMode={metadataMode}
              overwrite={overwrite}
              resume={resume}
              onChange={(patch) => {
                if (patch.preset !== undefined) setPreset(String(patch.preset));
                if (patch.formats !== undefined) setFormats(patch.formats as string[]);
                if (patch.quality !== undefined) setQuality(Number(patch.quality));
                if (patch.maxSize !== undefined) setMaxSize(Number(patch.maxSize));
                if (patch.responsiveSizes !== undefined) setResponsiveSizes(String(patch.responsiveSizes));
                if (patch.metadataMode !== undefined) setMetadataMode(patch.metadataMode as typeof metadataMode);
                if (patch.overwrite !== undefined) setOverwrite(Boolean(patch.overwrite));
                if (patch.resume !== undefined) setResume(Boolean(patch.resume));
              }}
            />
            <RetrySettings
              listRetries={scanRequest.list_retries}
              downloadRetries={scanRequest.download_retries}
              retryDelay={scanRequest.retry_delay}
              cooldown={scanRequest.cooldown}
              onlyFailed={onlyFailed}
              failedLog={failedLog}
              onChange={(patch) => {
                setScanRequest((current) => ({
                  ...current,
                  list_retries: patch.listRetries ?? current.list_retries,
                  download_retries: patch.downloadRetries ?? current.download_retries,
                  retry_delay: patch.retryDelay ?? current.retry_delay,
                  cooldown: patch.cooldown ?? current.cooldown,
                }));
                if (patch.onlyFailed !== undefined) setOnlyFailed(Boolean(patch.onlyFailed));
                if (patch.failedLog !== undefined) setFailedLog(String(patch.failedLog));
              }}
            />
          </div>
          <div className="grid gap-5">
            <DoctorPanel health={health} />
            <SettingsPanel />
          </div>
        </div>
        <ScanResults scan={scan} />
        <JobProgress job={activeJob} events={events} onCancel={() => void action("cancel")} onResume={() => void action("resume")} onRetryFailed={() => void action("retry")} />
        <FailedFilesPanel failed={failed} failedLogPath={paths.failed_tsv} errorsPath={paths.errors_csv} onRetryFailed={() => void action("retry")} />
        <ReportPanel report={report} />
      </div>
    </Layout>
  );
}

function parseSizes(value: string): number[] | null {
  const sizes = value
    .split(",")
    .map((item) => Number(item.trim()))
    .filter((item) => Number.isFinite(item) && item > 0);
  return sizes.length ? sizes : null;
}
