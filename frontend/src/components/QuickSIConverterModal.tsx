"use client";

import { useState, useMemo } from "react";
import {
  Calculator,
  X,
  Copy,
  Check,
  ArrowRightLeft,
  Info,
} from "lucide-react";

interface ConverterCategory {
  id: string;
  name: string;
  units: { id: string; label: string; toSI: (v: number) => number; fromSI: (v: number) => number; isSI?: boolean }[];
  siUnit: string;
  notes: string;
}

const CATEGORIES: ConverterCategory[] = [
  {
    id: "pressure",
    name: "Mechanical Strength & Pressure",
    siUnit: "MPa (Standardized)",
    notes: "Literature commonly uses GPa for Young's Modulus and MPa for Yield / Tensile Strength.",
    units: [
      { id: "mpa", label: "MPa (Megapascals)", toSI: (v) => v, fromSI: (v) => v, isSI: true },
      { id: "gpa", label: "GPa (Gigapascals)", toSI: (v) => v * 1000, fromSI: (v) => v / 1000 },
      { id: "pa", label: "Pa (Pascals)", toSI: (v) => v / 1e6, fromSI: (v) => v * 1e6 },
      { id: "bar", label: "bar", toSI: (v) => v * 0.1, fromSI: (v) => v / 0.1 },
      { id: "psi", label: "psi (Pounds/sq.in)", toSI: (v) => v * 0.00689476, fromSI: (v) => v / 0.00689476 },
      { id: "ksi", label: "ksi (Kilopounds/sq.in)", toSI: (v) => v * 6.89476, fromSI: (v) => v / 6.89476 },
    ],
  },
  {
    id: "density",
    name: "Material Density",
    siUnit: "kg/m³ (Canonical SI)",
    notes: "Literature frequently lists density in g/cm³ (1 g/cm³ = 1000 kg/m³).",
    units: [
      { id: "g_cm3", label: "g/cm³ (Grams per cubic cm)", toSI: (v) => v * 1000, fromSI: (v) => v / 1000 },
      { id: "kg_m3", label: "kg/m³ (Canonical SI)", toSI: (v) => v, fromSI: (v) => v, isSI: true },
      { id: "g_ml", label: "g/mL", toSI: (v) => v * 1000, fromSI: (v) => v / 1000 },
      { id: "lb_ft3", label: "lb/ft³", toSI: (v) => v * 16.0185, fromSI: (v) => v / 16.0185 },
    ],
  },
  {
    id: "temperature",
    name: "Thermodynamic Temperature",
    siUnit: "K (Kelvin)",
    notes: "Absolute temperature is normalized to Kelvin: K = °C + 273.15.",
    units: [
      { id: "c", label: "°C (Celsius)", toSI: (v) => v + 273.15, fromSI: (v) => v - 273.15 },
      { id: "k", label: "K (Kelvin)", toSI: (v) => v, fromSI: (v) => v, isSI: true },
      { id: "f", label: "°F (Fahrenheit)", toSI: (v) => ((v - 32) * 5) / 9 + 273.15, fromSI: (v) => ((v - 273.15) * 9) / 5 + 32 },
    ],
  },
  {
    id: "electrical",
    name: "Electrical Conductivity",
    siUnit: "S/m (Siemens per meter)",
    notes: "Solid electrolytes and conductors frequently report in S/cm or mS/cm.",
    units: [
      { id: "s_cm", label: "S/cm (Siemens per cm)", toSI: (v) => v * 100, fromSI: (v) => v / 100 },
      { id: "s_m", label: "S/m (Canonical SI)", toSI: (v) => v, fromSI: (v) => v, isSI: true },
      { id: "ms_cm", label: "mS/cm (MilliSiemens per cm)", toSI: (v) => v * 0.1, fromSI: (v) => v / 0.1 },
      { id: "us_cm", label: "μS/cm (MicroSiemens per cm)", toSI: (v) => v * 0.0001, fromSI: (v) => v / 0.0001 },
    ],
  },
  {
    id: "thermal",
    name: "Thermal Conductivity",
    siUnit: "W/(m·K)",
    notes: "1 W/(m·K) = 0.00238846 cal/(s·cm·°C).",
    units: [
      { id: "w_mk", label: "W/(m·K) (Watts per meter-Kelvin)", toSI: (v) => v, fromSI: (v) => v, isSI: true },
      { id: "cal_scm_c", label: "cal/(s·cm·°C)", toSI: (v) => v * 418.68, fromSI: (v) => v / 418.68 },
      { id: "btu_hrft_f", label: "BTU/(hr·ft·°F)", toSI: (v) => v * 1.730735, fromSI: (v) => v / 1.730735 },
    ],
  },
];

