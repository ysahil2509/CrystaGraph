"use client";

import { useEffect, useState, useMemo } from "react";
import Link from "next/link";
import {
  Atom,
  Search,
  ChevronRight,
  SlidersHorizontal,
  Copy,
  Check,
  Sparkles,
  Download,
  Star,
} from "lucide-react";
import { searchKnowledge } from "@/lib/api";
import { useBookmarks } from "@/lib/useBookmarks";

interface MaterialKnowledgeItem {
  material_name: string;
  normalized_material?: string;
  composition_summary?: string;
  property_name: string;
  property_category?: string;
  value_numeric?: number;
  unit?: string;
  si_value?: number;
  si_unit?: string;
  paper_id: string;
  doi: string;
  table_id: string;
}

const CATEGORIES = [
  "All Systems",
  "Titanium Alloys",
  "Battery Cathodes",
  "Perovskite Ceramics",
  "High-Entropy Alloys",
  "Bioactive Glasses",
  "Thermoelectrics",
];

const DEFAULT_MATERIALS = [
  {
    name: "Ti-6Al-4V (Grade 5)",
    category: "Titanium Alloys",
    tag: "Alpha-Beta Titanium Alloy",
    composition: "Ti: 89.0wt.%, Al: 6.2wt.%, V: 4.1wt.%, Fe: 0.2wt.%",
    paper_id: "paper_01_ti_alloys",
    doi: "10.1016/j.msea.2023.144890",
    properties: [
      { name: "Yield Strength", val: "880 MPa", si: "880 MPa" },
      { name: "Tensile Strength", val: "950 MPa", si: "950 MPa" },
      { name: "Density", val: "4.43 g/cm³", si: "4430 kg/m³" },
      { name: "Hardness", val: "340 HV", si: "340 HV" },
    ],
  },
  {
    name: "LiNi0.8Mn0.1Co0.1O2 (NMC811)",
    category: "Battery Cathodes",
    tag: "High-Nickel Cathode Oxide",
    composition: "Ni: 80.0mol%, Mn: 10.0mol%, Co: 10.0mol%",
    paper_id: "paper_02_battery_cathodes",
    doi: "10.1016/j.ensm.2023.102844",
    properties: [
      { name: "Initial Discharge Capacity", val: "205.4 mAh/g", si: "205.4 mAh/g" },
      { name: "Capacity Retention", val: "88.2 %", si: "88.2 %" },
      { name: "Thermal Runaway Temperature", val: "218 °C", si: "491.15 K" },
    ],
  },
  {
    name: "BaTiO3 Lead-Free Perovskite",
    category: "Perovskite Ceramics",
    tag: "Piezoelectric Ceramic",
    composition: "Ba: 50.0mol%, Ti: 50.0mol%, O: 3.0mol%",
    paper_id: "paper_03_perovskite_dielectrics",
    doi: "10.1016/j.jeurceramsoc.2023.05.012",
    properties: [
      { name: "Dielectric Constant", val: "1850", si: "1850" },
      { name: "Curie Temperature", val: "125 °C", si: "398.15 K" },
      { name: "Piezoelectric Coefficient d33", val: "190 pC/N", si: "190 pC/N" },
    ],
  },
  {
    name: "CoCrFeNi High-Entropy Alloy",
    category: "High-Entropy Alloys",
    tag: "Equiatomic FCC Alloy",
    composition: "Co: 25.0at.%, Cr: 25.0at.%, Fe: 25.0at.%, Ni: 25.0at.%",
    paper_id: "paper_04_high_entropy_alloys",
    doi: "10.1016/j.actamat.2023.118942",
    properties: [
      { name: "Yield Strength", val: "215 MPa", si: "215 MPa" },
      { name: "Ultimate Tensile Strength", val: "580 MPa", si: "580 MPa" },
      { name: "Elongation at Break", val: "52.0 %", si: "52.0 %" },
    ],
  },
  {
    name: "45S5 Bioglass",
    category: "Bioactive Glasses",
    tag: "Bioactive Silicate Glass",
    composition: "SiO2: 45.0wt.%, Na2O: 24.5wt.%, CaO: 24.5wt.%, P2O5: 6.0wt.%",
    paper_id: "paper_05_bioactive_glasses",
    doi: "10.1016/j.jnoncrysol.2023.122119",
    properties: [
      { name: "Glass Transition Temperature", val: "535 °C", si: "808.15 K" },
      { name: "Crystallization Onset", val: "680 °C", si: "953.15 K" },
      { name: "Density", val: "2.70 g/cm³", si: "2700 kg/m³" },
    ],
  },
  {
    name: "Bi2Te3 p-Type Thermoelectric",
    category: "Thermoelectrics",
    tag: "Bismuth Telluride Alloy",
    composition: "Bi: 40.0at.%, Te: 60.0at.%",
    paper_id: "paper_06_thermoelectrics",
    doi: "10.1016/j.actamat.2023.119022",
    properties: [
      { name: "Figure of Merit (ZT)", val: "1.42", si: "1.42" },
      { name: "Seebeck Coefficient", val: "220 µV/K", si: "220 µV/K" },
      { name: "Thermal Conductivity", val: "1.15 W/mK", si: "1.15 W/mK" },
    ],
  },
];

