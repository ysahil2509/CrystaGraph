"use client";

import { useState } from "react";
import {
  Bot,
  User,
  Send,
  Loader2,
  ShieldCheck,
  Table2,
  Copy,
  Check,
  Trash2,
} from "lucide-react";
import { sendChatMessage } from "@/lib/api";

interface Message {
  sender: "user" | "bot";
  text: string;
  citations?: Array<{
    paper_id: string;
    doi: string;
    table_id: string;
    material?: string;
    property?: string;
  }>;
  grounded?: boolean;
}

const PRESET_QUERIES = [
  "What is the yield strength and composition of Ti-6Al-4V?",
  "What are the dielectric and piezoelectric properties of barium titanate?",
  "What is the discharge capacity and thermal stability of NMC811 cathode?",
  "Compare tensile strength of CoCrFeNi high entropy alloys",
];

export default function AssistantPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      sender: "bot",
      text: "Hello! I am **CrystaBot**, your grounded materials informatics research copilot. Unlike general-purpose LLMs that frequently hallucinate physical constants, I formulate every response strictly using verified tables and scientific publications stored in the CrystaGraph repository. Ask me anything about material compositions, mechanical strengths, densities, or electrical properties.",
      grounded: true,
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [copiedIdx, setCopiedIdx] = useState<number | null>(null);

  const handleSend = async (queryText?: string) => {
    const textToSend = queryText || input;
    if (!textToSend.trim() || loading) return;

    const userMsg: Message = { sender: "user", text: textToSend };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await sendChatMessage(textToSend);
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: res.response,
          citations: res.citations,
          grounded: res.grounded,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: "I am temporarily unable to reach the FastAPI microservice. If you are running locally, please verify that `uvicorn app.api:app --port 8000` is active.",
          grounded: false,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleCopyText = (text: string, idx: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIdx(idx);
    setTimeout(() => setCopiedIdx(null), 2000);
  };

  const handleClear = () => {
    setMessages([
      {
        sender: "bot",
        text: "Conversation cleared. How can I assist with your materials research today?",
        grounded: true,
      },
    ]);
  };

  return (
    <div className="space-y-4 max-w-4xl mx-auto flex flex-col h-[calc(100vh-140px)]">
      {/* Header Bar */}
      <div className="flex items-center justify-between border-b border-slate-200 pb-3">
        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-900 text-sky-400">
            <Bot className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-slate-900">
              CrystaBot &bull; Grounded Academic Copilot
            </h1>
            <p className="text-[11px] text-slate-500">
              Direct table cell provenance citation &bull; Verified Materials Informatics
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 rounded-full bg-emerald-50 border border-emerald-200 px-3 py-1 text-[11px] font-semibold text-emerald-800">
            <ShieldCheck className="h-3.5 w-3.5 text-emerald-600" />
            Zero-Hallucination Grounding
          </div>
          <button
            onClick={handleClear}
            title="Clear chat"
            className="p-1.5 text-slate-400 hover:text-slate-600 rounded hover:bg-slate-100 transition-colors"
          >
            <Trash2 className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>

      {/* Preset Chips */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
        <span className="text-[10px] font-semibold uppercase text-slate-400 shrink-0">
          Suggested:
        </span>
        {PRESET_QUERIES.map((q, i) => (
          <button
            key={i}
            onClick={() => handleSend(q)}
            disabled={loading}
            className="px-2.5 py-1 rounded-full bg-white border border-slate-200 hover:border-slate-300 hover:bg-slate-50 text-slate-700 whitespace-nowrap text-[11px] transition-colors shrink-0 shadow-2xs"
          >
            {q}
          </button>
        ))}
      </div>

      {/* Message Stream */}
      <div className="flex-1 overflow-y-auto space-y-4 p-4 rounded-xl border border-slate-200 bg-white shadow-2xs">
        {messages.map((m, idx) => (
          <div
            key={idx}
            className={`flex gap-3 text-xs ${
              m.sender === "user" ? "justify-end" : "justify-start"
            }`}
          >
            {m.sender === "bot" && (
              <div className="flex h-7 w-7 items-center justify-center rounded bg-slate-900 text-sky-400 shrink-0 mt-0.5">
                <Bot className="h-4 w-4" />
              </div>
            )}

            <div
              className={`max-w-[82%] rounded-xl p-3.5 leading-relaxed space-y-2 relative group ${
                m.sender === "user"
                  ? "bg-slate-900 text-white rounded-tr-none"
                  : "bg-slate-50 border border-slate-200/80 text-slate-800 rounded-tl-none"
              }`}
            >
              {m.sender === "bot" && (
                <div className="flex items-center justify-between pb-1 text-[10px] text-slate-400 border-b border-slate-200/50">
                  <span className="font-semibold text-slate-600">CrystaBot Response</span>
                  <button
                    onClick={() => handleCopyText(m.text, idx)}
                    className="flex items-center gap-1 hover:text-slate-800 transition-colors"
                    title="Copy answer"
                  >
                    {copiedIdx === idx ? (
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
              )}

              <p className="whitespace-pre-wrap">{m.text}</p>

              {/* Citations Box */}
              {m.citations && m.citations.length > 0 && (
                <div className="pt-2 border-t border-slate-200/60 space-y-1.5">
                  <span className="text-[10px] font-mono uppercase text-slate-400 flex items-center gap-1">
                    <Table2 className="h-3 w-3" />
                    Verified Literature Evidence Provenance
                  </span>
                  <div className="flex flex-wrap gap-1.5">
                    {m.citations.map((c, cIdx) => (
                      <span
                        key={cIdx}
                        className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-white border border-slate-200 text-[10px] font-mono text-slate-700 shadow-2xs"
                      >
                        <span>{c.paper_id}</span>
                        <span className="text-slate-300">&bull;</span>
                        <span>{c.table_id}</span>
                        {c.material && (
                          <>
                            <span className="text-slate-300">&bull;</span>
                            <span className="text-sky-700 font-semibold">{c.material}</span>
                          </>
                        )}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {m.sender === "user" && (
              <div className="flex h-7 w-7 items-center justify-center rounded bg-slate-200 text-slate-700 shrink-0 mt-0.5 font-semibold text-[10px]">
                <User className="h-4 w-4" />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex gap-3 text-xs items-center text-slate-500">
            <div className="flex h-7 w-7 items-center justify-center rounded bg-slate-900 text-sky-400 shrink-0">
              <Bot className="h-4 w-4" />
            </div>
            <div className="flex items-center gap-2 bg-slate-50 border border-slate-200 rounded-xl p-3">
              <Loader2 className="h-4 w-4 animate-spin text-sky-600" />
              <span>Querying verified SQLite table records...</span>
            </div>
          </div>
        )}
      </div>

      {/* Input Composer */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="flex items-center gap-2"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a materials informatics question (e.g., 'What is the density of 45S5 bioglass?')..."
          className="flex-1 rounded-xl border border-slate-300 px-4 py-2.5 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-600 bg-white shadow-2xs"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="inline-flex items-center gap-1.5 rounded-xl bg-slate-900 px-4 py-2.5 text-xs font-semibold text-white shadow-sm hover:bg-slate-800 disabled:opacity-50 transition-colors"
        >
          <Send className="h-3.5 w-3.5" />
          Send
        </button>
      </form>
    </div>
  );
}
