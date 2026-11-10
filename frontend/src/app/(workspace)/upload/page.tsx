"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import {
  UploadCloud,
  FileCode,
  FileText,
  CheckCircle2,
  AlertCircle,
  Loader2,
  ArrowRight,
  RefreshCw,
  Sparkles,
} from "lucide-react";
import {
  uploadPaper,
  getJobStatus,
  listJobs,
  JobStatusResponse,
} from "@/lib/api";

const PIPELINE_STEPS = [
  { label: "Document Parsing", desc: "Validate XML/PDF structure" },
  { label: "Table Normalization", desc: "Span expansion & header indexing" },
  { label: "Stoichiometry Mining", desc: "Chemical formula & percentage parsing" },
  { label: "Property Extraction", desc: "Numerical values & SI conversion" },
  { label: "Knowledge Linking", desc: "Relational n-tuple persistence" },
];

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Pipeline configuration toggles
  const [options, setOptions] = useState({
    extract_tables: true,
    extract_compositions: true,
    extract_properties: true,
    extract_text: true,
    normalize_si: true,
  });

  // Active Job State
  const [activeJob, setActiveJob] = useState<JobStatusResponse | null>(null);
  const [jobHistory, setJobHistory] = useState<JobStatusResponse[]>([]);
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const fetchJobs = () => {
    listJobs()
      .then((jobs) => setJobHistory(jobs))
      .catch(() => {});
  };

  useEffect(() => {
    fetchJobs();
    return () => {
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current);
    };
  }, []);

  // Polling active job
  useEffect(() => {
    if (!activeJob) return;

    if (activeJob.status === "completed" || activeJob.status === "failed") {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
      fetchJobs();
      return;
    }

    if (!pollIntervalRef.current) {
      pollIntervalRef.current = setInterval(() => {
        getJobStatus(activeJob.job_id)
          .then((updated) => {
            setActiveJob(updated);
            if (updated.status === "completed" || updated.status === "failed") {
              if (pollIntervalRef.current) {
                clearInterval(pollIntervalRef.current);
                pollIntervalRef.current = null;
              }
              fetchJobs();
            }
          })
          .catch(() => {});
      }, 1500);
    }
  }, [activeJob]);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      selectFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      selectFile(e.target.files[0]);
    }
  };

  const selectFile = (selectedFile: File) => {
    setErrorMessage(null);
    const ext = selectedFile.name.split(".").pop()?.toLowerCase();
    if (ext !== "xml" && ext !== "pdf") {
      setErrorMessage("Please upload an XML or PDF research paper.");
      return;
    }
    setFile(selectedFile);
  };

  const handleStartUpload = async () => {
    if (!file) return;
    setUploading(true);
    setErrorMessage(null);

    try {
      const initialJob = await uploadPaper(file, options);
      setActiveJob(initialJob);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMessage(err.message);
      } else {
        setErrorMessage("Upload failed. Ensure FastAPI server is running on port 8000.");
      }
    } finally {
      setUploading(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  const getStepProgressIndex = (pct: number) => {
    if (pct < 20) return 0;
    if (pct < 45) return 1;
    if (pct < 65) return 2;
    if (pct < 85) return 3;
    return 4;
  };

  return (
    <div className="space-y-8 max-w-6xl">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold tracking-tight text-slate-900">
          Paper Ingestion & Knowledge Extraction Pipeline
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Upload scientific publications in XML (Elsevier/JATS) or PDF format to extract scientific
          tables, stoichiometry, and physical material properties.
        </p>
      </div>

      {/* Main Grid: Upload Form + Configuration */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Upload Drop Zone & Selected File */}
        <div className="lg:col-span-2 space-y-4">
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              isDragging
                ? "border-sky-500 bg-sky-50/50"
                : file
                ? "border-emerald-300 bg-emerald-50/20"
                : "border-slate-300 hover:border-slate-400 bg-white"
            }`}
          >
            <input
              type="file"
              id="paper-file-input"
              accept=".xml,.pdf"
              onChange={handleFileChange}
              className="hidden"
            />
            <label
              htmlFor="paper-file-input"
              className="cursor-pointer flex flex-col items-center justify-center space-y-3"
            >
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-slate-100 text-slate-600">
                <UploadCloud className="h-6 w-6 text-slate-500" />
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-900">
                  Click to select paper or drag & drop file here
                </p>
                <p className="text-xs text-slate-500 mt-1">
                  Supported academic formats: <strong className="text-slate-700">.xml</strong>{" "}
                  (Elsevier / JATS / TEI) and <strong className="text-slate-700">.pdf</strong>{" "}
                  (Native PDFplumber extraction)
                </p>
              </div>
            </label>
          </div>

          {/* Selected File Details */}
          {file && (
            <div className="rounded-lg border border-slate-200 bg-white p-4 flex items-center justify-between shadow-sm">
              <div className="flex items-center gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded bg-sky-50 text-sky-700">
                  {file.name.endsWith(".xml") ? (
                    <FileCode className="h-5 w-5" />
                  ) : (
                    <FileText className="h-5 w-5" />
                  )}
                </div>
                <div>
                  <p className="text-xs font-semibold text-slate-900 truncate max-w-md">
                    {file.name}
                  </p>
                  <p className="text-[11px] text-slate-500">
                    Size: {formatFileSize(file.size)} &bull; Format:{" "}
                    <span className="font-mono uppercase font-semibold text-slate-700">
                      {file.name.split(".").pop()}
                    </span>
                  </p>
                </div>
              </div>

              <button
                type="button"
                onClick={() => setFile(null)}
                className="text-xs text-slate-400 hover:text-slate-600 p-1"
              >
                Remove
              </button>
            </div>
          )}

          {errorMessage && (
            <div className="rounded-md bg-rose-50 border border-rose-200 p-3.5 flex items-start gap-2.5 text-xs text-rose-800">
              <AlertCircle className="h-4 w-4 text-rose-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold">Pipeline Error</p>
                <p className="mt-0.5 text-rose-700">{errorMessage}</p>
              </div>
            </div>
          )}

          {/* Action Trigger */}
          <div className="flex justify-end">
            <button
              type="button"
              disabled={!file || uploading || activeJob?.status === "processing"}
              onClick={handleStartUpload}
              className="inline-flex items-center gap-2 rounded-md bg-slate-900 px-5 py-2.5 text-xs font-medium text-white shadow-sm hover:bg-slate-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {uploading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin text-sky-400" />
                  Uploading Publication...
                </>
              ) : activeJob?.status === "processing" ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin text-sky-400" />
                  Pipeline Running...
                </>
              ) : (
                <>
                  Start Extraction Pipeline
                  <ArrowRight className="h-4 w-4" />
                </>
              )}
            </button>
          </div>
        </div>

        {/* Pipeline Configuration Options */}
        <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm space-y-4">
          <div>
            <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-500">
              Pipeline Stages & Options
            </h2>
            <p className="text-[11px] text-slate-400 mt-1">
              Select extraction components to activate during background execution.
            </p>
          </div>

          <div className="space-y-3 pt-2">
            <label className="flex items-start gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={options.extract_tables}
                onChange={(e) =>
                  setOptions({ ...options, extract_tables: e.target.checked })
                }
                className="mt-0.5 rounded border-slate-300 text-sky-600 focus:ring-sky-500"
              />
              <div>
                <p className="text-xs font-medium text-slate-800">
                  Scientific Table Extraction
                </p>
                <p className="text-[11px] text-slate-500">
                  Parses multi-row tables, resolves colspans, and cleans cell strings.
                </p>
              </div>
            </label>

            <label className="flex items-start gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={options.extract_compositions}
                onChange={(e) =>
                  setOptions({ ...options, extract_compositions: e.target.checked })
                }
                className="mt-0.5 rounded border-slate-300 text-sky-600 focus:ring-sky-500"
              />
              <div>
                <p className="text-xs font-medium text-slate-800">
                  Chemical Composition Mining
                </p>
                <p className="text-[11px] text-slate-500">
                  Extracts wt.%, at.%, mol% stoichiometric fractions from material columns.
                </p>
              </div>
            </label>

            <label className="flex items-start gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={options.extract_properties}
                onChange={(e) =>
                  setOptions({ ...options, extract_properties: e.target.checked })
                }
                className="mt-0.5 rounded border-slate-300 text-sky-600 focus:ring-sky-500"
              />
              <div>
                <p className="text-xs font-medium text-slate-800">
                  Material Property Extraction
                </p>
                <p className="text-[11px] text-slate-500">
                  Extracts yield strength, density, dielectric constants, and hardness.
                </p>
              </div>
            </label>

            <label className="flex items-start gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={options.extract_text}
                onChange={(e) =>
                  setOptions({ ...options, extract_text: e.target.checked })
                }
                className="mt-0.5 rounded border-slate-300 text-sky-600 focus:ring-sky-500"
              />
              <div>
                <p className="text-xs font-medium text-slate-800">
                  Narrative Text Mining
                </p>
                <p className="text-[11px] text-slate-500">
                  Mines numerical properties stated in abstract and body paragraphs.
                </p>
              </div>
            </label>

            <label className="flex items-start gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={options.normalize_si}
                onChange={(e) =>
                  setOptions({ ...options, normalize_si: e.target.checked })
                }
                className="mt-0.5 rounded border-slate-300 text-sky-600 focus:ring-sky-500"
              />
              <div>
                <p className="text-xs font-medium text-slate-800">
                  SI Unit Standardization
                </p>
                <p className="text-[11px] text-slate-500">
                  Normalizes units (e.g. ksi to MPa, g/cm³ to kg/m³, °C to K).
                </p>
              </div>
            </label>
          </div>
        </div>
      </div>

      {/* Active Pipeline Progress Monitor */}
      {activeJob && (
        <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-slate-100 pb-4">
            <div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs font-semibold text-sky-800 bg-sky-50 px-2 py-0.5 rounded border border-sky-100">
                  {activeJob.job_id}
                </span>
                <span className="text-xs text-slate-500">&bull;</span>
                <span className="text-xs font-medium text-slate-700">
                  {activeJob.filename}
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-1">
                Current Step:{" "}
                <strong className="text-slate-800">{activeJob.current_step}</strong>
              </p>
            </div>

            <div className="flex items-center gap-3">
              <span
                className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium ${
                  activeJob.status === "completed"
                    ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                    : activeJob.status === "failed"
                    ? "bg-rose-50 text-rose-700 border border-rose-200"
                    : "bg-sky-50 text-sky-700 border border-sky-200 animate-pulse"
                }`}
              >
                {activeJob.status === "processing" || activeJob.status === "pending" ? (
                  <Loader2 className="h-3 w-3 animate-spin" />
                ) : activeJob.status === "completed" ? (
                  <CheckCircle2 className="h-3 w-3 text-emerald-600" />
                ) : (
                  <AlertCircle className="h-3 w-3 text-rose-600" />
                )}
                {activeJob.status.toUpperCase()}
              </span>
              <span className="font-mono text-xs font-bold text-slate-700 tabular-nums">
                {activeJob.progress_pct}%
              </span>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
            <div
              className={`h-full transition-all duration-500 ${
                activeJob.status === "completed"
                  ? "bg-emerald-600"
                  : activeJob.status === "failed"
                  ? "bg-rose-600"
                  : "bg-sky-600"
              }`}
              style={{ width: `${activeJob.progress_pct}%` }}
            />
          </div>

          {/* Sequential Stage Stepper */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
            {PIPELINE_STEPS.map((step, idx) => {
              const currentStepIdx = getStepProgressIndex(activeJob.progress_pct);
              const isPast =
                activeJob.status === "completed" || currentStepIdx > idx;
              const isCurrent =
                activeJob.status === "processing" && currentStepIdx === idx;

              return (
                <div
                  key={idx}
                  className={`rounded-md p-3 border transition-colors ${
                    isPast
                      ? "border-emerald-200 bg-emerald-50/40 text-emerald-900"
                      : isCurrent
                      ? "border-sky-300 bg-sky-50/50 text-sky-900"
                      : "border-slate-200 bg-slate-50/30 text-slate-400"
                  }`}
                >
                  <div className="flex items-center gap-1.5 text-xs font-semibold">
                    {isPast ? (
                      <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" />
                    ) : isCurrent ? (
                      <Loader2 className="h-3.5 w-3.5 animate-spin text-sky-600" />
                    ) : (
                      <span className="h-3.5 w-3.5 rounded-full border border-slate-300 inline-block text-[9px] leading-3 text-center text-slate-400">
                        {idx + 1}
                      </span>
                    )}
                    <span>{step.label}</span>
                  </div>
                  <p className="text-[10px] text-slate-500 mt-1 leading-snug">
                    {step.desc}
                  </p>
                </div>
              );
            })}
          </div>

          {/* Results Summary Callout (Upon Completion) */}
          {activeJob.status === "completed" && (
            <div className="rounded-md bg-emerald-50/50 border border-emerald-200 p-4 space-y-3">
              <div className="flex items-center gap-2 text-xs font-semibold text-emerald-900">
                <Sparkles className="h-4 w-4 text-emerald-600" />
                Knowledge Extraction Complete & Stored in SQLite
              </div>
              <div className="grid grid-cols-3 gap-4 text-center">
                <div className="bg-white rounded border border-emerald-100 p-2.5">
                  <span className="text-[10px] uppercase font-semibold text-slate-400 block">
                    Tables Extracted
                  </span>
                  <span className="text-lg font-bold text-slate-900 font-mono">
                    {activeJob.extracted_tables_count}
                  </span>
                </div>
                <div className="bg-white rounded border border-emerald-100 p-2.5">
                  <span className="text-[10px] uppercase font-semibold text-slate-400 block">
                    Compositions
                  </span>
                  <span className="text-lg font-bold text-slate-900 font-mono">
                    {activeJob.extracted_compositions_count}
                  </span>
                </div>
                <div className="bg-white rounded border border-emerald-100 p-2.5">
                  <span className="text-[10px] uppercase font-semibold text-slate-400 block">
                    Property Values
                  </span>
                  <span className="text-lg font-bold text-slate-900 font-mono">
                    {activeJob.extracted_properties_count}
                  </span>
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => {
                    setActiveJob(null);
                    setFile(null);
                  }}
                  className="text-xs font-medium text-slate-600 hover:text-slate-800"
                >
                  Upload Another Document
                </button>
                <Link
                  href="/tables"
                  className="inline-flex items-center gap-1.5 rounded bg-emerald-700 px-3.5 py-1.5 text-xs font-medium text-white shadow-sm hover:bg-emerald-800 transition-colors"
                >
                  Open Extracted Tables
                  <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Extraction Job History Table */}
      <div className="rounded-lg border border-slate-200 bg-white shadow-sm">
        <div className="flex items-center justify-between border-b border-slate-200 px-6 py-4">
          <div>
            <h2 className="text-sm font-semibold text-slate-900">
              Recent Extraction Jobs
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              History of background paper parsing tasks and extraction counts.
            </p>
          </div>
          <button
            onClick={fetchJobs}
            type="button"
            className="inline-flex items-center gap-1 text-xs text-slate-500 hover:text-slate-800"
          >
            <RefreshCw className="h-3 w-3" />
            Refresh
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="border-b border-slate-100 bg-slate-50/60 font-medium text-slate-500 uppercase">
              <tr>
                <th scope="col" className="px-6 py-3">
                  Job ID & File
                </th>
                <th scope="col" className="px-6 py-3">
                  Format
                </th>
                <th scope="col" className="px-6 py-3 text-center">
                  Tables
                </th>
                <th scope="col" className="px-6 py-3 text-center">
                  Compositions
                </th>
                <th scope="col" className="px-6 py-3 text-center">
                  Properties
                </th>
                <th scope="col" className="px-6 py-3">
                  Status & Progress
                </th>
                <th scope="col" className="px-6 py-3 text-right">
                  Timestamp
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {jobHistory.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center text-slate-400 text-xs">
                    No extraction jobs recorded yet. Upload a research publication above to begin.
                  </td>
                </tr>
              ) : (
                jobHistory.map((j) => (
                  <tr key={j.job_id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="px-6 py-3.5">
                      <span className="font-mono font-semibold text-slate-900 block">
                        {j.job_id}
                      </span>
                      <span className="text-slate-500 truncate block max-w-xs mt-0.5">
                        {j.filename}
                      </span>
                    </td>
                    <td className="px-6 py-3.5">
                      <span className="inline-flex items-center uppercase font-mono px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-100 text-slate-700 border border-slate-200">
                        {j.file_type}
                      </span>
                    </td>
                    <td className="px-6 py-3.5 text-center font-mono tabular-nums text-slate-700">
                      {j.extracted_tables_count}
                    </td>
                    <td className="px-6 py-3.5 text-center font-mono tabular-nums text-slate-700">
                      {j.extracted_compositions_count}
                    </td>
                    <td className="px-6 py-3.5 text-center font-mono tabular-nums text-slate-700">
                      {j.extracted_properties_count}
                    </td>
                    <td className="px-6 py-3.5">
                      <div className="flex items-center gap-2">
                        <span
                          className={`inline-flex items-center rounded-full px-2 py-0.5 text-[10px] font-medium ${
                            j.status === "completed"
                              ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                              : j.status === "failed"
                              ? "bg-rose-50 text-rose-700 border border-rose-200"
                              : "bg-sky-50 text-sky-700 border border-sky-200"
                          }`}
                        >
                          {j.status}
                        </span>
                        <span className="font-mono text-[11px] text-slate-500">
                          {j.progress_pct}%
                        </span>
                      </div>
                      <p className="text-[10px] text-slate-400 truncate max-w-xs mt-0.5">
                        {j.current_step}
                      </p>
                    </td>
                    <td className="px-6 py-3.5 text-right font-mono text-[11px] text-slate-400 whitespace-nowrap">
                      {j.created_at ? new Date(j.created_at).toLocaleString() : "-"}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