interface QuickSIConverterModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function QuickSIConverterModal({
  isOpen,
  onClose,
}: QuickSIConverterModalProps) {
  const [selectedCatId, setSelectedCatId] = useState("pressure");
  const [inputValue, setInputValue] = useState<string>("880");
  const [fromUnitId, setFromUnitId] = useState<string>("mpa");
  const [toUnitId, setToUnitId] = useState<string>("gpa");
  const [copied, setCopied] = useState(false);

  const activeCategory = useMemo(
    () => CATEGORIES.find((c) => c.id === selectedCatId) || CATEGORIES[0],
    [selectedCatId]
  );

  // Update default units when category changes
  const handleCategoryChange = (catId: string) => {
    setSelectedCatId(catId);
    const cat = CATEGORIES.find((c) => c.id === catId);
    if (cat && cat.units.length >= 2) {
      setFromUnitId(cat.units[0].id);
      setToUnitId(cat.units[1].id);
      if (catId === "pressure") setInputValue("880");
      else if (catId === "density") setInputValue("4.43");
      else if (catId === "temperature") setInputValue("218");
      else if (catId === "electrical") setInputValue("0.05");
      else if (catId === "thermal") setInputValue("7.2");
    }
  };

  // Swap From / To units
  const handleSwapUnits = () => {
    const prevFrom = fromUnitId;
    setFromUnitId(toUnitId);
    setToUnitId(prevFrom);
  };

  // Perform unit conversion
  const conversionResult = useMemo(() => {
    const num = parseFloat(inputValue);
    if (isNaN(num)) return null;

    const fromUnit = activeCategory.units.find((u) => u.id === fromUnitId);
    const toUnit = activeCategory.units.find((u) => u.id === toUnitId);

    if (!fromUnit || !toUnit) return null;

    // Convert to canonical SI baseline, then from SI baseline to target unit
    const siValue = fromUnit.toSI(num);
    const converted = toUnit.fromSI(siValue);

    // Format with sensible scientific decimal precision
    let displayVal: string;
    if (Math.abs(converted) >= 10000 || (Math.abs(converted) > 0 && Math.abs(converted) < 0.001)) {
      displayVal = converted.toExponential(4);
    } else {
      displayVal = Number(converted.toFixed(4)).toString();
    }

    return {
      converted: displayVal,
      siValue: Number(siValue.toFixed(4)).toString(),
      fromLabel: fromUnit.label,
      toLabel: toUnit.label,
      isSame: fromUnitId === toUnitId,
    };
  }, [inputValue, fromUnitId, toUnitId, activeCategory]);

  const handleCopy = () => {
    if (!conversionResult) return;
    const text = `${conversionResult.converted} ${conversionResult.toLabel.split(" ")[0]}`;
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-fadeIn">
      <div className="fixed inset-0" onClick={onClose} />

      <div className="relative w-full max-w-lg bg-white rounded-xl shadow-2xl border border-slate-200 overflow-hidden z-10">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-slate-200 bg-slate-50/70">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded bg-sky-600 text-white">
              <Calculator className="h-4 w-4" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-900">
                Quick SI Unit Converter
              </h3>
              <p className="text-[10px] text-slate-400 font-mono">
                Standardize literature values to canonical SI
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 text-slate-400 hover:text-slate-600 rounded"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Category Pills */}
        <div className="p-4 border-b border-slate-100 flex gap-1.5 overflow-x-auto pb-3">
          {CATEGORIES.map((cat) => (
            <button
              key={cat.id}
              onClick={() => handleCategoryChange(cat.id)}
              className={`px-2.5 py-1 text-xs rounded-full whitespace-nowrap transition-colors font-medium ${
                selectedCatId === cat.id
                  ? "bg-slate-900 text-white"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              {cat.name.split(" ")[0]}
            </button>
          ))}
        </div>

        {/* Input & Unit Selection */}
        <div className="p-5 space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-600 mb-1">
              Input Value
            </label>
            <input
              type="number"
              step="any"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              className="w-full px-3 py-2 border border-slate-200 rounded-lg text-base font-semibold text-slate-900 focus:outline-none focus:ring-2 focus:ring-sky-500 font-mono"
              placeholder="e.g. 880"
            />
          </div>

          <div className="grid grid-cols-[1fr,auto,1fr] items-center gap-2">
            <div>
              <label className="block text-[11px] font-medium text-slate-500 mb-1">
                From Unit
              </label>
              <select
                value={fromUnitId}
                onChange={(e) => setFromUnitId(e.target.value)}
                className="w-full px-2.5 py-1.5 border border-slate-200 rounded-md text-xs text-slate-800 bg-white focus:outline-none focus:ring-1 focus:ring-sky-500"
              >
                {activeCategory.units.map((u) => (
                  <option key={u.id} value={u.id}>
                    {u.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="pt-5">
              <button
                onClick={handleSwapUnits}
                title="Swap units"
                className="p-1.5 rounded-md border border-slate-200 text-slate-500 hover:bg-slate-100 transition-colors"
              >
                <ArrowRightLeft className="h-3.5 w-3.5" />
              </button>
            </div>

            <div>
              <label className="block text-[11px] font-medium text-slate-500 mb-1">
                To Target Unit
              </label>
              <select
                value={toUnitId}
                onChange={(e) => setToUnitId(e.target.value)}
                className="w-full px-2.5 py-1.5 border border-slate-200 rounded-md text-xs text-slate-800 bg-white focus:outline-none focus:ring-1 focus:ring-sky-500"
              >
                {activeCategory.units.map((u) => (
                  <option key={u.id} value={u.id}>
                    {u.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Converted Output Display */}
          <div className="mt-4 p-4 rounded-lg bg-sky-50/70 border border-sky-100 flex items-center justify-between">
            <div>
              <span className="text-[10px] font-semibold text-sky-700 uppercase tracking-wider">
                Converted Output
              </span>
              <div className="flex items-baseline gap-2 mt-0.5">
                <span className="text-2xl font-bold font-mono text-slate-900">
                  {conversionResult?.converted ?? "—"}
                </span>
                <span className="text-xs font-semibold text-slate-600">
                  {conversionResult?.toLabel.split(" ")[0]}
                </span>
              </div>
            </div>

            <button
              onClick={handleCopy}
              disabled={!conversionResult}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-sky-800 bg-sky-100 hover:bg-sky-200 rounded-md transition-colors"
            >
              {copied ? (
                <>
                  <Check className="h-3.5 w-3.5 text-emerald-600" />
                  Copied!
                </>
              ) : (
                <>
                  <Copy className="h-3.5 w-3.5" />
                  Copy Value
                </>
              )}
            </button>
          </div>

          {/* Canonical SI notation footnote */}
          <div className="flex items-start gap-2 p-2.5 rounded bg-slate-50 text-[11px] text-slate-500 border border-slate-100">
            <Info className="h-3.5 w-3.5 text-sky-600 shrink-0 mt-0.5" />
            <span>{activeCategory.notes}</span>
          </div>
        </div>

        {/* Footer */}
        <div className="px-5 py-2.5 bg-slate-50 border-t border-slate-200 flex items-center justify-between text-xs text-slate-400">
          <span>Keyboard shortcut: <kbd className="font-mono bg-white px-1 py-0.5 rounded border border-slate-200">⌘U</kbd></span>
          <button
            onClick={onClose}
            className="text-xs text-slate-600 hover:text-slate-900 font-medium"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
}
