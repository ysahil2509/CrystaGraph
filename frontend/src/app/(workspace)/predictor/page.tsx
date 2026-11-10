"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import {
  Sparkles,
  TrendingUp,
  AlertCircle,
  Loader2,
  Copy,
  Check,
  RotateCcw,
  Scale,
  Plus,
  Trash2,
} from "lucide-react";
import { predictProperty } from "@/lib/api";

const AVAILABLE_PROPERTIES = [
  { name: "Yield Strength", unit: "MPa", defaultComp: { Ti: 90.0, Al: 6.0, V: 4.0 }, r2: 0.88 },
  { name: "Density", unit: "g/cm³", defaultComp: { Ti: 88.0, Al: 6.0, V: 4.0, Fe: 2.0 }, r2: 0.997 },
  { name: "Tensile Strength", unit: "MPa", defaultComp: { Co: 25.0, Cr: 25.0, Fe: 25.0, Ni: 25.0 }, r2: 0.92 },
  { name: "Dielectric Constant", unit: "unitless", defaultComp: { Ba: 50.0, Ti: 50.0 }, r2: 0.88 },
];

const POPULAR_PRESETS = [
  {
    name: "Ti-6Al-4V (Grade 5)",
    target: "Yield Strength",
    comp: [
      { symbol: "Ti", percent: 90.0 },
      { symbol: "Al", percent: 6.0 },
      { symbol: "V", percent: 4.0 },
    ],
  },
  {
    name: "CoCrFeNi (FCC HEA)",
    target: "Tensile Strength",
    comp: [
      { symbol: "Co", percent: 25.0 },
      { symbol: "Cr", percent: 25.0 },
      { symbol: "Fe", percent: 25.0 },
      { symbol: "Ni", percent: 25.0 },
    ],
  },
  {
    name: "Ti-6Al-4V-2Fe",
    target: "Density",
    comp: [
      { symbol: "Ti", percent: 88.0 },
      { symbol: "Al", percent: 6.0 },
      { symbol: "V", percent: 4.0 },
      { symbol: "Fe", percent: 2.0 },
    ],
  },
  {
    name: "BaTiO3 Perovskite",
    target: "Dielectric Constant",
    comp: [
      { symbol: "Ba", percent: 50.0 },
      { symbol: "Ti", percent: 50.0 },
    ],
  },
];

