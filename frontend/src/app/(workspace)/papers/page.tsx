"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  FileText,
  Search,
  ExternalLink,
  Table2,
  ArrowRight,
} from "lucide-react";
import { listPapers } from "@/lib/api";

interface PaperRecord {
  paper_id: string;
  doi: string;
  pii: string;
  title: string;
  status: string;
  tables_count?: number;
}

const BENCHMARK_PAPERS: PaperRecord[] = [
  {
    paper_id: "paper_01_ti_alloys",
    title: "Microstructural evolution and mechanical properties of advanced alpha-beta titanium alloys for aerospace applications",
    doi: "10.1016/j.msea.2023.144890",
    pii: "S0921-5093(23)00482-1",
    status: "success",
    tables_count: 2,
  },
  {
    paper_id: "paper_02_battery_cathodes",
    title: "High-capacity single-crystal LiNi0.8Mn0.1Co0.1O2 cathode materials for lithium-ion batteries: Synthesis, electrochemical performance and thermal stability",
    doi: "10.1016/j.ensm.2023.102844",
    pii: "S2405-8297(23)00312-5",
    status: "success",
    tables_count: 2,
  },
  {
    paper_id: "paper_03_perovskite_dielectrics",
    title: "Dielectric and piezoelectric characteristics of lead-free barium titanate-based ceramics synthesized via solid-state reaction",
    doi: "10.1016/j.jeurceramsoc.2023.05.012",
    pii: "S0955-2219(23)00245-8",
    status: "success",
    tables_count: 2,
  },
  {
    paper_id: "paper_04_high_entropy_alloys",
    title: "Phase stability and tensile deformation mechanisms in CoCrFeNi high-entropy alloy systems",
    doi: "10.1016/j.actamat.2023.118942",
    pii: "S1359-6454(23)00189-3",
    status: "success",
    tables_count: 2,
  },
  {
    paper_id: "paper_05_bioactive_glasses",
    title: "Thermal properties and crystallization kinetics of 45S5 bioactive silicate glasses",
    doi: "10.1016/j.jnoncrysol.2023.122119",
    pii: "S0022-3093(23)00115-4",
    status: "success",
    tables_count: 2,
  },
  {
    paper_id: "paper_06_thermoelectrics",
    title: "Enhanced thermoelectric figure of merit in p-type Bi2Te3 alloys via grain boundary engineering",
    doi: "10.1016/j.actamat.2023.119022",
    pii: "S1359-6454(23)00269-2",
    status: "success",
    tables_count: 2,
  },
  {
    paper_id: "paper_07_solid_electrolytes",
    title: "Ionic conductivity and interfacial impedance of garnet-type LLZO solid-state electrolytes",
    doi: "10.1016/j.jpowsour.2023.232981",
    pii: "S0378-7753(23)00412-9",
    status: "success",
    tables_count: 2,
  },
  {
    paper_id: "paper_08_shape_memory",
    title: "Superelasticity and cyclic fatigue resistance of NiTi shape memory wires under thermal cycling",
    doi: "10.1016/j.msea.2023.145102",
    pii: "S0921-5093(23)00694-7",
    status: "success",
    tables_count: 2,
  },
  {
    paper_id: "paper_09_ultra_high_temp_ceramics",
    title: "Ablation resistance and mechanical behavior of ZrB2-SiC ultra-high temperature ceramics",
    doi: "10.1016/j.jeurceramsoc.2023.07.034",
    pii: "S0955-2219(23)00456-1",
    status: "success",
    tables_count: 2,
  },
  {
    paper_id: "paper_10_mxenes",
    title: "Electrochemical capacitance and electromagnetic shielding properties of delaminated Ti3C2Tx MXene films",
    doi: "10.1016/j.carbon.2023.118245",
    pii: "S0008-6223(23)00512-3",
    status: "success",
    tables_count: 2,
  },
];

export default function PapersPage() {
  const [papers, setPapers] = useState<PaperRecord[]>(BENCHMARK_PAPERS);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    listPapers()
      .then((data) => {
        if (data && data.length > 0) {
          setPapers(data);
        }
      })
      .catch(() => {});
  }, []);

  const filtered = papers.filter((p) => {
    const q = searchQuery.toLowerCase();
    return (
      p.title.toLowerCase().includes(q) ||
      p.doi.toLowerCase().includes(q) ||
      p.paper_id.toLowerCase().includes(q)
    );
  });

  return (
    <div className="space-y-6 max-w-6xl">
      {/* Page Heading */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-900">
            Ingested Research Papers
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Browse and inspect scientific publications processed by the MIT XML and PDF table extraction pipelines.
          </p>
        </div>

        <Link
          href="/upload"
          className="inline-flex items-center gap-1.5 rounded-md bg-slate-900 px-3.5 py-1.5 text-xs font-medium text-white shadow-sm hover:bg-slate-800 transition-colors"
        >
          Upload New Paper
        </Link>
      </div>

      {/* Search & Filter Bar */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search papers by title, DOI, or document ID..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full rounded-md border border-slate-300 pl-9 pr-4 py-2 text-xs text-slate-900 placeholder-slate-400 focus:border-sky-600 focus:outline-none focus:ring-1 focus:ring-sky-600 bg-white"
          />
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-500 font-medium">
            Showing <strong className="text-slate-800">{filtered.length}</strong> publications
          </span>
        </div>
      </div>

      {/* Papers Table */}
      <div className="rounded-lg border border-slate-200 bg-white shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="border-b border-slate-100 bg-slate-50/60 font-medium text-slate-500 uppercase">
              <tr>
                <th scope="col" className="px-6 py-3">
                  Document ID & Publication Title
                </th>
                <th scope="col" className="px-6 py-3">
                  Digital Object Identifier (DOI)
                </th>
                <th scope="col" className="px-6 py-3 text-center">
                  Tables
                </th>
                <th scope="col" className="px-6 py-3">
                  Status
                </th>
                <th scope="col" className="px-6 py-3 text-right">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.map((paper) => (
                <tr key={paper.paper_id} className="hover:bg-slate-50/70 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-start gap-2.5">
                      <div className="mt-0.5 flex h-7 w-7 flex-shrink-0 items-center justify-center rounded bg-slate-100 text-slate-600">
                        <FileText className="h-4 w-4" />
                      </div>
                      <div className="max-w-md">
                        <Link
                          href={`/papers/${paper.paper_id}`}
                          className="font-semibold text-slate-900 hover:text-sky-700 block transition-colors leading-snug"
                        >
                          {paper.title}
                        </Link>
                        <span className="font-mono text-[10px] text-slate-400 block mt-1">
                          {paper.paper_id}
                        </span>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <a
                      href={`https://doi.org/${paper.doi}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 font-mono text-[11px] text-sky-700 hover:text-sky-900 hover:underline"
                    >
                      {paper.doi}
                      <ExternalLink className="h-3 w-3" />
                    </a>
                  </td>
                  <td className="px-6 py-4 text-center font-mono text-slate-700 tabular-nums">
                    <span className="inline-flex items-center gap-1 rounded bg-slate-100 px-2 py-0.5 text-[11px]">
                      <Table2 className="h-3 w-3 text-slate-500" />
                      {paper.tables_count ?? 2}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex items-center rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-medium text-emerald-700 border border-emerald-200">
                      Indexed
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right whitespace-nowrap">
                    <Link
                      href={`/papers/${paper.paper_id}`}
                      className="inline-flex items-center gap-1 text-xs font-medium text-sky-700 hover:text-sky-900"
                    >
                      Inspect Verification Canvas
                      <ArrowRight className="h-3.5 w-3.5" />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
