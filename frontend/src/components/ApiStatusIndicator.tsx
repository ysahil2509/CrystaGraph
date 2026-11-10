"use client";

import { useEffect, useState, useCallback } from "react";
import { Activity, CheckCircle2, AlertCircle, RefreshCw, ExternalLink } from "lucide-react";

export default function ApiStatusIndicator() {
  const [status, setStatus] = useState<"checking" | "online" | "offline">("checking");
  const [latency, setLatency] = useState<number | null>(null);
  const [showTooltip, setShowTooltip] = useState(false);
  const [isBrowserOnCloud, setIsBrowserOnCloud] = useState(false);

  const rawUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const apiUrl = rawUrl.trim().replace(/\/+$/, "");
  const isLocalTarget = apiUrl.includes("localhost") || apiUrl.includes("127.0.0.1");
  const apiBadgeLabel = isLocalTarget ? "API :8000" : "API Cloud";

  useEffect(() => {
    if (typeof window !== "undefined") {
      setIsBrowserOnCloud(
        window.location.hostname !== "localhost" &&
        window.location.hostname !== "127.0.0.1"
      );
    }
  }, []);

  const checkHealth = useCallback(async () => {
    const startTime = performance.now();
    try {
      const res = await fetch(`${apiUrl}/api/v1/health`, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
        // 12s timeout to accommodate Render free tier cold-start wakeups
        signal: AbortSignal.timeout(12000),
      });
      const endTime = performance.now();
      if (res.ok) {
        setStatus("online");
        setLatency(Math.round(endTime - startTime));
      } else {
        setStatus("offline");
        setLatency(null);
      }
    } catch {
      setStatus("offline");
      setLatency(null);
    }
  }, [apiUrl]);

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30s
    return () => clearInterval(interval);
  }, [checkHealth]);

  const isMisconfigured = isBrowserOnCloud && isLocalTarget;

  return (
    <div className="relative inline-block">
      <button
        onClick={() => setShowTooltip(!showTooltip)}
        className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium border transition-colors ${
          status === "online"
            ? "bg-emerald-50 text-emerald-800 border-emerald-200 hover:bg-emerald-100"
            : status === "offline"
            ? "bg-rose-50 text-rose-800 border-rose-200 hover:bg-rose-100"
            : "bg-slate-50 text-slate-600 border-slate-200"
        }`}
      >
        <span className="relative flex h-2 w-2">
          {status === "online" && (
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
          )}
          <span
            className={`relative inline-flex rounded-full h-2 w-2 ${
              status === "online"
                ? "bg-emerald-500"
                : status === "offline"
                ? "bg-rose-500"
                : "bg-amber-400 animate-pulse"
            }`}
          ></span>
        </span>

        <span>
          {status === "online"
            ? `${apiBadgeLabel}${latency !== null ? ` (${latency}ms)` : ""}`
            : status === "offline"
            ? isMisconfigured
              ? "API Config Error"
              : "API Offline"
            : "Checking..."}
        </span>
      </button>

      {/* Detail Popover */}
      {showTooltip && (
        <div className="absolute right-0 mt-2 w-72 bg-white rounded-lg shadow-xl border border-slate-200 p-3.5 z-30 text-xs text-slate-700 animate-fadeIn space-y-2">
          <div className="flex items-center justify-between font-semibold pb-1.5 border-b border-slate-100">
            <span className="flex items-center gap-1.5">
              <Activity className="h-3.5 w-3.5 text-slate-500" />
              Backend Connection
            </span>
            <button
              onClick={() => {
                setStatus("checking");
                checkHealth();
              }}
              title="Refresh connection"
              className="text-slate-400 hover:text-slate-600"
            >
              <RefreshCw className="h-3 w-3" />
            </button>
          </div>

          <div className="font-mono text-[10px] text-slate-500 bg-slate-50 p-1.5 rounded border border-slate-100 break-all">
            Target: <strong>{apiUrl}</strong>
          </div>

          {status === "online" ? (
            <div className="space-y-1">
              <p className="text-emerald-700 font-medium flex items-center gap-1">
                <CheckCircle2 className="h-3.5 w-3.5" />
                FastAPI microservice connected
              </p>
              <p className="text-[11px] text-slate-500">
                Swagger documentation is available at{" "}
                <a
                  href={`${apiUrl}/docs`}
                  target="_blank"
                  rel="noreferrer"
                  className="text-sky-600 underline font-mono inline-flex items-center gap-0.5"
                >
                  /docs <ExternalLink className="h-2.5 w-2.5" />
                </a>
                .
              </p>
            </div>
          ) : (
            <div className="space-y-1.5">
              <p className="text-rose-700 font-medium flex items-center gap-1">
                <AlertCircle className="h-3.5 w-3.5" />
                Backend not responding
              </p>

              {isMisconfigured ? (
                <div className="p-2 bg-amber-50 border border-amber-200 rounded text-[11px] text-amber-900 space-y-1">
                  <p className="font-semibold">⚠️ Vercel Redeploy Needed</p>
                  <p>
                    Vercel is still pointing to <code className="font-mono text-[10px]">localhost:8000</code>.
                  </p>
                  <p>
                    In Vercel &rarr; Settings &rarr; Environment Variables, set{" "}
                    <strong>NEXT_PUBLIC_API_URL</strong> to your Render HTTPS URL, then click <strong>Redeploy</strong>!
                  </p>
                </div>
              ) : isLocalTarget ? (
                <p className="text-[11px] text-slate-500">
                  Start local backend using:{" "}
                  <code className="bg-slate-100 px-1 py-0.5 rounded font-mono text-[10px]">
                    ./start_platform.sh
                  </code>
                </p>
              ) : (
                <div className="text-[11px] text-slate-500 space-y-1">
                  <p>
                    Render free instances spin down after 15m. Click below to wake it up:
                  </p>
                  <a
                    href={`${apiUrl}/api/v1/health`}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 text-sky-700 font-semibold hover:underline"
                  >
                    Open Render Healthcheck <ExternalLink className="h-3 w-3" />
                  </a>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
