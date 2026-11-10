"use client";

import { useEffect, useState } from "react";
import {
  Download,
  Filter,
  Layers,
} from "lucide-react";
import { getSynthesisData } from "@/lib/api";

interface AshbyPoint {
  material: string;
  paper_id: string;
  doi: string;
  yield_strength_mpa?: number;
  density_gcm3?: number;
  tensile_strength_mpa?: number;
  hardness_hv?: number;
}

export default function SynthesizePage() {
  const [records, setRecords] = useState<Array<Record<string, unknown>>>([]);
  const [ashbyPoints, setAshbyPoints] = useState<AshbyPoint[]>([]);
  const [searchFilter, setSearchFilter] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    getSynthesisData()
      .then((data) => {
        setRecords(data.records);
        setAshbyPoints(data.ashby_points);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const filteredRecords = records.filter((r) => {
    const q = searchFilter.toLowerCase();
    const mat = String(r["Material / Alloy"] ?? "").toLowerCase();
    const prop = String(r["Property"] ?? "").toLowerCase();
    const paper = String(r["Paper ID"] ?? "").toLowerCase();
    return mat.includes(q) || prop.includes(q) || paper.includes(q);
  });

  const handleExportConsolidatedCSV = () => {
    if (!records.length) return;
    const keys = Object.keys(records[0]);
    const headers = keys.join(",");
    const rows = records
      .map((r) => keys.map((k) => `"${String(r[k] ?? "").replace(/"/g, '""')}"`).join(","))
      .join("\n");
    const blob = new Blob([`${headers}\n${rows}`], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `crystagraph_cross_paper_synthesis_10papers.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6 max-w-7xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-900">
            10-Paper Cross-Literature Synthesizer
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Consolidated cross-paper knowledge matrix across 10 benchmark publications, 50 unique
            materials systems, and 255 standardized SI properties.
          </p>
        </div>

        <button
          type="button"
          onClick={handleExportConsolidatedCSV}
          disabled={!records.length}
          className="inline-flex items-center gap-1.5 rounded-md bg-slate-900 px-3.5 py-1.5 text-xs font-medium text-white shadow-sm hover:bg-slate-800 disabled:opacity-50 transition-colors"
        >
          <Download className="h-3.5 w-3.5" />
          Export Unified Matrix (CSV)
        </button>
      </div>

      {/* Ashby Material Space Plot Card */}
      <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm space-y-3">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div>
            <h2 className="text-sm font-semibold text-slate-900 flex items-center gap-2">
              <Layers className="h-4 w-4 text-sky-600" />
              Ashby Material Property Map: Yield Strength vs. Density
            </h2>
            <p className="text-[11px] text-slate-500 mt-0.5">
              Specific strength comparison across titanium alloys, high entropy alloys, and ceramics.
            </p>
          </div>
          <span className="text-[11px] font-mono text-slate-400">
            {ashbyPoints.length} Material Systems Plotted
          </span>
        </div>

        {/* Visual Ashby Scatter Matrix */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 pt-2">
          {ashbyPoints.map((pt, idx) => {
            const ys = pt.yield_strength_mpa;
            const rho = pt.density_gcm3;
            const specStrength = ys && rho ? (ys / rho).toFixed(1) : "-";

            return (
              <div
                key={idx}
                className="rounded-md border border-slate-200 bg-slate-50/50 p-3 text-xs space-y-2 hover:border-slate-300 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <h3 className="font-bold text-slate-900 truncate max-w-[180px]">
                    {pt.material}
                  </h3>
                  <span className="font-mono text-[10px] text-sky-800 bg-sky-50 px-1.5 py-0.5 rounded border border-sky-100">
                    {pt.paper_id.replace("paper_", "P")}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-600">
                  <div>
                    <span className="text-slate-400 block text-[10px]">Yield Strength:</span>
                    <strong className="font-mono text-slate-800">
                      {ys ? `${ys} MPa` : "N/A"}
                    </strong>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px]">Density:</span>
                    <strong className="font-mono text-slate-800">
                      {rho ? `${rho} g/cm³` : "N/A"}
                    </strong>
                  </div>
                </div>

                <div className="pt-1.5 border-t border-slate-200/60 flex items-center justify-between text-[10px] text-slate-500">
                  <span>Specific Strength (σ/ρ):</span>
                  <span className="font-mono font-semibold text-emerald-700">
                    {specStrength} kN·m/kg
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Search Filter for Consolidated Matrix */}
      <div className="flex items-center gap-3">
        <div className="relative flex-1">
          <Filter className="absolute left-3 top-2.5 h-3.5 w-3.5 text-slate-400" />
          <input
            type="text"
            placeholder="Search unified matrix by material formula, property, or paper ID..."
            value={searchFilter}
            onChange={(e) => setSearchFilter(e.target.value)}
            className="w-full rounded-md border border-slate-300 pl-8 pr-3 py-1.5 text-xs text-slate-900 focus:outline-none focus:ring-1 focus:ring-sky-600 bg-white"
          />
        </div>
        <span className="text-xs text-slate-500 whitespace-nowrap">
          Showing <strong>{filteredRecords.length}</strong> of {records.length} records
        </span>
      </div>

      {/* Unified Synthesis Matrix Table */}
      <div className="rounded-lg border border-slate-200 bg-white shadow-sm overflow-hidden">
        <div className="overflow-x-auto max-h-[600px] overflow-y-auto">
          <table className="w-full text-left text-xs text-slate-700 divide-y divide-slate-100">
            <thead className="sticky top-0 border-b border-slate-200 bg-slate-50 font-medium text-slate-600 uppercase text-[10px]">
              <tr>
                <th className="px-4 py-2.5 whitespace-nowrap">Material / Alloy</th>
                <th className="px-4 py-2.5 whitespace-nowrap">Property</th>
                <th className="px-4 py-2.5 whitespace-nowrap">Standardized SI Measurement</th>
                <th className="px-4 py-2.5 whitespace-nowrap">Reported Value</th>
                <th className="px-4 py-2.5 whitespace-nowrap">Composition Summary</th>
                <th className="px-4 py-2.5 whitespace-nowrap">Paper DOI & Provenance</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 bg-white">
              {loading ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-xs text-slate-400">
                    Loading cross-literature synthesis matrix...
                  </td>
                </tr>
              ) : (
                filteredRecords.map((r, idx) => (
                  <tr key={idx} className="hover:bg-slate-50/70 transition-colors">
                    <td className="px-4 py-2.5 font-bold text-slate-900 whitespace-nowrap">
                      {String(r["Material / Alloy"] ?? "")}
                    </td>
                    <td className="px-4 py-2.5 text-slate-700 whitespace-nowrap">
                      {String(r["Property"] ?? "")}
                    </td>
                    <td className="px-4 py-2.5 font-mono font-bold text-emerald-800 whitespace-nowrap">
                      {String(r["Standardized SI Measurement"] ?? "")}
                    </td>
                    <td className="px-4 py-2.5 font-mono text-slate-500 whitespace-nowrap text-[11px]">
                      {String(r["Reported Value"] ?? "")} {String(r["Reported Unit"] ?? "")}
                    </td>
                    <td className="px-4 py-2.5 font-mono text-slate-500 text-[11px] max-w-xs truncate">
                      {String(r["Composition Summary"] ?? "-")}
                    </td>
                    <td className="px-4 py-2.5 font-mono text-sky-700 text-[11px] whitespace-nowrap">
                      {String(r["DOI"] ?? "")}
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
