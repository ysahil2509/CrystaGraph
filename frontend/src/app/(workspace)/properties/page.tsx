"use client";

import { useEffect, useState } from "react";
import {
  Search,
  ExternalLink,
  CheckCircle2,
} from "lucide-react";
import { listAllProperties } from "@/lib/api";

interface PropertyItem {
  prop_id: number;
  material_name: string;
  property_name: string;
  property_category: string;
  value_numeric: number;
  value_raw: string;
  unit: string;
  si_value: number;
  si_unit: string;
  source_type: string;
  condition_footnote?: string;
  paper_id: string;
  table_id: string;
  doi: string;
}

const CATEGORIES = [
  "All Categories",
  "Mechanical Properties",
  "Physical & Structural Properties",
  "Electrochemical & Energy Properties",
  "Dielectric & Piezoelectric",
  "Thermal & Kinetic Properties",
];

export default function PropertiesPage() {
  const [properties, setProperties] = useState<PropertyItem[]>([]);
  const [selectedCategory, setSelectedCategory] = useState("All Categories");
  const [searchQuery, setSearchQuery] = useState("");
  const [useSIUnits, setUseSIUnits] = useState(true);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    listAllProperties()
      .then((data) => {
        if (data && data.length > 0) {
          setProperties(data);
        }
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const filtered = properties.filter((p) => {
    const matchesCat =
      selectedCategory === "All Categories" ||
      p.property_category.toLowerCase().includes(selectedCategory.toLowerCase().slice(0, 8));
    const q = searchQuery.toLowerCase();
    const matchesQuery =
      p.material_name.toLowerCase().includes(q) ||
      p.property_name.toLowerCase().includes(q) ||
      p.paper_id.toLowerCase().includes(q);
    return matchesCat && matchesQuery;
  });

  return (
    <div className="space-y-6 max-w-7xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-900">
            Physical Property & SI Unit Explorer
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Browse 255 verified property measurements standardized from imperial and disparate
            literature units into canonical SI dimensions.
          </p>
        </div>

        {/* SI Unit Toggle */}
        <div className="inline-flex rounded-md border border-slate-300 bg-white p-1 text-xs shadow-sm">
          <button
            type="button"
            onClick={() => setUseSIUnits(true)}
            className={`px-3 py-1 rounded font-medium transition-colors ${
              useSIUnits ? "bg-slate-900 text-white" : "text-slate-600 hover:text-slate-900"
            }`}
          >
            Canonical SI Units
          </button>
          <button
            type="button"
            onClick={() => setUseSIUnits(false)}
            className={`px-3 py-1 rounded font-medium transition-colors ${
              !useSIUnits ? "bg-slate-900 text-white" : "text-slate-600 hover:text-slate-900"
            }`}
          >
            Reported Units
          </button>
        </div>
      </div>

      {/* Filter Row: Search & Category Chips */}
      <div className="space-y-3">
        <div className="relative">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input
            type="text"
            placeholder="Filter properties by material name, property (e.g. Yield Strength, Density, Curie Temp)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full rounded-md border border-slate-300 pl-9 pr-4 py-2 text-xs text-slate-900 focus:outline-none focus:ring-1 focus:ring-sky-600 bg-white"
          />
        </div>

        <div className="flex flex-wrap gap-1.5">
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              type="button"
              onClick={() => setSelectedCategory(cat)}
              className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
                selectedCategory === cat
                  ? "bg-sky-100 text-sky-900 border border-sky-300"
                  : "bg-white text-slate-600 border border-slate-200 hover:bg-slate-50"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Properties Table */}
      <div className="rounded-lg border border-slate-200 bg-white shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="border-b border-slate-100 bg-slate-50/60 font-medium text-slate-500 uppercase text-[11px]">
              <tr>
                <th scope="col" className="px-6 py-3">
                  Material Entity
                </th>
                <th scope="col" className="px-6 py-3">
                  Property Name
                </th>
                <th scope="col" className="px-6 py-3">
                  Category
                </th>
                <th scope="col" className="px-6 py-3 text-right">
                  {useSIUnits ? "Canonical SI Value" : "Reported Value"}
                </th>
                <th scope="col" className="px-6 py-3 text-center">
                  Provenance
                </th>
                <th scope="col" className="px-6 py-3 text-right">
                  DOI Citation
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-xs text-slate-400">
                    Loading property measurements...
                  </td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-xs text-slate-400">
                    No property records match the selected filter.
                  </td>
                </tr>
              ) : (
                filtered.map((item, idx) => (
                  <tr key={idx} className="hover:bg-slate-50/70 transition-colors">
                    <td className="px-6 py-3.5 font-bold text-slate-900 whitespace-nowrap">
                      {item.material_name}
                    </td>
                    <td className="px-6 py-3.5 text-slate-700 font-medium whitespace-nowrap">
                      {item.property_name}
                    </td>
                    <td className="px-6 py-3.5 text-slate-500 text-[11px] whitespace-nowrap">
                      {item.property_category || "General"}
                    </td>
                    <td className="px-6 py-3.5 text-right font-mono font-bold text-slate-900 whitespace-nowrap">
                      {useSIUnits ? (
                        <span>
                          {item.si_value ?? item.value_numeric}{" "}
                          <span className="text-[10px] text-slate-500 font-normal">
                            {item.si_unit || item.unit}
                          </span>
                        </span>
                      ) : (
                        <span>
                          {item.value_raw || item.value_numeric}{" "}
                          <span className="text-[10px] text-slate-500 font-normal">
                            {item.unit}
                          </span>
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-3.5 text-center font-mono text-[11px] text-slate-500 whitespace-nowrap">
                      <span className="inline-flex items-center gap-1 bg-slate-100 px-2 py-0.5 rounded">
                        <CheckCircle2 className="h-3 w-3 text-emerald-600" />
                        {item.table_id || "table"}
                      </span>
                    </td>
                    <td className="px-6 py-3.5 text-right whitespace-nowrap">
                      <a
                        href={`https://doi.org/${item.doi}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 font-mono text-[11px] text-sky-700 hover:underline"
                      >
                        {item.doi}
                        <ExternalLink className="h-2.5 w-2.5" />
                      </a>
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
