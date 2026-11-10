"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Atom,
  X,
  Search,
  Sparkles,
  ChevronRight,
} from "lucide-react";

const CATEGORIES = [
  "All",
  "Titanium",
  "Batteries",
  "Dielectrics",
  "High-Entropy",
  "Bioglass",
  "Thermoelectric",
];

const BENCHMARK_MATERIALS = [
  {
    name: "Ti-6Al-4V (Grade 5)",
    cat: "Titanium",
    type: "Alpha-Beta Titanium Aerospace Alloy",
    comp: "Ti: 89.0%, Al: 6.2%, V: 4.1%, Fe: 0.2%",
    properties: [
      { name: "Yield Strength", val: "880 MPa" },
      { name: "Tensile Strength", val: "950 MPa" },
      { name: "Density", val: "4,430 kg/m³" },
    ],
    paper_id: "paper_01_ti_alloys",
  },
  {
    name: "LiNi0.8Mn0.1Co0.1O2 (NMC811)",
    cat: "Batteries",
    type: "Single-Crystal Battery Cathode Oxide",
    comp: "Ni: 80.0%, Mn: 10.0%, Co: 10.0%",
    properties: [
      { name: "Specific Capacity", val: "205.4 mAh/g" },
      { name: "Capacity Retention", val: "88.2%" },
      { name: "Thermal Runaway", val: "491.15 K (218 °C)" },
    ],
    paper_id: "paper_02_battery_cathodes",
  },
  {
    name: "BaTiO3 Perovskite",
    cat: "Dielectrics",
    type: "Lead-Free Ferroelectric Ceramic",
    comp: "BaO: 50.0%, TiO2: 50.0%",
    properties: [
      { name: "Dielectric Constant", val: "1,850 (εr)" },
      { name: "Curie Temp", val: "398.15 K (125 °C)" },
      { name: "Piezo d33", val: "190 pC/N" },
    ],
    paper_id: "paper_03_perovskite_dielectrics",
  },
  {
    name: "CoCrFeNi Cantor Alloy",
    cat: "High-Entropy",
    type: "Equiatomic Single-Phase FCC HEA",
    comp: "Co: 25%, Cr: 25%, Fe: 25%, Ni: 25%",
    properties: [
      { name: "Yield Strength", val: "215 MPa" },
      { name: "Ultimate Tensile", val: "580 MPa" },
      { name: "Elongation", val: "52.0%" },
    ],
    paper_id: "paper_04_high_entropy_alloys",
  },
  {
    name: "45S5 Bioglass",
    cat: "Bioglass",
    type: "Bioactive Silicate Bone Ceramic",
    comp: "SiO2: 45%, Na2O: 24.5%, CaO: 24.5%, P2O5: 6%",
    properties: [
      { name: "Glass Transition", val: "808.15 K (535 °C)" },
      { name: "Density", val: "2,700 kg/m³" },
    ],
    paper_id: "paper_05_bioactive_glasses",
  },
  {
    name: "Bi2Te3 p-Type",
    cat: "Thermoelectric",
    type: "Bismuth Telluride Thermoelectric Alloy",
    comp: "Bi: 40.0at.%, Te: 60.0at.%",
    properties: [
      { name: "Figure of Merit (ZT)", val: "1.42" },
      { name: "Seebeck Coeff", val: "220 µV/K" },
      { name: "Thermal Cond", val: "1.15 W/mK" },
    ],
    paper_id: "paper_06_thermoelectrics",
  },
];

interface MaterialsDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectMaterialQuery?: (query: string) => void;
}

