"use client";

import { useEffect, useState, useMemo, useRef } from "react";
import { useRouter } from "next/navigation";
import {
  Search,
  LayoutDashboard,
  UploadCloud,
  FileText,
  Table2,
  Atom,
  SlidersHorizontal,
  GitCompare,
  Bot,
  Sparkles,
  Calculator,
  X,
} from "lucide-react";
import { searchKnowledge } from "@/lib/api";

interface CommandItem {
  id: string;
  category: "Navigation" | "Quick Action" | "Material" | "Property Target";
  title: string;
  subtitle?: string;
  icon: React.ComponentType<{ className?: string }>;
  href?: string;
  action?: () => void;
  badge?: string;
}

const STATIC_COMMANDS: CommandItem[] = [
  // Navigation
  {
    id: "nav-dashboard",
    category: "Navigation",
    title: "Workspace Dashboard",
    subtitle: "High-level metrics, paper status, and database overview",
    icon: LayoutDashboard,
    href: "/dashboard",
  },
  {
    id: "nav-upload",
    category: "Navigation",
    title: "Upload Scientific Papers",
    subtitle: "Ingest XML/PDF papers with automatic table & SI extraction",
    icon: UploadCloud,
    href: "/upload",
    badge: "Upload",
  },
  {
    id: "nav-papers",
    category: "Navigation",
    title: "Paper Explorer",
    subtitle: "Browse 10 benchmark materials science papers with XML previews",
    icon: FileText,
    href: "/papers",
  },
  {
    id: "nav-tables",
    category: "Navigation",
    title: "Table Explorer",
    subtitle: "Inspect multi-row/col normalized experimental research tables",
    icon: Table2,
    href: "/tables",
  },
  {
    id: "nav-materials",
    category: "Navigation",
    title: "Material Explorer",
    subtitle: "Query compositions, elemental wt%/mol% stoichiometry & properties",
    icon: Atom,
    href: "/materials",
  },
  {
    id: "nav-properties",
    category: "Navigation",
    title: "Property Explorer",
    subtitle: "Standardized SI physical properties (MPa, kg/m³, K, S/m)",
    icon: SlidersHorizontal,
    href: "/properties",
  },
  {
    id: "nav-synthesize",
    category: "Navigation",
    title: "10-Paper Cross Synthesizer",
    subtitle: "Unified cross-paper Ashby comparison matrix across 10 articles",
    icon: GitCompare,
    href: "/synthesize",
    badge: "10-Paper Matrix",
  },
  {
    id: "nav-copilot",
    category: "Navigation",
    title: "AI Copilot (CrystaBot)",
    subtitle: "Interactive conversational Q&A grounded on research papers",
    icon: Bot,
    href: "/assistant",
    badge: "Grounded AI",
  },
  {
    id: "nav-predictor",
    category: "Navigation",
    title: "ML Property Predictor",
    subtitle: "Random Forest regression inference for novel alloy formulations",
    icon: Sparkles,
    href: "/predictor",
    badge: "R²=0.99",
  },

  // Quick Actions & Popular Material Systems
  {
    id: "action-ti-alloy",
    category: "Material",
    title: "Ti-6Al-4V (Grade 5 Titanium)",
    subtitle: "Aerospace alloy: Yield 880 MPa, Tensile 950 MPa, Density 4.43 g/cm³",
    icon: Atom,
    href: "/materials?q=Ti-6Al-4V",
  },
  {
    id: "action-nmc811",
    category: "Material",
    title: "LiNi0.8Mn0.1Co0.1O2 (NMC811 Cathode)",
    subtitle: "Battery cathode: 205.4 mAh/g capacity, 88.2% retention",
    icon: Atom,
    href: "/materials?q=NMC811",
  },
  {
    id: "action-batio3",
    category: "Material",
    title: "BaTiO3 Lead-Free Perovskite",
    subtitle: "Dielectric ceramic: Dielectric const 1850, Curie temp 125 °C",
    icon: Atom,
    href: "/materials?q=BaTiO3",
  },
  {
    id: "action-hea",
    category: "Material",
    title: "CoCrFeNi High-Entropy Alloy",
    subtitle: "Equiatomic FCC: Yield 215 MPa, Ultimate Tensile 580 MPa",
    icon: Atom,
    href: "/materials?q=CoCrFeNi",
  },
  {
    id: "action-pred-yield",
    category: "Property Target",
    title: "Predict Yield Strength (MPa)",
    subtitle: "Input elemental wt% (Ti, Al, V, Fe) -> R²=0.88 estimation",
    icon: Sparkles,
    href: "/predictor?target=Yield+Strength",
  },
  {
    id: "action-pred-density",
    category: "Property Target",
    title: "Predict Theoretical Density (g/cm³)",
    subtitle: "Rule of mixtures & Random Forest regression -> R²=0.997 estimation",
    icon: Sparkles,
    href: "/predictor?target=Density",
  },
];

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  onOpenSIConverter: () => void;
}

