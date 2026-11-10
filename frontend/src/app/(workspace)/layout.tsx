"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  LayoutDashboard,
  UploadCloud,
  FileText,
  Table2,
  Atom,
  SlidersHorizontal,
  GitCompare,
  Bot,
  Sparkles,
  LogOut,
  ChevronRight,
  Building2,
  Search,
  Calculator,
  Keyboard,
} from "lucide-react";
import { useAuth } from "@/lib/AuthContext";
import CommandPalette from "@/components/CommandPalette";
import QuickSIConverterModal from "@/components/QuickSIConverterModal";
import KeyboardShortcutsModal from "@/components/KeyboardShortcutsModal";
import ApiStatusIndicator from "@/components/ApiStatusIndicator";

const NAV_ITEMS = [
  {
    name: "Workspace Dashboard",
    href: "/dashboard",
    icon: LayoutDashboard,
    badge: null,
  },
  {
    name: "Upload Papers",
    href: "/upload",
    icon: UploadCloud,
    badge: "PDF / XML",
  },
  {
    name: "Paper Explorer",
    href: "/papers",
    icon: FileText,
    badge: null,
  },
  {
    name: "Table Explorer",
    href: "/tables",
    icon: Table2,
    badge: null,
  },
  {
    name: "Material Explorer",
    href: "/materials",
    icon: Atom,
    badge: null,
  },
  {
    name: "Property Explorer",
    href: "/properties",
    icon: SlidersHorizontal,
    badge: "SI Units",
  },
  {
    name: "Cross-Paper Synthesizer",
    href: "/synthesize",
    icon: GitCompare,
    badge: "10 Papers",
  },
  {
    name: "AI Copilot (CrystaBot)",
    href: "/assistant",
    icon: Bot,
    badge: "Grounded",
  },
  {
    name: "ML Property Predictor",
    href: "/predictor",
    icon: Sparkles,
    badge: "R²=0.99",
  },
];

