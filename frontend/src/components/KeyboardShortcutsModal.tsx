"use client";

import { X, Keyboard } from "lucide-react";

interface KeyboardShortcutsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const SHORTCUTS = [
  { keys: ["⌘", "K"], label: "Omnisearch / Command Palette", desc: "Search materials, papers, properties, or jump between pages" },
  { keys: ["⌘", "U"], label: "Quick SI Unit Converter", desc: "Convert literature units (MPa, GPa, g/cm³, °C, K, S/cm)" },
  { keys: ["ESC"], label: "Close Modal / Palette", desc: "Dismiss any active drawer, overlay, or search dialog" },
  { keys: ["?"], label: "Keyboard Shortcuts", desc: "Open this keyboard shortcut reference sheet" },
  { keys: ["↑", "↓"], label: "Navigate Results", desc: "Move selection in Command Palette and dropdowns" },
  { keys: ["↵"], label: "Execute / Jump", desc: "Confirm selection and jump to target view" },
];

export default function KeyboardShortcutsModal({
  isOpen,
  onClose,
}: KeyboardShortcutsModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-fadeIn">
      <div className="fixed inset-0" onClick={onClose} />

      <div className="relative w-full max-w-md bg-white rounded-xl shadow-2xl border border-slate-200 overflow-hidden z-10">
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-slate-200 bg-slate-50/70">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded bg-slate-900 text-white">
              <Keyboard className="h-4 w-4" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-900">
                Keyboard Shortcuts
              </h3>
              <p className="text-[10px] text-slate-400 font-mono">
                Speed up your daily materials research
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

        <div className="p-5 divide-y divide-slate-100">
          {SHORTCUTS.map((s, idx) => (
            <div key={idx} className="py-2.5 flex items-center justify-between gap-4 first:pt-0 last:pb-0">
              <div>
                <p className="text-xs font-semibold text-slate-900">{s.label}</p>
                <p className="text-[11px] text-slate-500">{s.desc}</p>
              </div>
              <div className="flex items-center gap-1 shrink-0">
                {s.keys.map((k, kIdx) => (
                  <kbd
                    key={kIdx}
                    className="px-2 py-1 text-xs font-mono font-semibold bg-slate-100 text-slate-700 border border-slate-200 rounded shadow-xs"
                  >
                    {k}
                  </kbd>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="px-5 py-3 bg-slate-50 border-t border-slate-200 text-right">
          <button
            onClick={onClose}
            className="px-3 py-1.5 text-xs font-medium bg-slate-900 text-white rounded-md hover:bg-slate-800 transition-colors"
          >
            Got it
          </button>
        </div>
      </div>
    </div>
  );
}

