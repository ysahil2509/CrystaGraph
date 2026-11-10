"use client";

import { useState } from "react";
import Link from "next/link";
import {
  MessageSquare,
  Plus,
  Trash2,
  FileText,
  Atom,
  Calculator,
  LogOut,
  LogIn,
  UserPlus,
  PanelLeftClose,
  Search,
  Sparkles,
} from "lucide-react";
import { useAuth } from "@/lib/AuthContext";
import { ChatMessage } from "./CleanChatGptHome";

export interface ChatSession {
  id: string;
  title: string;
  timestamp: string;
  preview: string;
  messages: ChatMessage[];
  paperName?: string;
}

interface ChatSidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  sessions: ChatSession[];
  activeSessionId: string | null;
  onSelectSession: (session: ChatSession) => void;
  onNewChat: () => void;
  onDeleteSession: (id: string, e: React.MouseEvent) => void;
  onOpenPapers: () => void;
  onOpenMaterials: () => void;
  onOpenSI: () => void;
}

export default function ChatSidebar({
  isOpen,
  onToggle,
  sessions,
  activeSessionId,
  onSelectSession,
  onNewChat,
  onDeleteSession,
  onOpenPapers,
  onOpenMaterials,
  onOpenSI,
}: ChatSidebarProps) {
  const { user, logout } = useAuth();
  const [searchQuery, setSearchQuery] = useState("");

  const filteredSessions = sessions.filter(
    (s) =>
      s.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.preview.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (s.paperName && s.paperName.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const getInitials = (name?: string) => {
    if (!name) return "U";
    const parts = name.split(" ").filter(Boolean);
    if (parts.length >= 2) return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
    return name.slice(0, 2).toUpperCase();
  };

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          onClick={onToggle}
          className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs z-40 md:hidden animate-fadeIn"
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed md:static inset-y-0 left-0 z-40 w-72 bg-[#171717] text-slate-200 flex flex-col justify-between transition-all duration-200 ease-in-out border-r border-[#262626] font-sans ${
          isOpen ? "translate-x-0" : "-translate-x-full md:hidden"
        }`}
      >
        {/* Top Header & New Chat Button */}
        <div className="p-3 border-b border-[#262626] space-y-2.5">
          <div className="flex items-center justify-between px-1">
            <Link href="/" className="flex items-center gap-2 group">
              <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-sky-500 text-slate-950 font-bold shadow-xs">
                <Atom className="h-4 w-4" />
              </div>
              <span className="font-bold text-sm tracking-tight text-white group-hover:text-sky-300 transition-colors">
                CrystaGraph
              </span>
              <span className="text-[10px] font-mono text-sky-400 bg-sky-950/80 px-1.5 py-0.2 rounded border border-sky-800/60">
                v2.0
              </span>
            </Link>

            <button
              onClick={onToggle}
              title="Close sidebar"
              className="p-1 text-slate-400 hover:text-white rounded-md hover:bg-[#262626] transition-colors"
            >
              <PanelLeftClose className="h-4 w-4" />
            </button>
          </div>

          {/* New Chat Button */}
          <button
            onClick={onNewChat}
            className="w-full flex items-center justify-between px-3 py-2 text-xs font-semibold text-white bg-[#262626] hover:bg-[#303030] border border-[#383838] rounded-xl transition-all group shadow-2xs"
          >
            <span className="flex items-center gap-2">
              <Plus className="h-3.5 w-3.5 text-sky-400 group-hover:scale-110 transition-transform" />
              <span>New Paper Chat</span>
            </span>
            <kbd className="text-[10px] font-mono text-slate-400 bg-[#1e1e1e] px-1.5 py-0.5 rounded border border-[#333]">
              +
            </kbd>
          </button>

          {/* Quick Search Sessions */}
          <div className="relative">
            <Search className="h-3.5 w-3.5 text-slate-500 absolute left-2.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search chat history..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-8 pr-2.5 py-1.5 text-xs bg-[#212121] border border-[#303030] rounded-lg text-slate-200 placeholder-slate-500 focus:outline-none focus:border-sky-500/80 transition-colors"
            />
          </div>
        </div>

        {/* Scrollable Center: Chat History & Uploaded Paper Sessions */}
        <div className="flex-1 overflow-y-auto px-2 py-3 space-y-4">
          {/* Recent History Group */}
          <div>
            <div className="flex items-center justify-between px-2 mb-1.5 text-[10px] font-semibold uppercase tracking-wider text-slate-400">
              <span className="flex items-center gap-1.5">
                <Sparkles className="h-3 w-3 text-sky-400" />
                Previous Chats &amp; Papers
              </span>
              <span className="font-mono text-slate-400 text-[10px]">
                {filteredSessions.length}
              </span>
            </div>

            {filteredSessions.length === 0 ? (
              <p className="px-3 py-4 text-xs text-slate-500 text-center">
                No matching conversations found.
              </p>
            ) : (
              <div className="space-y-1">
                {filteredSessions.map((session) => {
                  const isActive = activeSessionId === session.id;
                  return (
                    <div
                      key={session.id}
                      onClick={() => onSelectSession(session)}
                      className={`group relative flex items-center justify-between px-2.5 py-2 rounded-xl text-xs cursor-pointer transition-all ${
                        isActive
                          ? "bg-[#2a2a2a] text-white font-medium border border-[#3a3a3a]"
                          : "text-slate-300 hover:bg-[#212121] hover:text-white"
                      }`}
                    >
                      <div className="flex items-center gap-2.5 min-w-0 flex-1 pr-2">
                        <MessageSquare
                          className={`h-3.5 w-3.5 shrink-0 ${
                            isActive ? "text-sky-400" : "text-slate-500 group-hover:text-slate-300"
                          }`}
                        />
                        <div className="min-w-0 flex-1">
                          <p className="truncate leading-tight text-xs">{session.title}</p>
                          <p className="text-[10px] text-slate-500 truncate mt-0.5">
                            {session.timestamp} &bull; {session.preview}
                          </p>
                        </div>
                      </div>

                      {/* Delete Session Button */}
                      <button
                        onClick={(e) => onDeleteSession(session.id, e)}
                        title="Delete chat"
                        className="opacity-0 group-hover:opacity-100 p-1 hover:text-rose-400 transition-opacity"
                      >
                        <Trash2 className="h-3 w-3" />
                      </button>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Quick Tools & Drawers Section */}
          <div className="pt-2 border-t border-[#262626] space-y-1">
            <span className="px-2 text-[10px] font-semibold uppercase tracking-wider text-slate-500 block mb-1">
              Scientific Tools
            </span>

            {/* Uploaded Papers Library Trigger */}
            <button
              onClick={onOpenPapers}
              className="w-full flex items-center justify-between px-2.5 py-2 text-xs text-slate-300 hover:text-white hover:bg-[#212121] rounded-xl transition-colors group"
            >
              <span className="flex items-center gap-2">
                <FileText className="h-3.5 w-3.5 text-sky-400" />
                <span>Uploaded Papers</span>
              </span>
              <span className="font-mono text-[10px] text-slate-400 bg-[#262626] px-1.5 py-0.5 rounded">
                10
              </span>
            </button>

            {/* Materials Database Trigger */}
            <button
              onClick={onOpenMaterials}
              className="w-full flex items-center justify-between px-2.5 py-2 text-xs text-slate-300 hover:text-white hover:bg-[#212121] rounded-xl transition-colors group"
            >
              <span className="flex items-center gap-2">
                <Atom className="h-3.5 w-3.5 text-indigo-400" />
                <span>Materials Explorer</span>
              </span>
              <span className="font-mono text-[10px] text-slate-400 bg-[#262626] px-1.5 py-0.5 rounded">
                50
              </span>
            </button>

            {/* Quick SI Unit Tool */}
            <button
              onClick={onOpenSI}
              className="w-full flex items-center justify-between px-2.5 py-2 text-xs text-slate-300 hover:text-white hover:bg-[#212121] rounded-xl transition-colors group"
            >
              <span className="flex items-center gap-2">
                <Calculator className="h-3.5 w-3.5 text-amber-400" />
                <span>SI Unit Converter</span>
              </span>
              <span className="text-[10px] font-mono text-slate-400">32 props</span>
            </button>
          </div>
        </div>

        {/* Bottom Profile & Authentication Bar */}
        <div className="p-3 border-t border-[#262626] bg-[#1a1a1a]">
          {user ? (
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5 min-w-0">
                <div className="h-8 w-8 rounded-full bg-sky-500 text-slate-950 flex items-center justify-center font-bold text-xs shrink-0 shadow-xs">
                  {getInitials(user.full_name)}
                </div>
                <div className="min-w-0 truncate">
                  <p className="text-xs font-semibold text-white truncate">
                    {user.full_name || "Academic Researcher"}
                  </p>
                  <p className="text-[10px] text-slate-400 truncate">
                    {user.email || "researcher@university.edu"}
                  </p>
                </div>
              </div>

              <button
                onClick={logout}
                title="Sign out"
                className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-[#262626] rounded-lg transition-colors ml-1 shrink-0"
              >
                <LogOut className="h-4 w-4" />
              </button>
            </div>
          ) : (
            <div className="space-y-1.5">
              <div className="flex items-center gap-2">
                <Link
                  href="/login"
                  className="flex-1 flex items-center justify-center gap-1.5 py-1.5 px-3 rounded-lg text-xs font-medium text-white bg-[#262626] hover:bg-[#333] border border-[#383838] transition-colors"
                >
                  <LogIn className="h-3.5 w-3.5 text-slate-400" />
                  <span>Log in</span>
                </Link>
                <Link
                  href="/register"
                  className="flex-1 flex items-center justify-center gap-1.5 py-1.5 px-3 rounded-lg text-xs font-semibold text-slate-950 bg-sky-400 hover:bg-sky-300 transition-colors shadow-xs"
                >
                  <UserPlus className="h-3.5 w-3.5" />
                  <span>Sign up</span>
                </Link>
              </div>
              <p className="text-[10px] text-slate-400 text-center">
                Sign in to save and sync your paper extractions
              </p>
            </div>
          )}
        </div>
      </aside>
    </>
  );
}