export default function WorkspaceLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuth();

  const [isCommandOpen, setIsCommandOpen] = useState(false);
  const [isSIModalOpen, setIsSIModalOpen] = useState(false);
  const [isShortcutsOpen, setIsShortcutsOpen] = useState(false);

  // Global Keyboard Shortcuts (⌘K, ⌘U, ?)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't trigger if user is typing in a textarea or text input
      const target = e.target as HTMLElement;
      const isInput =
        target.tagName === "INPUT" ||
        target.tagName === "TEXTAREA" ||
        target.isContentEditable;

      // Command + K or Ctrl + K
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setIsCommandOpen((prev) => !prev);
      }
      // Command + U or Ctrl + U (Quick SI Converter)
      else if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "u") {
        e.preventDefault();
        setIsSIModalOpen((prev) => !prev);
      }
      // Question mark (?) for shortcuts cheat sheet
      else if (e.key === "?" && !isInput && !e.metaKey && !e.ctrlKey) {
        e.preventDefault();
        setIsShortcutsOpen((prev) => !prev);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const handleSignOut = () => {
    logout();
    router.push("/login");
  };

  const getInitials = (name?: string) => {
    if (!name) return "AC";
    const parts = name.split(" ").filter(Boolean);
    if (parts.length >= 2) return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
    return name.slice(0, 2).toUpperCase();
  };

  return (
    <div className="flex min-h-screen bg-slate-50 text-slate-900">
      {/* Sidebar */}
      <aside className="w-64 flex-shrink-0 border-r border-slate-200 bg-white flex flex-col justify-between">
        <div>
          {/* Brand header */}
          <div className="flex h-16 items-center justify-between border-b border-slate-200 px-5">
            <Link href="/" className="flex items-center gap-2.5">
              <div className="flex h-8 w-8 items-center justify-center rounded bg-slate-900 text-white font-semibold">
                <Atom className="h-4 w-4 text-sky-400" />
              </div>
              <div>
                <span className="text-sm font-bold tracking-tight text-slate-900">
                  CrystaGraph
                </span>
                <span className="block text-[10px] font-mono text-slate-400">
                  v2.0 Academic
                </span>
              </div>
            </Link>
          </div>

          {/* Workspace label */}
          <div className="px-5 py-2.5 border-b border-slate-100 bg-slate-50/60 flex items-center justify-between">
            <div>
              <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                Active Workspace
              </p>
              <p className="text-xs font-medium text-slate-700 truncate mt-0.5">
                Materials Informatics Lab
              </p>
            </div>
            <span className="text-[10px] px-1.5 py-0.5 font-mono text-slate-500 bg-white border border-slate-200 rounded">
              BMU
            </span>
          </div>

          {/* Quick Omnisearch Trigger Button in Sidebar */}
          <div className="p-3 pb-1">
            <button
              onClick={() => setIsCommandOpen(true)}
              className="w-full flex items-center justify-between px-3 py-2 text-xs text-slate-500 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-lg transition-colors group"
            >
              <span className="flex items-center gap-2">
                <Search className="h-3.5 w-3.5 text-slate-400 group-hover:text-slate-600" />
                <span>Quick Search...</span>
              </span>
              <kbd className="px-1.5 py-0.5 text-[10px] font-mono bg-white border border-slate-200 rounded text-slate-400 shadow-xs">
                ⌘K
              </kbd>
            </button>
          </div>

          {/* Navigation links */}
          <nav className="p-3 pt-1 space-y-1">
            {NAV_ITEMS.map((item) => {
              const isActive = pathname === item.href;
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center justify-between rounded-md px-3 py-2 text-xs font-medium transition-colors ${
                    isActive
                      ? "bg-sky-50 text-sky-800 font-semibold border border-sky-100"
                      : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    <Icon
                      className={`h-4 w-4 ${
                        isActive ? "text-sky-700" : "text-slate-400"
                      }`}
                      strokeWidth={1.75}
                    />
                    <span>{item.name}</span>
                  </div>
                  {item.badge && (
                    <span
                      className={`text-[10px] px-1.5 py-0.5 rounded font-mono ${
                        isActive
                          ? "bg-sky-200/60 text-sky-800"
                          : "bg-slate-100 text-slate-500"
                      }`}
                    >
                      {item.badge}
                    </span>
                  )}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Footer info & system health */}
        <div className="p-4 border-t border-slate-200 bg-slate-50/50 space-y-3">
          <div className="flex items-center justify-between text-[11px] text-slate-500">
            <span className="flex items-center gap-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500"></span>
              SQLite Online
            </span>
            <span className="font-mono text-slate-400">matgraph.db</span>
          </div>

          <div className="flex items-center justify-between border-t border-slate-200/60 pt-2.5 text-xs text-slate-700">
            <div className="flex items-center gap-2">
              <div className="flex h-7 w-7 items-center justify-center rounded-full bg-slate-200 text-slate-700 font-semibold text-[11px]">
                {getInitials(user?.full_name)}
              </div>
              <div className="truncate max-w-[130px]">
                <p className="text-[11px] font-medium leading-none text-slate-900 truncate">
                  {user?.full_name || "Academic Researcher"}
                </p>
                <p className="text-[10px] text-slate-400 leading-none mt-1 capitalize truncate">
                  {user?.role || "Researcher"}
                </p>
              </div>
            </div>
            <button
              onClick={handleSignOut}
              title="Sign out"
              type="button"
              className="text-slate-400 hover:text-slate-600 p-1 rounded hover:bg-slate-100 transition-colors"
            >
              <LogOut className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Workspace Header */}
        <header className="h-16 border-b border-slate-200 bg-white flex items-center justify-between px-6 z-10 gap-4">
          {/* Breadcrumb / Institute tag */}
          <div className="flex items-center gap-2.5 text-xs text-slate-500 shrink-0">
            <Building2 className="h-4 w-4 text-slate-400" />
            <span className="font-medium text-slate-700 hidden sm:inline">
              BML Munjal University
            </span>
            <ChevronRight className="h-3.5 w-3.5 text-slate-300 hidden sm:inline" />
            <span className="text-slate-600 font-mono text-[11px]">CrystaGraph Workstation</span>
          </div>

          {/* Quick Omnisearch Bar in Center */}
          <div className="flex-1 max-w-md hidden md:block">
            <button
              onClick={() => setIsCommandOpen(true)}
              className="w-full flex items-center justify-between px-3.5 py-1.5 text-xs text-slate-400 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-lg transition-colors shadow-2xs group"
            >
              <span className="flex items-center gap-2 truncate">
                <Search className="h-3.5 w-3.5 text-slate-400 group-hover:text-slate-600 shrink-0" />
                <span className="truncate">Search materials, papers, properties...</span>
              </span>
              <kbd className="px-1.5 py-0.5 text-[10px] font-mono bg-white border border-slate-200 rounded text-slate-500 shadow-xs shrink-0">
                ⌘K
              </kbd>
            </button>
          </div>

          {/* Top Right Quick Actions & Status */}
          <div className="flex items-center gap-2.5 shrink-0">
            {/* Live API Status Pill */}
            <ApiStatusIndicator />

            {/* Quick SI Unit Converter Button */}
            <button
              onClick={() => setIsSIModalOpen(true)}
              title="Quick SI Unit Converter (⌘U)"
              className="inline-flex items-center gap-1.5 rounded-md border border-slate-200 px-2.5 py-1.5 text-xs font-medium text-slate-700 bg-white hover:bg-slate-50 transition-colors shadow-2xs"
            >
              <Calculator className="h-3.5 w-3.5 text-sky-600" />
              <span className="hidden lg:inline">SI Tool</span>
              <kbd className="hidden xl:inline text-[9px] font-mono text-slate-400 bg-slate-100 px-1 py-0.5 rounded">
                ⌘U
              </kbd>
            </button>

            {/* Keyboard Shortcuts Button */}
            <button
              onClick={() => setIsShortcutsOpen(true)}
              title="Keyboard shortcuts (?)"
              className="p-1.5 rounded-md border border-slate-200 text-slate-500 hover:text-slate-800 hover:bg-slate-50 transition-colors"
            >
              <Keyboard className="h-3.5 w-3.5" />
            </button>

            {/* Upload Paper CTA */}
            <Link
              href="/upload"
              className="inline-flex items-center gap-1.5 rounded-md bg-slate-900 px-3 py-1.5 text-xs font-medium text-white shadow-sm hover:bg-slate-800 transition-colors"
            >
              <UploadCloud className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">Upload Paper</span>
            </Link>
          </div>
        </header>

        {/* Page Content Body */}
        <main className="flex-1 p-6 lg:p-8 overflow-y-auto">{children}</main>
      </div>

      {/* Global Modals & Command Palette */}
      <CommandPalette
        isOpen={isCommandOpen}
        onClose={() => setIsCommandOpen(false)}
        onOpenSIConverter={() => setIsSIModalOpen(true)}
      />

      <QuickSIConverterModal
        isOpen={isSIModalOpen}
        onClose={() => setIsSIModalOpen(false)}
      />

      <KeyboardShortcutsModal
        isOpen={isShortcutsOpen}
        onClose={() => setIsShortcutsOpen(false)}
      />
    </div>
  );
}