export default function MaterialsPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("All Systems");
  const [activeResults, setActiveResults] = useState<MaterialKnowledgeItem[]>([]);
  const [useLiveSearch, setUseLiveSearch] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const { isBookmarked, toggleBookmark } = useBookmarks();

  useEffect(() => {
    if (searchQuery.trim().length > 1) {
      searchKnowledge(searchQuery.trim())
        .then((res) => {
          if (res && res.results && res.results.length > 0) {
            setActiveResults(res.results as unknown as MaterialKnowledgeItem[]);
            setUseLiveSearch(true);
          } else {
            setUseLiveSearch(false);
          }
        })
        .catch(() => setUseLiveSearch(false));
    } else {
      setUseLiveSearch(false);
    }
  }, [searchQuery]);

  const filteredDefaults = useMemo(() => {
    const q = searchQuery.toLowerCase();
    return DEFAULT_MATERIALS.filter((m) => {
      const matchesCategory =
        selectedCategory === "All Systems" || m.category === selectedCategory;
      const matchesSearch =
        !q ||
        m.name.toLowerCase().includes(q) ||
        m.composition.toLowerCase().includes(q) ||
        m.category.toLowerCase().includes(q);
      return matchesCategory && matchesSearch;
    });
  }, [searchQuery, selectedCategory]);

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleExportCSV = () => {
    const rows = [
      ["Material Name", "Category", "Composition", "Paper ID", "DOI", "Properties"],
    ];
    filteredDefaults.forEach((m) => {
      const propsStr = m.properties.map((p) => `${p.name}: ${p.si}`).join("; ");
      rows.push([m.name, m.category, m.composition, m.paper_id, m.doi, propsStr]);
    });

    const csvContent = "data:text/csv;charset=utf-8," + rows.map((e) => e.map((c) => `"${c}"`).join(",")).join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `crystagraph_materials_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6 max-w-6xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-900">
            Material Stoichiometry & Systems Explorer
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Explore 50 unique alloys, battery cathodes, dielectrics, and bioactive glasses mapped to
            their stoichiometric formulas and physical properties.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleExportCSV}
            className="inline-flex items-center gap-1.5 rounded-md border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50 transition-colors shadow-2xs"
          >
            <Download className="h-3.5 w-3.5 text-slate-500" />
            Export CSV
          </button>
          <Link
            href="/synthesize"
            className="inline-flex items-center gap-1.5 rounded-md bg-slate-900 px-3.5 py-1.5 text-xs font-medium text-white shadow-sm hover:bg-slate-800 transition-colors"
          >
            <SlidersHorizontal className="h-3.5 w-3.5" />
            Cross-Paper Comparison
          </Link>
        </div>
      </div>

      {/* Category Filter Pills */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-3 py-1.5 text-xs rounded-full whitespace-nowrap transition-colors font-medium ${
              selectedCategory === cat
                ? "bg-slate-900 text-white shadow-xs"
                : "bg-white border border-slate-200 text-slate-600 hover:bg-slate-50"
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Search Input */}
      <div className="relative">
        <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
        <input
          type="text"
          placeholder="Search by alloy formula (e.g., Ti-6Al-4V, NMC811, BaTiO3, 45S5, or element Ti, Ni, Fe)..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full rounded-md border border-slate-300 pl-9 pr-4 py-2 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-sky-600 bg-white shadow-sm"
        />
      </div>

      {/* Materials Cards Grid */}
      {!useLiveSearch ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredDefaults.map((mat, idx) => {
            const isPinned = isBookmarked(mat.name);
            return (
              <div
                key={idx}
                className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm space-y-4 hover:border-slate-300 transition-colors flex flex-col justify-between"
              >
                <div className="space-y-3">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-2.5">
                      <div className="flex h-8 w-8 items-center justify-center rounded bg-slate-100 text-slate-700">
                        <Atom className="h-4 w-4 text-sky-700" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <h2 className="text-sm font-bold text-slate-900">{mat.name}</h2>
                          <button
                            onClick={() =>
                              toggleBookmark({
                                id: mat.name,
                                type: "material",
                                title: mat.name,
                                subtitle: mat.tag,
                                url: `/materials?q=${encodeURIComponent(mat.name)}`,
                              })
                            }
                            title={isPinned ? "Remove pin" : "Pin to Daily Focus"}
                            className="text-slate-400 hover:text-amber-500 transition-colors"
                          >
                            <Star
                              className={`h-3.5 w-3.5 ${
                                isPinned ? "fill-amber-400 text-amber-500" : ""
                              }`}
                            />
                          </button>
                        </div>
                        <span className="text-[11px] text-slate-500">{mat.tag}</span>
                      </div>
                    </div>

                    <Link
                      href={`/papers/${mat.paper_id}`}
                      className="font-mono text-[10px] text-sky-700 hover:underline flex items-center gap-1 shrink-0"
                    >
                      {mat.paper_id}
                      <ChevronRight className="h-3 w-3" />
                    </Link>
                  </div>

                  {/* Stoichiometry Box */}
                  <div className="rounded bg-slate-50 p-2.5 border border-slate-100 text-xs">
                    <div className="flex items-center justify-between text-[10px] font-mono uppercase text-slate-400 mb-1">
                      <span>Elemental Stoichiometry</span>
                      <button
                        onClick={() => handleCopy(`comp-${idx}`, mat.composition)}
                        className="text-slate-400 hover:text-slate-600 flex items-center gap-1"
                        title="Copy composition"
                      >
                        {copiedId === `comp-${idx}` ? (
                          <>
                            <Check className="h-3 w-3 text-emerald-600" />
                            <span className="text-emerald-600">Copied</span>
                          </>
                        ) : (
                          <>
                            <Copy className="h-3 w-3" />
                            <span>Copy</span>
                          </>
                        )}
                      </button>
                    </div>
                    <p className="font-mono text-slate-800 text-[11px] font-medium leading-relaxed">
                      {mat.composition}
                    </p>
                  </div>

                  {/* Standardized Physical Properties */}
                  <div className="space-y-1.5">
                    <span className="text-[10px] font-mono uppercase text-slate-400">
                      Standardized SI Properties
                    </span>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      {mat.properties.map((p, pIdx) => (
                        <div
                          key={pIdx}
                          className="rounded bg-slate-50/70 border border-slate-100 p-2 flex flex-col justify-between"
                        >
                          <span className="text-[10px] text-slate-500 truncate">{p.name}</span>
                          <span className="font-mono font-bold text-slate-900 mt-0.5">
                            {p.si}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Card Actions Footer */}
                <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                  <span className="font-mono text-[10px] text-slate-400 truncate max-w-[180px]">
                    DOI: {mat.doi}
                  </span>
                  <Link
                    href={`/predictor?target=${encodeURIComponent(
                      mat.properties[0]?.name || "Yield Strength"
                    )}`}
                    className="inline-flex items-center gap-1 text-[11px] font-medium text-sky-700 hover:text-sky-900 bg-sky-50 hover:bg-sky-100 px-2.5 py-1 rounded transition-colors"
                  >
                    <Sparkles className="h-3 w-3 text-sky-600" />
                    Predict Alloy
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        /* Live Search Results from Knowledge Database */
        <div className="rounded-lg border border-slate-200 bg-white shadow-sm overflow-hidden">
          <div className="p-4 border-b border-slate-200 bg-slate-50/50 flex items-center justify-between text-xs text-slate-600">
            <span>
              Found <strong>{activeResults.length}</strong> material property triples matching &ldquo;
              {searchQuery}&rdquo;
            </span>
            <button
              onClick={() => setSearchQuery("")}
              className="text-sky-700 hover:underline"
            >
              Clear live search
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-700">
              <thead className="border-b border-slate-200 bg-slate-50/60 font-medium text-slate-500 uppercase">
                <tr>
                  <th className="px-5 py-3">Material</th>
                  <th className="px-5 py-3">Property</th>
                  <th className="px-5 py-3">Literature Value</th>
                  <th className="px-5 py-3">SI Standardized</th>
                  <th className="px-5 py-3">Paper & Table</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {activeResults.map((r, i) => (
                  <tr key={i} className="hover:bg-slate-50/60">
                    <td className="px-5 py-3 font-semibold text-slate-900">
                      {r.material_name}
                    </td>
                    <td className="px-5 py-3 text-slate-600">{r.property_name}</td>
                    <td className="px-5 py-3 font-mono text-slate-700">
                      {r.value_numeric} {r.unit}
                    </td>
                    <td className="px-5 py-3 font-mono font-bold text-sky-700">
                      {r.si_value ?? r.value_numeric} {r.si_unit ?? r.unit}
                    </td>
                    <td className="px-5 py-3">
                      <Link
                        href={`/papers/${r.paper_id}`}
                        className="font-mono text-sky-700 hover:underline"
                      >
                        {r.paper_id} &bull; {r.table_id}
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
