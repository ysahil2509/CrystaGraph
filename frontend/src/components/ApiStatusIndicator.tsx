"use client";

import { useEffect, useState } from "react";
import { Activity, CheckCircle2, AlertCircle, RefreshCw } from "lucide-react";

export default function ApiStatusIndicator() {
  const [status, setStatus] = useState<"checking" | "online" | "offline">("checking");
  const [latency, setLatency] = useState<number | null>(null);
  const [showTooltip, setShowTooltip] = useState(false);

  const checkHealth = async () => {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    const startTime = performance.now();
    try {
      const res = await fetch(`${apiUrl}/api/v1/health`, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
        // short timeout
        signal: AbortSignal.timeout(3000),
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
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30s
    return () => clearInterval(interval);
  }, []);

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
            ? `API :8000${latency !== null ? ` (${latency}ms)` : ""}`
            : status === "offline"
            ? "API Offline"
            : "Checking..."}
        </span>
      </button>

      {/* Detail Popover */}
      {showTooltip && (
        <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-xl border border-slate-200 p-3 z-30 text-xs text-slate-700 animate-fadeIn">
          <div className="flex items-center justify-between font-semibold pb-1.5 mb-1.5 border-b border-slate-100">
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

          {status === "online" ? (
            <div className="space-y-1">
              <p className="text-emerald-700 font-medium flex items-center gap-1">
                <CheckCircle2 className="h-3.5 w-3.5" />
                FastAPI microservice connected
              </p>
              <p className="text-[11px] text-slate-500">
                Port 8000 &bull; SQLite database online. Swagger available at{" "}
                <a
                  href="http://localhost:8000/docs"
                  target="_blank"
                  rel="noreferrer"
                  className="text-sky-600 underline font-mono"
                >
                  /docs
                </a>
                .
              </p>
            </div>
          ) : (
            <div className="space-y-1">
              <p className="text-rose-700 font-medium flex items-center gap-1">
                <AlertCircle className="h-3.5 w-3.5" />
                Backend not responding
              </p>
              <p className="text-[11px] text-slate-500">
                Start the backend using:
              </p>
              <pre className="bg-slate-100 p-1.5 rounded font-mono text-[10px] text-slate-800">
                ./start_platform.sh
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