export default function MaterialsDrawer({
  isOpen,
  onClose,
  onSelectMaterialQuery,
}: MaterialsDrawerProps) {
  const [selectedCat, setSelectedCat] = useState("All");
  const [search, setSearch] = useState("");

  if (!isOpen) return null;

  const filtered = BENCHMARK_MATERIALS.filter((m) => {
    const matchesCat = selectedCat === "All" || m.cat === selectedCat;
    const q = search.toLowerCase();
    const matchesSearch =
      m.name.toLowerCase().includes(q) ||
      m.comp.toLowerCase().includes(q) ||
      m.type.toLowerCase().includes(q);
    return matchesCat && matchesSearch;
  });

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-slate-900/40 backdrop-blur-xs animate-fadeIn">
      <div className="fixed inset-0" onClick={onClose} />

      <div className="relative w-full max-w-lg bg-white h-full shadow-2xl flex flex-col z-10 border-l border-slate-200">
        {/* Drawer Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-200 bg-slate-50/70">
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-900 text-white">
              <Atom className="h-4 w-4 text-sky-400" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-slate-900">
                Material Systems & Alloys
              </h2>
              <p className="text-[11px] text-slate-500">
                50 unique systems mapped to stoichiometric formulas and SI properties
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100 transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Category Pills & Search */}
        <div className="p-3 border-b border-slate-100 bg-white space-y-2">
          <div className="relative">
            <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search by alloy formula (e.g., Ti-6Al-4V, NMC811)..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 text-xs border border-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-sky-600 bg-slate-50/50"
            />
          </div>

          <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
            {CATEGORIES.map((c) => (
              <button
                key={c}
                onClick={() => setSelectedCat(c)}
                className={`px-2.5 py-1 text-[11px] font-medium rounded-full whitespace-nowrap transition-colors ${
                  selectedCat === c
                    ? "bg-slate-900 text-white"
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
              >
                {c}
              </button>
            ))}
          </div>
        </div>

        {/* Materials List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {filtered.map((m, idx) => (
            <div
              key={idx}
              className="p-4 rounded-xl border border-slate-200 bg-white hover:border-slate-300 transition-all space-y-2.5"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-xs font-bold text-slate-900">{m.name}</h3>
                  <p className="text-[11px] text-slate-500">{m.type}</p>
                </div>
                <span className="font-mono text-[10px] text-sky-700 bg-sky-50 px-2 py-0.5 rounded border border-sky-100">
                  {m.cat}
                </span>
              </div>

              <div className="bg-slate-50 p-2 rounded-lg border border-slate-100 font-mono text-[11px] text-slate-700">
                {m.comp}
              </div>

              <div className="grid grid-cols-2 gap-1.5">
                {m.properties.map((p, pIdx) => (
                  <div
                    key={pIdx}
                    className="p-1.5 rounded bg-slate-50/70 border border-slate-100 text-[10px]"
                  >
                    <span className="text-slate-400 block">{p.name}</span>
                    <span className="font-mono font-bold text-slate-800">{p.val}</span>
                  </div>
                ))}
              </div>

              <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs">
                <Link
                  href={`/papers/${m.paper_id}`}
                  className="font-mono text-[10px] text-slate-400 hover:text-sky-700 flex items-center gap-1"
                >
                  {m.paper_id}
                  <ChevronRight className="h-3 w-3" />
                </Link>

                <div className="flex items-center gap-1.5">
                  {onSelectMaterialQuery && (
                    <button
                      onClick={() => {
                        onSelectMaterialQuery(`Tell me about the composition and properties of ${m.name}`);
                        onClose();
                      }}
                      className="px-2.5 py-1 text-[11px] font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 rounded transition-colors"
                    >
                      Ask AI
                    </button>
                  )}
                  <Link
                    href={`/predictor?target=${encodeURIComponent(m.properties[0]?.name || "Yield Strength")}`}
                    className="px-2.5 py-1 text-[11px] font-medium text-sky-700 bg-sky-50 hover:bg-sky-100 rounded transition-colors flex items-center gap-1"
                  >
                    <Sparkles className="h-2.5 w-2.5" />
                    Predict
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="p-3 border-t border-slate-200 bg-slate-50 flex items-center justify-between text-xs text-slate-500">
          <span>Explore all 50 materials</span>
          <button
            onClick={onClose}
            className="px-3 py-1 bg-slate-900 text-white rounded-md text-xs font-medium hover:bg-slate-800"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