export default function CommandPalette({
  isOpen,
  onClose,
  onOpenSIConverter,
}: CommandPaletteProps) {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [liveResults, setLiveResults] = useState<CommandItem[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // Focus input on open
  useEffect(() => {
    if (isOpen) {
      setQuery("");
      setSelectedIndex(0);
      setLiveResults([]);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [isOpen]);

  // Live database search debounced
  useEffect(() => {
    const q = query.trim();
    if (q.length < 2) {
      setLiveResults([]);
      return;
    }

    const timer = setTimeout(async () => {
      setIsSearching(true);
      try {
        const res = await searchKnowledge(q);
        if (res && res.results && res.results.length > 0) {
          const items: CommandItem[] = (res.results as Array<Record<string, unknown>>).slice(0, 5).map((r, idx: number) => {
            const matName = String(r.material_name || "Extracted Material");
            const propName = String(r.property_name || "Property");
            const valNum = r.value_numeric !== undefined ? String(r.value_numeric) : "";
            const unit = String(r.unit || "");
            const doi = String(r.doi || "paper");
            return {
              id: `live-${idx}-${matName}`,
              category: "Material",
              title: matName,
              subtitle: `${propName}: ${valNum} ${unit} (DOI: ${doi})`,
              icon: Atom,
              href: `/materials?q=${encodeURIComponent(matName)}`,
              badge: propName,
            };
          });
          setLiveResults(items);
        } else {
          setLiveResults([]);
        }
      } catch {
        setLiveResults([]);
      } finally {
        setIsSearching(false);
      }
    }, 250);

    return () => clearTimeout(timer);
  }, [query]);

  // Filter static commands
  const filteredCommands = useMemo(() => {
    const q = query.toLowerCase().trim();
    const actions: CommandItem[] = [
      {
        id: "action-si-converter",
        category: "Quick Action",
        title: "Quick SI Unit Converter (⌘U)",
        subtitle: "Instant conversion between MPa, GPa, g/cm³, kg/m³, °C, K, S/cm",
        icon: Calculator,
        action: () => {
          onClose();
          onOpenSIConverter();
        },
        badge: "Tool",
      },
    ];

    const baseList = [...actions, ...STATIC_COMMANDS];
    if (!q) return baseList;

    const filteredStatic = baseList.filter(
      (cmd) =>
        cmd.title.toLowerCase().includes(q) ||
        (cmd.subtitle && cmd.subtitle.toLowerCase().includes(q)) ||
        cmd.category.toLowerCase().includes(q)
    );

    // Merge live results on top of static matching
    return [...liveResults, ...filteredStatic];
  }, [query, liveResults, onOpenSIConverter, onClose]);

  // Keep selected index within bounds
  useEffect(() => {
    setSelectedIndex(0);
  }, [query, filteredCommands.length]);

  // Keyboard navigation inside palette
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setSelectedIndex((prev) => (prev + 1) % Math.max(1, filteredCommands.length));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setSelectedIndex((prev) =>
        prev === 0 ? Math.max(0, filteredCommands.length - 1) : prev - 1
      );
    } else if (e.key === "Enter") {
      e.preventDefault();
      const current = filteredCommands[selectedIndex];
      if (current) {
        executeItem(current);
      }
    } else if (e.key === "Escape") {
      e.preventDefault();
      onClose();
    }
  };

  const executeItem = (item: CommandItem) => {
    onClose();
    if (item.action) {
      item.action();
    } else if (item.href) {
      router.push(item.href);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-16 sm:pt-24 px-4 bg-slate-900/40 backdrop-blur-sm animate-fadeIn">
      {/* Background click overlay */}
      <div className="fixed inset-0" onClick={onClose} />

      <div className="relative w-full max-w-2xl bg-white rounded-xl shadow-2xl border border-slate-200 overflow-hidden z-10 flex flex-col max-h-[80vh]">
        {/* Search Input Bar */}
        <div className="flex items-center px-4 py-3.5 border-b border-slate-200 gap-3 bg-slate-50/50">
          <Search className="h-5 w-5 text-slate-400 shrink-0" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a command, alloy formula (e.g. Ti-6Al-4V, NMC811), or page..."
            className="w-full bg-transparent text-sm text-slate-900 placeholder-slate-400 focus:outline-none"
          />
          {isSearching && (
            <span className="text-xs text-sky-600 font-mono animate-pulse">
              Searching...
            </span>
          )}
          {query && (
            <button
              onClick={() => setQuery("")}
              className="p-1 text-slate-400 hover:text-slate-600 rounded"
            >
              <X className="h-4 w-4" />
            </button>
          )}
          <kbd className="hidden sm:inline-block px-1.5 py-0.5 text-[10px] font-mono text-slate-400 bg-white border border-slate-200 rounded shadow-xs">
            ESC
          </kbd>
        </div>

        {/* Results list */}
        <div className="overflow-y-auto p-2 divide-y divide-slate-100 flex-1">
          {filteredCommands.length === 0 ? (
            <div className="py-12 text-center text-slate-500">
              <Atom className="h-8 w-8 mx-auto text-slate-300 mb-2" />
              <p className="text-sm font-medium">No results found for &ldquo;{query}&rdquo;</p>
              <p className="text-xs text-slate-400 mt-1">
                Try searching for alloy names (Ti-6Al-4V), properties (Yield Strength), or pages.
              </p>
            </div>
          ) : (
            <div className="space-y-0.5">
              {filteredCommands.map((item, idx) => {
                const isSelected = idx === selectedIndex;
                const Icon = item.icon;
                return (
                  <div
                    key={item.id}
                    onClick={() => executeItem(item)}
                    onMouseEnter={() => setSelectedIndex(idx)}
                    className={`flex items-center justify-between px-3 py-2.5 rounded-lg cursor-pointer transition-colors ${
                      isSelected
                        ? "bg-sky-50 text-sky-900 border border-sky-100"
                        : "text-slate-700 hover:bg-slate-50"
                    }`}
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <div
                        className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-md ${
                          isSelected
                            ? "bg-sky-600 text-white"
                            : "bg-slate-100 text-slate-600"
                        }`}
                      >
                        <Icon className="h-4 w-4" />
                      </div>
                      <div className="truncate">
                        <div className="flex items-center gap-2">
                          <p className="text-xs font-semibold truncate text-slate-900">
                            {item.title}
                          </p>
                          <span className="text-[10px] font-mono text-slate-400 uppercase">
                            {item.category}
                          </span>
                        </div>
                        {item.subtitle && (
                          <p className="text-[11px] text-slate-500 truncate mt-0.5">
                            {item.subtitle}
                          </p>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-2 shrink-0 ml-3">
                      {item.badge && (
                        <span className="text-[10px] px-1.5 py-0.5 rounded font-mono bg-slate-100 text-slate-600">
                          {item.badge}
                        </span>
                      )}
                      {isSelected && (
                        <kbd className="hidden sm:inline-flex items-center gap-0.5 text-[10px] font-mono text-sky-700 bg-sky-100 px-1.5 py-0.5 rounded">
                          <span>↵</span> Jump
                        </kbd>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Footer shortcuts helper */}
        <div className="px-4 py-2 bg-slate-50 border-t border-slate-200 flex items-center justify-between text-[11px] text-slate-500">
          <div className="flex items-center gap-3">
            <span className="flex items-center gap-1">
              <kbd className="px-1 py-0.5 font-mono text-[10px] bg-white border border-slate-200 rounded">
                ↑
              </kbd>
              <kbd className="px-1 py-0.5 font-mono text-[10px] bg-white border border-slate-200 rounded">
                ↓
              </kbd>{" "}
              Navigate
            </span>
            <span className="flex items-center gap-1">
              <kbd className="px-1 py-0.5 font-mono text-[10px] bg-white border border-slate-200 rounded">
                ↵
              </kbd>{" "}
              Select
            </span>
          </div>
          <span className="font-mono text-[10px] text-slate-400">
            CrystaGraph Omnisearch
          </span>
        </div>
      </div>
    </div>
  );
}