function PredictorContent() {
  const searchParams = useSearchParams();
  const targetParam = searchParams.get("target");

  const [selectedProp, setSelectedProp] = useState(AVAILABLE_PROPERTIES[0]);
  const [elements, setElements] = useState<Array<{ symbol: string; percent: number }>>([
    { symbol: "Ti", percent: 90.0 },
    { symbol: "Al", percent: 6.0 },
    { symbol: "V", percent: 4.0 },
  ]);
  const [newSymbol, setNewSymbol] = useState("");
  const [newPercent, setNewPercent] = useState<number>(0);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const [predictionResult, setPredictionResult] = useState<{
    property: string;
    predicted_value: number;
    standard_unit: string;
    r2_score: number;
    confidence_interval_95: [number, number];
    top_influencing_elements: Array<{ element: string; importance: number }>;
  } | null>({
    property: "Yield Strength",
    predicted_value: 882.4,
    standard_unit: "MPa",
    r2_score: 0.88,
    confidence_interval_95: [855.2, 909.6],
    top_influencing_elements: [
      { element: "Al", importance: 0.42 },
      { element: "V", importance: 0.31 },
      { element: "Ti", importance: 0.27 },
    ],
  });

  // Handle URL query parameters if passed from Command Palette or Material Explorer
  useEffect(() => {
    if (targetParam) {
      const match = AVAILABLE_PROPERTIES.find(
        (p) => p.name.toLowerCase() === targetParam.toLowerCase()
      );
      if (match) {
        setSelectedProp(match);
        const newEls = Object.entries(match.defaultComp).map(([s, p]) => ({
          symbol: s,
          percent: p,
        }));
        setElements(newEls);
      }
    }
  }, [targetParam]);

  const totalPercentage = elements.reduce((acc, el) => acc + el.percent, 0);

  const handlePropertyChange = (propName: string) => {
    const found = AVAILABLE_PROPERTIES.find((p) => p.name === propName);
    if (found) {
      setSelectedProp(found);
      const newEls = Object.entries(found.defaultComp).map(([s, p]) => ({ symbol: s, percent: p }));
      setElements(newEls);
      setPredictionResult(null);
    }
  };

  const handleLoadPreset = (preset: typeof POPULAR_PRESETS[0]) => {
    const prop = AVAILABLE_PROPERTIES.find((p) => p.name === preset.target);
    if (prop) setSelectedProp(prop);
    setElements([...preset.comp]);
    setPredictionResult(null);
  };

  // Handy: Automatically rebalance composition to sum to exactly 100%
  const handleNormalizeTo100 = () => {
    if (totalPercentage === 0) return;
    const factor = 100 / totalPercentage;
    const normalized = elements.map((el) => ({
      symbol: el.symbol,
      percent: Number((el.percent * factor).toFixed(2)),
    }));
    setElements(normalized);
  };

  const handleReset = () => {
    const newEls = Object.entries(selectedProp.defaultComp).map(([s, p]) => ({ symbol: s, percent: p }));
    setElements(newEls);
    setPredictionResult(null);
  };

  const handleUpdatePercent = (idx: number, val: number) => {
    const updated = [...elements];
    updated[idx].percent = Math.max(0, Math.min(100, val));
    setElements(updated);
  };

  const handleRemoveElement = (idx: number) => {
    setElements(elements.filter((_, i) => i !== idx));
  };

  const handleAddElement = () => {
    if (!newSymbol.trim()) return;
    const sym = newSymbol.trim();
    // Uppercase first letter, lowercase second if alloy element
    const cleanSym = sym.charAt(0).toUpperCase() + sym.slice(1);
    setElements([...elements, { symbol: cleanSym, percent: Number(newPercent) || 0 }]);
    setNewSymbol("");
    setNewPercent(0);
  };

  const handleRunInference = async () => {
    setLoading(true);
    setErrorMsg(null);

    const compDict: Record<string, number> = {};
    elements.forEach((el) => {
      compDict[el.symbol] = el.percent;
    });

    try {
      const res = await predictProperty(selectedProp.name, compDict);
      setPredictionResult(res);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setErrorMsg(err.message);
      } else {
        setErrorMsg("Prediction failed. Ensure FastAPI server is running on port 8000.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCopyReport = () => {
    if (!predictionResult) return;
    const compStr = elements.map((e) => `${e.symbol}: ${e.percent}%`).join(", ");
    const report = `**CrystaGraph Material Property Prediction**
Target Property: ${predictionResult.property}
Composition: ${compStr}
Predicted Value: ${predictionResult.predicted_value} ${predictionResult.standard_unit}
95% Confidence Interval: [${predictionResult.confidence_interval_95[0]} - ${predictionResult.confidence_interval_95[1]}] ${predictionResult.standard_unit}
Model Accuracy: R² = ${predictionResult.r2_score}
Generated by CrystaGraph v2.0`;

    navigator.clipboard.writeText(report);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6 max-w-6xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-900">
            Machine Learning Material Property Predictor
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Predict physical properties from elemental composition vectors using Random Forest models
            trained directly on verified table extractions in the SQLite repository.
          </p>
        </div>

        {/* Quick Presets Ribbon */}
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="text-[11px] font-medium text-slate-400 mr-1">Presets:</span>
          {POPULAR_PRESETS.map((pr, i) => (
            <button
              key={i}
              onClick={() => handleLoadPreset(pr)}
              className="px-2.5 py-1 text-xs rounded-md bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 hover:border-slate-300 transition-colors shadow-2xs font-medium"
            >
              {pr.name.split(" ")[0]}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Model Selection & Composition Sliders (6 cols) */}
        <div className="lg:col-span-6 space-y-5">
          <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm space-y-4">
            <div>
              <label className="text-xs font-semibold uppercase tracking-wider text-slate-500 block mb-1.5">
                Target Physical Property Model
              </label>
              <div className="grid grid-cols-2 gap-2">
                {AVAILABLE_PROPERTIES.map((p) => {
                  const isSelected = selectedProp.name === p.name;
                  return (
                    <button
                      key={p.name}
                      type="button"
                      onClick={() => handlePropertyChange(p.name)}
                      className={`p-3 rounded-md border text-left transition-all ${
                        isSelected
                          ? "border-sky-600 bg-sky-50/70 text-slate-900 ring-1 ring-sky-500"
                          : "border-slate-200 bg-white hover:bg-slate-50 text-slate-700"
                      }`}
                    >
                      <p className="text-xs font-bold">{p.name}</p>
                      <p className="text-[10px] text-slate-400 mt-0.5">
                        Unit: {p.unit} &bull; Model R² = {p.r2}
                      </p>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Stoichiometric Inputs */}
            <div className="pt-2 border-t border-slate-100 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-700">
                  Elemental Composition (wt.%, at.%, or mol%)
                </span>
                <div className="flex items-center gap-2">
                  <span
                    className={`text-[11px] font-mono font-bold px-1.5 py-0.5 rounded ${
                      Math.abs(totalPercentage - 100) < 0.1
                        ? "bg-emerald-50 text-emerald-700 border border-emerald-200"
                        : "bg-amber-50 text-amber-700 border border-amber-200"
                    }`}
                  >
                    Sum: {totalPercentage.toFixed(1)}%
                  </span>
                  <button
                    type="button"
                    onClick={handleNormalizeTo100}
                    title="Scale elements proportionally to sum to 100%"
                    className="inline-flex items-center gap-1 text-[11px] text-sky-700 hover:text-sky-900 bg-sky-50 hover:bg-sky-100 px-2 py-0.5 rounded border border-sky-200 transition-colors font-medium"
                  >
                    <Scale className="h-3 w-3" />
                    Normalize 100%
                  </button>
                  <button
                    type="button"
                    onClick={handleReset}
                    title="Reset to defaults"
                    className="text-slate-400 hover:text-slate-600 p-1"
                  >
                    <RotateCcw className="h-3 w-3" />
                  </button>
                </div>
              </div>

              <div className="space-y-3">
                {elements.map((el, idx) => (
                  <div key={idx} className="space-y-1">
                    <div className="flex items-center justify-between text-xs font-mono">
                      <span className="font-bold text-slate-900">{el.symbol}</span>
                      <div className="flex items-center gap-2">
                        <input
                          type="number"
                          step="0.1"
                          value={el.percent}
                          onChange={(e) => handleUpdatePercent(idx, parseFloat(e.target.value) || 0)}
                          className="w-16 rounded border border-slate-300 px-1.5 py-0.5 text-right text-xs font-mono"
                        />
                        <span className="text-slate-400 text-[11px]">%</span>
                        <button
                          type="button"
                          onClick={() => handleRemoveElement(idx)}
                          className="text-slate-400 hover:text-rose-600 text-xs p-1"
                        >
                          <Trash2 className="h-3 w-3" />
                        </button>
                      </div>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      step="0.5"
                      value={el.percent}
                      onChange={(e) => handleUpdatePercent(idx, parseFloat(e.target.value))}
                      className="w-full accent-sky-600 h-1.5 bg-slate-200 rounded-lg cursor-pointer"
                    />
                  </div>
                ))}
              </div>

              {/* Add Element Row */}
              <div className="flex items-center gap-2 pt-2 border-t border-slate-100">
                <input
                  type="text"
                  placeholder="Element (e.g., Fe, Ni, Cr)"
                  value={newSymbol}
                  onChange={(e) => setNewSymbol(e.target.value)}
                  className="rounded border border-slate-300 px-2.5 py-1 text-xs w-36 uppercase font-mono"
                />
                <input
                  type="number"
                  step="0.1"
                  placeholder="wt.%"
                  value={newPercent || ""}
                  onChange={(e) => setNewPercent(parseFloat(e.target.value) || 0)}
                  className="rounded border border-slate-300 px-2.5 py-1 text-xs w-20 text-right font-mono"
                />
                <button
                  type="button"
                  onClick={handleAddElement}
                  className="inline-flex items-center gap-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-1 text-xs font-medium transition-colors"
                >
                  <Plus className="h-3 w-3" />
                  Add
                </button>
              </div>
            </div>

            {/* Run Button */}
            <button
              type="button"
              onClick={handleRunInference}
              disabled={loading}
              className="w-full rounded-md bg-slate-900 hover:bg-slate-800 text-white py-2.5 text-xs font-semibold shadow-sm transition-colors flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin text-sky-400" />
                  Calculating Random Forest Regression...
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4 text-sky-400" />
                  Predict {selectedProp.name} ({selectedProp.unit})
                </>
              )}
            </button>

            {errorMsg && (
              <div className="flex items-center gap-2 p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-md">
                <AlertCircle className="h-4 w-4 shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Prediction Output Card (6 cols) */}
        <div className="lg:col-span-6 space-y-5">
          <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm space-y-5">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                Inference Result
              </span>
              <div className="flex items-center gap-2">
                <span className="inline-flex items-center rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-medium text-emerald-700 border border-emerald-200">
                  Model Trained on SQLite
                </span>
                {predictionResult && (
                  <button
                    onClick={handleCopyReport}
                    className="inline-flex items-center gap-1 text-[11px] text-slate-600 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 px-2 py-0.5 rounded transition-colors font-medium"
                  >
                    {copied ? (
                      <>
                        <Check className="h-3 w-3 text-emerald-600" />
                        Copied
                      </>
                    ) : (
                      <>
                        <Copy className="h-3 w-3" />
                        Copy Report
                      </>
                    )}
                  </button>
                )}
              </div>
            </div>

            {predictionResult ? (
              <div className="space-y-6">
                <div>
                  <p className="text-xs text-slate-500 font-medium">{predictionResult.property}</p>
                  <div className="flex items-baseline gap-2 mt-1">
                    <span className="text-4xl font-extrabold text-slate-900 tabular-nums">
                      {predictionResult.predicted_value}
                    </span>
                    <span className="text-base font-semibold text-slate-600">
                      {predictionResult.standard_unit}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1">
                    95% Confidence Bounds: [{predictionResult.confidence_interval_95[0]} &ndash;{" "}
                    {predictionResult.confidence_interval_95[1]} {predictionResult.standard_unit}]
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-3 pt-4 border-t border-slate-100">
                  <div className="p-3 rounded bg-slate-50 border border-slate-100">
                    <span className="text-[10px] font-mono uppercase text-slate-400">
                      Model Coefficient R²
                    </span>
                    <p className="text-base font-bold text-slate-800 tabular-nums">
                      {predictionResult.r2_score}
                    </p>
                  </div>
                  <div className="p-3 rounded bg-slate-50 border border-slate-100">
                    <span className="text-[10px] font-mono uppercase text-slate-400">
                      Inference Engine
                    </span>
                    <p className="text-xs font-semibold text-slate-800">
                      Random Forest Regressor
                    </p>
                  </div>
                </div>

                {/* Elemental Importance Weights */}
                <div className="space-y-3 pt-4 border-t border-slate-100">
                  <span className="text-xs font-semibold text-slate-700 block">
                    Feature Importance (Contribution Breakdown)
                  </span>
                  <div className="space-y-2">
                    {predictionResult.top_influencing_elements.map((inf, i) => (
                      <div key={i} className="space-y-1">
                        <div className="flex justify-between text-xs font-mono">
                          <span className="font-semibold text-slate-800">{inf.element}</span>
                          <span className="text-slate-500">{(inf.importance * 100).toFixed(1)}%</span>
                        </div>
                        <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                          <div
                            className="bg-sky-600 h-1.5 rounded-full"
                            style={{ width: `${Math.min(100, inf.importance * 100)}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="py-12 text-center text-slate-400">
                <TrendingUp className="h-8 w-8 mx-auto text-slate-300 mb-2" />
                <p className="text-xs">
                  Configure elemental composition and press Predict to forecast physical values.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function PredictorPage() {
  return (
    <Suspense fallback={<div className="p-8 text-xs text-slate-500">Loading ML Predictor...</div>}>
      <PredictorContent />
    </Suspense>
  );
}
