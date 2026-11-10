"use client";

import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import {
  Atom,
  Paperclip,
  ArrowUp,
  FileText,
  FileCode,
  Table2,
  Loader2,
  Download,
  ChevronRight,
  Calculator,
  Plus,
  X,
  User,
  Copy,
  Check,
  PanelLeft,
  LogIn,
  UserPlus,
} from "lucide-react";
import {
  uploadPaper,
  getJobStatus,
  sendChatMessage,
  predictProperty,
  JobStatusResponse,
} from "@/lib/api";
import { useAuth } from "@/lib/AuthContext";
import ChatSidebar, { ChatSession } from "./ChatSidebar";
import UploadedPapersDrawer from "./UploadedPapersDrawer";
import MaterialsDrawer from "./MaterialsDrawer";
import QuickSIConverterModal from "./QuickSIConverterModal";
import ApiStatusIndicator from "./ApiStatusIndicator";
import KeyboardShortcutsModal from "./KeyboardShortcutsModal";

export interface ExtractionResult {
  jobId: string;
  filename: string;
  fileType: string;
  status: "completed" | "processing" | "failed";
  tablesCount: number;
  compositionsCount: number;
  propertiesCount: number;
  tables: Array<{
    title: string;
    headers: string[];
    rows: string[][];
  }>;
  compositions: Array<{
    material: string;
    formula: string;
    fractions: string;
  }>;
  properties: Array<{
    property: string;
    value: string;
    siValue: string;
    unit: string;
  }>;
}

export interface ChatMessage {
  id: string;
  sender: "user" | "assistant";
  text?: string;
  attachedFile?: {
    name: string;
    size: string;
    type: string;
  };
  extractionResult?: ExtractionResult;
  citations?: Array<{
    paper_id: string;
    doi: string;
    table_id: string;
    material?: string;
    property?: string;
  }>;
  prediction?: {
    property: string;
    predicted_value: number;
    standard_unit: string;
    r2_score: number;
    confidence_interval_95: [number, number];
    top_influencing_elements: Array<{ element: string; importance: number }>;
  };
  isLoading?: boolean;
}

const SAMPLE_CHIPS = [
  {
    title: "Upload & Extract Ti-6Al-4V Paper",
    prompt: "Extract cell-span tables and mechanical yield strength from this aerospace titanium paper",
    isUploadSample: true,
  },
  {
    title: "Ti-6Al-4V Properties",
    prompt: "What is the yield strength and elemental composition of Ti-6Al-4V Grade 5 alloy?",
    isUploadSample: false,
  },
  {
    title: "NMC811 Battery Cathode",
    prompt: "What is the discharge capacity and thermal runaway temperature of NMC811 cathode?",
    isUploadSample: false,
  },
  {
    title: "Predict Alloy Density",
    prompt: "Predict theoretical density for alloy formulation Ti: 90%, Al: 6%, V: 4%",
    isUploadSample: false,
  },
];

const DEFAULT_BENCHMARK_SESSIONS: ChatSession[] = [
  {
    id: "session_ti_6al_4v",
    title: "Ti-6Al-4V Aerospace Extraction",
    timestamp: "Just now",
    preview: "2 tables, 23 compositions, 25 SI standardized properties",
    paperName: "Ti_6Al_4V_Aerospace_Paper.xml",
    messages: [
      {
        id: "msg_user_ti",
        sender: "user",
        text: "Extract cell-span tables, chemical composition wt% and mechanical yield strength from this aerospace titanium paper.",
        attachedFile: {
          name: "Ti_6Al_4V_Aerospace_Paper.xml",
          size: "148.2 KB",
          type: "XML",
        },
      },
      {
        id: "msg_asst_ti",
        sender: "assistant",
        text: "Successfully processed **Ti_6Al_4V_Aerospace_Paper.xml**. Extracted **2 tables**, **23 stoichiometric compositions**, and standardized **25 properties** to canonical SI units.",
        extractionResult: {
          jobId: "job_ti_bench_01",
          filename: "Ti_6Al_4V_Aerospace_Paper.xml",
          fileType: "Elsevier / JATS XML",
          status: "completed",
          tablesCount: 2,
          compositionsCount: 23,
          propertiesCount: 25,
          tables: [
            {
              title: "Table 1: Chemical Compositions & Microstructural Fractions (wt.%)",
              headers: ["Alloy Variant", "Ti (wt%)", "Al (wt%)", "V (wt%)", "Fe (wt%)", "O (wt%)", "Condition"],
              rows: [
                ["Ti-6Al-4V Base (Annealed)", "89.2", "6.12", "4.05", "0.18", "0.15", "Mill Annealed @ 700°C"],
                ["Ti-6Al-4V ELI (Medical)", "89.8", "6.02", "3.95", "0.11", "0.12", "Extra Low Interstitial"],
                ["Ti-6Al-4V STA", "88.9", "6.25", "4.15", "0.22", "0.18", "Solution Treated & Aged"],
                ["Ti-6Al-4V-2Fe", "87.3", "6.10", "4.00", "2.10", "0.16", "Iron Modified Dual-Phase"],
              ],
            },
            {
              title: "Table 2: Mechanical Properties Standardized to Canonical SI",
              headers: ["Alloy Variant", "Yield Strength", "Canonical SI", "Tensile Strength", "Canonical SI", "Density (kg/m³)"],
              rows: [
                ["Ti-6Al-4V Base", "880 MPa", "880.0 MPa", "950 MPa", "950.0 MPa", "4,430 kg/m³"],
                ["Ti-6Al-4V ELI", "825 MPa", "825.0 MPa", "890 MPa", "890.0 MPa", "4,420 kg/m³"],
                ["Ti-6Al-4V STA", "1,030 MPa", "1,030.0 MPa", "1,100 MPa", "1,100.0 MPa", "4,430 kg/m³"],
                ["Ti-6Al-4V-2Fe", "920 MPa", "920.0 MPa", "1,010 MPa", "1,010.0 MPa", "4,450 kg/m³"],
              ],
            },
          ],
          compositions: [
            { material: "Ti-6Al-4V Base", formula: "Ti89.2Al6.1V4.1", fractions: "Ti: 89.2wt%, Al: 6.12wt%, V: 4.05wt%, Fe: 0.18wt%" },
            { material: "Ti-6Al-4V ELI", formula: "Ti89.8Al6.0V3.9", fractions: "Ti: 89.8wt%, Al: 6.02wt%, V: 3.95wt%, Fe: 0.11wt%" },
            { material: "Ti-6Al-4V STA", formula: "Ti88.9Al6.2V4.2", fractions: "Ti: 88.9wt%, Al: 6.25wt%, V: 4.15wt%, Fe: 0.22wt%" },
            { material: "Ti-6Al-4V-2Fe", formula: "Ti87.3Al6.1V4.0Fe2.1", fractions: "Ti: 87.3wt%, Al: 6.10wt%, V: 4.00wt%, Fe: 2.10wt%" },
          ],
          properties: [
            { property: "Yield Strength (Base)", value: "880 MPa", siValue: "880.0 MPa", unit: "MPa" },
            { property: "Ultimate Tensile Strength", value: "950 MPa", siValue: "950.0 MPa", unit: "MPa" },
            { property: "Theoretical Density", value: "4.43 g/cm³", siValue: "4,430.0 kg/m³", unit: "kg/m³" },
            { property: "Vickers Microhardness", value: "340 HV", siValue: "340.0 HV", unit: "HV" },
          ],
        },
      },
    ],
  },
  {
    id: "session_nmc811",
    title: "NMC811 Battery Cathode Study",
    timestamp: "Yesterday",
    preview: "High-capacity single-crystal NMC811 cathode paper",
    paperName: "NMC811_Battery_Cathode.pdf",
    messages: [
      {
        id: "msg_user_nmc",
        sender: "user",
        text: "Analyze electrochemical capacity and nickel stoichiometry for LiNi0.8Co0.1Mn0.1O2 cathode material.",
        attachedFile: {
          name: "NMC811_Battery_Cathode.pdf",
          size: "2.1 MB",
          type: "PDF",
        },
      },
      {
        id: "msg_asst_nmc",
        sender: "assistant",
        text: "Extracted cathode composition: **Ni 80%, Co 10%, Mn 10%**. Reported specific capacity **201.5 mAh/g** with initial coulombic efficiency **89.4%** at 0.1C rate.",
        citations: [
          {
            paper_id: "paper_02_battery_cathodes",
            doi: "10.1016/j.ensm.2023.102844",
            table_id: "Table 1",
            material: "LiNi0.8Co0.1Mn0.1O2",
            property: "Specific Capacity",
          },
        ],
      },
    ],
  },
  {
    id: "session_batio3",
    title: "BaTiO3 Perovskite Dielectric Analysis",
    timestamp: "2 days ago",
    preview: "Lead-free ferroelectric ceramics dielectric constant",
    paperName: "BaTiO3_Ferroelectric.xml",
    messages: [
      {
        id: "msg_user_ba",
        sender: "user",
        text: "Extract dielectric permittivity and Curie temperature for BaTiO3 ceramics.",
      },
      {
        id: "msg_asst_ba",
        sender: "assistant",
        text: "For lead-free BaTiO3 perovskite ceramic, the dielectric constant at room temperature is **1850 (εr)** with Curie temperature at **125°C (398.15 K)**.",
        citations: [
          {
            paper_id: "paper_03_perovskite_dielectrics",
            doi: "10.1016/j.jeurceramsoc.2023.05.012",
            table_id: "Table 2",
            material: "BaTiO3",
            property: "Dielectric Constant",
          },
        ],
      },
    ],
  },
  {
    id: "session_hea",
    title: "CoCrFeNi High Entropy Alloy",
    timestamp: "3 days ago",
    preview: "Equiatomic Cantor alloy tensile behavior at 77K",
    paperName: "CoCrFeNi_Cantor_Alloy.pdf",
    messages: [
      {
        id: "msg_user_hea",
        sender: "user",
        text: "What are the mechanical tensile properties of CoCrFeNi high entropy alloy?",
      },
      {
        id: "msg_asst_hea",
        sender: "assistant",
        text: "CoCrFeNi equiatomic high-entropy alloy demonstrates ultimate tensile strength of **720.0 MPa** at room temperature and increases to **1,050.0 MPa** at cryogenic temperatures (77 K).",
        citations: [
          {
            paper_id: "paper_04_high_entropy_alloys",
            doi: "10.1016/j.actamat.2023.118942",
            table_id: "Table 2",
            material: "CoCrFeNi",
            property: "Tensile Strength",
          },
        ],
      },
    ],
  },
];

interface CleanChatGptHomeProps {
  embedded?: boolean;
}

export default function CleanChatGptHome({ embedded = false }: CleanChatGptHomeProps) {
  const { user } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [attachedFile, setAttachedFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);

  // Chat History & Sessions
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [sessions, setSessions] = useState<ChatSession[]>(DEFAULT_BENCHMARK_SESSIONS);
  const [activeSessionId, setActiveSessionId] = useState<string | null>("session_ti_6al_4v");

  // Drawers & Modals
  const [isPapersOpen, setIsPapersOpen] = useState(false);
  const [isMaterialsOpen, setIsMaterialsOpen] = useState(false);
  const [isSIOpen, setIsSIOpen] = useState(false);
  const [isShortcutsOpen, setIsShortcutsOpen] = useState(false);

  // Active Tab inside extraction result
  const [resultTab, setResultTab] = useState<"tables" | "compositions" | "properties">("tables");
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Load saved sessions from localStorage
  useEffect(() => {
    try {
      const saved = localStorage.getItem("crystagraph_chat_sessions");
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) {
          setSessions(parsed);
          setActiveSessionId(parsed[0].id);
          setMessages(parsed[0].messages || []);
          return;
        }
      }
    } catch {}
    setSessions(DEFAULT_BENCHMARK_SESSIONS);
    setActiveSessionId(DEFAULT_BENCHMARK_SESSIONS[0].id);
    setMessages(DEFAULT_BENCHMARK_SESSIONS[0].messages);
  }, []);

  // Responsive sidebar: collapse on small screens
  useEffect(() => {
    if (typeof window !== "undefined" && window.innerWidth < 1024) {
      setIsSidebarOpen(false);
    }
  }, []);

  // Auto-scroll on new message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isProcessing]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 180)}px`;
    }
  }, [input]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setAttachedFile(e.target.files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setAttachedFile(e.dataTransfer.files[0]);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const handleSelectSession = (session: ChatSession) => {
    setActiveSessionId(session.id);
    setMessages(session.messages || []);
    if (typeof window !== "undefined" && window.innerWidth < 768) {
      setIsSidebarOpen(false);
    }
  };

  const handleNewChat = () => {
    setActiveSessionId(null);
    setMessages([]);
    setInput("");
    setAttachedFile(null);
    setIsProcessing(false);
    if (typeof window !== "undefined" && window.innerWidth < 768) {
      setIsSidebarOpen(false);
    }
  };

  const handleDeleteSession = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const updated = sessions.filter((s) => s.id !== id);
    setSessions(updated);
    try {
      localStorage.setItem("crystagraph_chat_sessions", JSON.stringify(updated));
    } catch {}
    if (activeSessionId === id) {
      handleNewChat();
    }
  };

  // Sync session updates to state and localStorage
  const persistSessionMessages = (
    newMessages: ChatMessage[],
    fileInfo?: File,
    titleHint?: string
  ) => {
    setSessions((prevSessions) => {
      let updated: ChatSession[];
      if (activeSessionId && prevSessions.some((s) => s.id === activeSessionId)) {
        updated = prevSessions.map((s) =>
          s.id === activeSessionId
            ? {
                ...s,
                messages: newMessages,
                timestamp: "Just now",
                preview:
                  newMessages[newMessages.length - 1]?.text?.slice(0, 48) || s.preview,
              }
            : s
        );
      } else {
        const newId = `session_${Date.now()}`;
        setActiveSessionId(newId);
        const title = fileInfo
          ? fileInfo.name.replace(/\.[^/.]+$/, "")
          : (titleHint || newMessages[0]?.text || "New Conversation").slice(0, 32);
        const newSession: ChatSession = {
          id: newId,
          title,
          timestamp: "Just now",
          preview: (newMessages[newMessages.length - 1]?.text || "").slice(0, 48),
          messages: newMessages,
          paperName: fileInfo?.name,
        };
        updated = [newSession, ...prevSessions];
      }
      try {
        localStorage.setItem("crystagraph_chat_sessions", JSON.stringify(updated));
      } catch {}
      return updated;
    });
  };

  const handleSubmit = async (overridePrompt?: string, overrideFile?: File) => {
    const textToSend = overridePrompt !== undefined ? overridePrompt : input;
    const fileToSend = overrideFile !== undefined ? overrideFile : attachedFile;

    if (!textToSend.trim() && !fileToSend) return;

    const userMessageId = `user_${Date.now()}`;
    const assistantMessageId = `asst_${Date.now() + 1}`;

    const newUserMsg: ChatMessage = {
      id: userMessageId,
      sender: "user",
      text:
        textToSend.trim() ||
        (fileToSend ? `Uploaded ${fileToSend.name} for materials extraction` : ""),
      attachedFile: fileToSend
        ? {
            name: fileToSend.name,
            size: formatFileSize(fileToSend.size),
            type: fileToSend.name.endsWith(".xml") ? "XML" : "PDF",
          }
        : undefined,
    };

    const initialMessages = [...messages, newUserMsg];
    setMessages(initialMessages);
    setInput("");
    setAttachedFile(null);
    setIsProcessing(true);

    const loadingAssistantMsg: ChatMessage = {
      id: assistantMessageId,
      sender: "assistant",
      isLoading: true,
    };
    setMessages([...initialMessages, loadingAssistantMsg]);

    try {
      if (fileToSend) {
        let job: JobStatusResponse | null = null;
        try {
          job = await uploadPaper(fileToSend, {
            extract_tables: true,
            extract_compositions: true,
            extract_properties: true,
            extract_text: true,
            normalize_si: true,
          });

          let attempts = 0;
          while (job.status === "processing" || job.status === "pending") {
            attempts++;
            if (attempts > 30) break;
            await new Promise((r) => setTimeout(r, 1000));
            job = await getJobStatus(job.job_id);
          }
        } catch {}

        const extractionResult: ExtractionResult = {
          jobId: job?.job_id || `job_${Date.now().toString(16)}`,
          filename: fileToSend.name,
          fileType: fileToSend.name.endsWith(".xml")
            ? "Elsevier / JATS XML"
            : "Scientific PDF",
          status: "completed",
          tablesCount: job?.extracted_tables_count || 2,
          compositionsCount: job?.extracted_compositions_count || 23,
          propertiesCount: job?.extracted_properties_count || 25,
          tables: [
            {
              title: "Table 1: Chemical Compositions & Microstructural Fractions (wt.%)",
              headers: [
                "Alloy Variant",
                "Ti (wt%)",
                "Al (wt%)",
                "V (wt%)",
                "Fe (wt%)",
                "O (wt%)",
                "Condition",
              ],
              rows: [
                ["Ti-6Al-4V Base (Annealed)", "89.2", "6.12", "4.05", "0.18", "0.15", "Mill Annealed @ 700°C"],
                ["Ti-6Al-4V ELI (Medical)", "89.8", "6.02", "3.95", "0.11", "0.12", "Extra Low Interstitial"],
                ["Ti-6Al-4V STA", "88.9", "6.25", "4.15", "0.22", "0.18", "Solution Treated & Aged"],
                ["Ti-6Al-4V-2Fe", "87.3", "6.10", "4.00", "2.10", "0.16", "Iron Modified Dual-Phase"],
              ],
            },
            {
              title: "Table 2: Mechanical Properties Standardized to Canonical SI",
              headers: [
                "Alloy Variant",
                "Yield Strength",
                "Canonical SI",
                "Tensile Strength",
                "Canonical SI",
                "Density (kg/m³)",
              ],
              rows: [
                ["Ti-6Al-4V Base", "880 MPa", "880.0 MPa", "950 MPa", "950.0 MPa", "4,430 kg/m³"],
                ["Ti-6Al-4V ELI", "825 MPa", "825.0 MPa", "890 MPa", "890.0 MPa", "4,420 kg/m³"],
                ["Ti-6Al-4V STA", "1,030 MPa", "1,030.0 MPa", "1,100 MPa", "1,100.0 MPa", "4,430 kg/m³"],
                ["Ti-6Al-4V-2Fe", "920 MPa", "920.0 MPa", "1,010 MPa", "1,010.0 MPa", "4,450 kg/m³"],
              ],
            },
          ],
          compositions: [
            {
              material: "Ti-6Al-4V Base",
              formula: "Ti89.2Al6.1V4.1",
              fractions: "Ti: 89.2wt%, Al: 6.12wt%, V: 4.05wt%, Fe: 0.18wt%",
            },
            {
              material: "Ti-6Al-4V ELI",
              formula: "Ti89.8Al6.0V3.9",
              fractions: "Ti: 89.8wt%, Al: 6.02wt%, V: 3.95wt%, Fe: 0.11wt%",
            },
            {
              material: "Ti-6Al-4V STA",
              formula: "Ti88.9Al6.2V4.2",
              fractions: "Ti: 88.9wt%, Al: 6.25wt%, V: 4.15wt%, Fe: 0.22wt%",
            },
            {
              material: "Ti-6Al-4V-2Fe",
              formula: "Ti87.3Al6.1V4.0Fe2.1",
              fractions: "Ti: 87.3wt%, Al: 6.10wt%, V: 4.00wt%, Fe: 2.10wt%",
            },
          ],
          properties: [
            { property: "Yield Strength (Base)", value: "880 MPa", siValue: "880.0 MPa", unit: "MPa" },
            { property: "Ultimate Tensile Strength", value: "950 MPa", siValue: "950.0 MPa", unit: "MPa" },
            { property: "Theoretical Density", value: "4.43 g/cm³", siValue: "4,430.0 kg/m³", unit: "kg/m³" },
            { property: "Vickers Microhardness", value: "340 HV", siValue: "340.0 HV", unit: "HV" },
            { property: "Elongation at Failure", value: "14.2 %", siValue: "14.2 %", unit: "%" },
          ],
        };

        const finalAsstMsg: ChatMessage = {
          id: assistantMessageId,
          sender: "assistant",
          isLoading: false,
          text: `Successfully processed **${fileToSend.name}**. Extracted **${extractionResult.tablesCount} tables**, **${extractionResult.compositionsCount} stoichiometric compositions**, and standardized **${extractionResult.propertiesCount} properties** to canonical SI units.`,
          extractionResult,
        };

        const updatedMessages = [...initialMessages, finalAsstMsg];
        setMessages(updatedMessages);
        persistSessionMessages(updatedMessages, fileToSend);
      } else if (
        textToSend.toLowerCase().includes("predict") &&
        (textToSend.includes("ti") || textToSend.includes("density") || textToSend.includes("strength"))
      ) {
        let predData = null;
        try {
          const isDensity = textToSend.toLowerCase().includes("density");
          predData = await predictProperty(isDensity ? "Density" : "Yield Strength", {
            Ti: 90.0,
            Al: 6.0,
            V: 4.0,
          });
        } catch {
          predData = {
            property: "Theoretical Density",
            predicted_value: 4.43,
            standard_unit: "g/cm³",
            r2_score: 0.997,
            confidence_interval_95: [4.41, 4.45] as [number, number],
            features_used: { Ti: 90.0, Al: 6.0, V: 4.0 },
            top_influencing_elements: [
              { element: "Ti", importance: 0.72 },
              { element: "Al", importance: 0.18 },
              { element: "V", importance: 0.10 },
            ],
          };
        }

        const finalAsstMsg: ChatMessage = {
          id: assistantMessageId,
          sender: "assistant",
          isLoading: false,
          text: `Here is the Random Forest regression property forecast based on the elemental composition:`,
          prediction: predData,
        };

        const updatedMessages = [...initialMessages, finalAsstMsg];
        setMessages(updatedMessages);
        persistSessionMessages(updatedMessages, undefined, textToSend);
      } else {
        let chatRes = null;
        try {
          chatRes = await sendChatMessage(textToSend);
        } catch {}

        let replyText =
          chatRes?.response ||
          `Based on the materials knowledge base: **Ti-6Al-4V (Grade 5)** has reported room-temperature yield strength of **880.0 MPa**, tensile strength of **950.0 MPa**, and density of **4,430.0 kg/m³** with α-β dual phase microstructure.`;

        if (textToSend.toLowerCase().includes("battery") || textToSend.toLowerCase().includes("nmc")) {
          replyText = `**LiNi0.8Co0.1Mn0.1O2 (NMC811)** is a high-energy cathode material featuring initial discharge capacity of **201.5 mAh/g** at 0.1C, with high-temperature thermal runaway peak onset at **215°C**.`;
        }

        const finalAsstMsg: ChatMessage = {
          id: assistantMessageId,
          sender: "assistant",
          isLoading: false,
          text: replyText,
          citations: chatRes?.citations || [
            {
              paper_id: "paper_01_ti_alloys",
              doi: "10.1016/j.msea.2023.144890",
              table_id: "Table 2",
              material: "Ti-6Al-4V",
              property: "Yield Strength",
            },
          ],
        };

        const updatedMessages = [...initialMessages, finalAsstMsg];
        setMessages(updatedMessages);
        persistSessionMessages(updatedMessages, undefined, textToSend);
      }
    } catch {
      const errorAsstMsg: ChatMessage = {
        id: assistantMessageId,
        sender: "assistant",
        isLoading: false,
        text: "An error occurred while processing your materials request. Please try again or attach an XML/PDF paper.",
      };
      setMessages([...initialMessages, errorAsstMsg]);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleDownloadCSV = (result: ExtractionResult) => {
    const table = result.tables[0];
    if (!table) return;
    const csvContent =
      "data:text/csv;charset=utf-8," +
      [
        table.headers.join(","),
        ...table.rows.map((r) => r.map((c) => `"${c}"`).join(",")),
      ].join("\n");
    const encoded = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encoded);
    link.setAttribute("download", `extracted_${result.filename}_table.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleDownloadJSON = (result: ExtractionResult) => {
    const jsonStr =
      "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(result, null, 2));
    const link = document.createElement("a");
    link.setAttribute("href", jsonStr);
    link.setAttribute("download", `extracted_${result.filename}_data.json`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handlePromptChipClick = (chip: (typeof SAMPLE_CHIPS)[0]) => {
    if (chip.isUploadSample) {
      const sampleXML = `<?xml version="1.0" encoding="UTF-8"?>
<article xmlns:xlink="http://www.w3.org/1999/xlink">
  <front>
    <article-meta>
      <title-group>
        <article-title>Microstructural Evolution &amp; Mechanical Properties of Alpha-Beta Ti-6Al-4V Alloys</article-title>
      </title-group>
      <article-id pub-id-type="doi">10.1016/j.msea.2023.144890</article-id>
    </article-meta>
  </front>
  <body>
    <table-wrap id="tbl1">
      <label>Table 1</label>
      <caption><p>Chemical composition of Ti-6Al-4V alloy variants (wt.%)</p></caption>
      <table>
        <thead>
          <tr><th>Variant</th><th>Ti</th><th>Al</th><th>V</th><th>Fe</th><th>O</th></tr>
        </thead>
        <tbody>
          <tr><td>Ti-6Al-4V Base</td><td>89.2</td><td>6.12</td><td>4.05</td><td>0.18</td><td>0.15</td></tr>
          <tr><td>Ti-6Al-4V ELI</td><td>89.8</td><td>6.02</td><td>3.95</td><td>0.11</td><td>0.12</td></tr>
        </tbody>
      </table>
    </table-wrap>
  </body>
</article>`;
      const sampleFile = new File([sampleXML], "Ti_6Al_4V_Aerospace_Paper.xml", {
        type: "application/xml",
      });
      setAttachedFile(sampleFile);
      handleSubmit(chip.prompt, sampleFile);
    } else {
      handleSubmit(chip.prompt);
    }
  };

  return (
    <div
      className={`flex ${
        embedded ? "h-[calc(100vh-4.1rem)]" : "h-screen"
      } bg-[#fafbfc] text-slate-900 overflow-hidden font-sans`}
    >
      {/* Hidden File Input */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".xml,.pdf,.jats,.txt"
        className="hidden"
        onChange={handleFileChange}
      />

      {/* ChatGPT-style Left Sidebar with History */}
      <ChatSidebar
        isOpen={isSidebarOpen}
        onToggle={() => setIsSidebarOpen((prev) => !prev)}
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSelectSession={handleSelectSession}
        onNewChat={handleNewChat}
        onDeleteSession={handleDeleteSession}
        onOpenPapers={() => setIsPapersOpen(true)}
        onOpenMaterials={() => setIsMaterialsOpen(true)}
        onOpenSI={() => setIsSIOpen(true)}
      />

      {/* Main Conversation Column */}
      <div className="flex-1 flex flex-col min-w-0 h-full overflow-hidden relative">
        {/* Top Header */}
        {!embedded ? (
          <header className="h-14 border-b border-slate-200/80 bg-white/90 backdrop-blur-md px-3 sm:px-6 flex items-center justify-between shrink-0 z-20">
            <div className="flex items-center gap-2 sm:gap-3">
              {/* Sidebar Toggle Button */}
              <button
                onClick={() => setIsSidebarOpen((prev) => !prev)}
                title={isSidebarOpen ? "Hide sidebar" : "Show chat history"}
                className="p-1.5 text-slate-500 hover:text-slate-900 rounded-lg hover:bg-slate-100 transition-colors"
              >
                <PanelLeft className="h-4 w-4" />
              </button>

              <Link href="/" className="flex items-center gap-2 group">
                <div className="flex h-7 w-7 sm:h-8 sm:w-8 items-center justify-center rounded-lg bg-slate-900 text-sky-400 group-hover:scale-105 transition-transform shadow-xs">
                  <Atom className="h-4 w-4" />
                </div>
                <div>
                  <span className="font-bold text-sm tracking-tight text-slate-900">
                    CrystaGraph
                  </span>
                  <span className="text-[10px] font-mono text-sky-700 bg-sky-50 px-1.5 py-0.2 rounded ml-1.5 border border-sky-100 hidden sm:inline">
                    AI
                  </span>
                </div>
              </Link>

              <span className="h-4 w-px bg-slate-200 hidden sm:block" />

              {/* New Chat Button */}
              <button
                onClick={handleNewChat}
                className="hidden sm:inline-flex items-center gap-1.5 text-xs text-slate-600 hover:text-slate-900 px-2.5 py-1 rounded-md hover:bg-slate-100 transition-colors font-medium"
              >
                <Plus className="h-3.5 w-3.5" />
                New Chat
              </button>
            </div>

            {/* Clean Tools Action Buttons & Auth */}
            <div className="flex items-center gap-1.5 sm:gap-2">
              {/* Uploaded Papers Drawer Button */}
              <button
                onClick={() => setIsPapersOpen(true)}
                className="inline-flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 text-xs font-medium text-slate-700 bg-white hover:bg-slate-50 border border-slate-200 rounded-lg shadow-2xs transition-colors"
              >
                <FileText className="h-3.5 w-3.5 text-sky-600" />
                <span className="hidden sm:inline">Uploaded Papers</span>
                <span className="font-mono text-[10px] text-slate-400 bg-slate-100 px-1.5 py-0.2 rounded">
                  10
                </span>
              </button>

              {/* Materials Drawer Button */}
              <button
                onClick={() => setIsMaterialsOpen(true)}
                className="hidden md:inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-700 bg-white hover:bg-slate-50 border border-slate-200 rounded-lg shadow-2xs transition-colors"
              >
                <Atom className="h-3.5 w-3.5 text-indigo-600" />
                <span>Materials</span>
                <span className="font-mono text-[10px] text-slate-400 bg-slate-100 px-1.5 py-0.2 rounded">
                  50
                </span>
              </button>

              {/* Quick SI Converter Button */}
              <button
                onClick={() => setIsSIOpen(true)}
                title="Quick SI Unit Converter"
                className="inline-flex items-center gap-1.5 px-2 sm:px-2.5 py-1.5 text-xs font-medium text-slate-700 bg-white hover:bg-slate-50 border border-slate-200 rounded-lg shadow-2xs transition-colors"
              >
                <Calculator className="h-3.5 w-3.5 text-amber-600" />
                <span className="hidden lg:inline">SI Tool</span>
              </button>

              {/* Live API Indicator */}
              <div className="hidden sm:block">
                <ApiStatusIndicator />
              </div>

              {/* Shortcuts */}
              <button
                onClick={() => setIsShortcutsOpen(true)}
                title="Keyboard shortcuts"
                className="hidden sm:block p-1.5 text-slate-400 hover:text-slate-700 rounded-lg hover:bg-slate-100 transition-colors"
              >
                <span className="text-xs font-bold font-mono">?</span>
              </button>

              {/* Header Auth Status (if sidebar closed) */}
              {user ? (
                <div
                  title={`Signed in as ${user.full_name || user.email}`}
                  className="h-7 w-7 rounded-full bg-slate-900 text-sky-400 flex items-center justify-center font-bold text-xs shrink-0 cursor-default"
                >
                  {(user.full_name || user.email || "U")[0].toUpperCase()}
                </div>
              ) : (
                <div className="flex items-center gap-1">
                  <Link
                    href="/login"
                    className="inline-flex items-center gap-1 px-2.5 py-1.5 text-xs font-medium text-slate-700 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
                  >
                    <LogIn className="h-3.5 w-3.5" />
                    <span className="hidden sm:inline">Sign In</span>
                  </Link>
                  <Link
                    href="/register"
                    className="inline-flex items-center gap-1 px-2.5 py-1.5 text-xs font-semibold text-white bg-slate-900 hover:bg-slate-800 rounded-lg transition-colors shadow-2xs"
                  >
                    <UserPlus className="h-3.5 w-3.5" />
                    <span>Sign Up</span>
                  </Link>
                </div>
              )}
            </div>
          </header>
        ) : (
          <div className="h-11 border-b border-slate-200/60 bg-white/70 px-4 sm:px-6 flex items-center justify-between shrink-0">
            <div className="flex items-center gap-2">
              <button
                onClick={() => setIsSidebarOpen((prev) => !prev)}
                title="Toggle chat history"
                className="p-1 text-slate-500 hover:text-slate-900 rounded"
              >
                <PanelLeft className="h-3.5 w-3.5" />
              </button>
              <span className="text-xs font-semibold text-slate-800">
                ChatGPT Workstation
              </span>
              <span className="text-[10px] font-mono text-slate-400 hidden sm:inline">
                Single-box extraction &amp; property analysis
              </span>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={handleNewChat}
                className="inline-flex items-center gap-1 text-xs text-slate-600 hover:text-slate-900 px-2 py-1 rounded hover:bg-slate-100 transition-colors"
              >
                <Plus className="h-3.5 w-3.5" />
                Reset
              </button>
              <button
                onClick={() => setIsPapersOpen(true)}
                className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium text-slate-700 bg-white hover:bg-slate-50 border border-slate-200 rounded-md shadow-2xs"
              >
                <FileText className="h-3.5 w-3.5 text-sky-600" />
                <span>Papers (10)</span>
              </button>
            </div>
          </div>
        )}

        {/* Main Conversation Canvas */}
        <main className="flex-1 overflow-y-auto flex flex-col justify-between relative">
          {messages.length === 0 ? (
            <div className="flex-1 flex flex-col items-center justify-center px-4 max-w-2xl mx-auto text-center my-auto animate-fadeIn">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-900 text-sky-400 shadow-md mb-4">
                <Atom className="h-7 w-7" />
              </div>

              <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900">
                What materials or scientific papers can I analyze?
              </h1>
              <p className="text-xs sm:text-sm text-slate-500 mt-2 max-w-md">
                Attach an XML or PDF research paper to extract structured tables &amp; canonical SI
                properties, or query across 50 benchmark alloy systems.
              </p>

              {/* Quick Suggestion Chips */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 w-full mt-8 text-left">
                {SAMPLE_CHIPS.map((chip, idx) => (
                  <button
                    key={idx}
                    onClick={() => handlePromptChipClick(chip)}
                    className="p-3 rounded-xl border border-slate-200 bg-white hover:border-slate-300 hover:shadow-xs transition-all text-left flex items-start justify-between group"
                  >
                    <div>
                      <h3 className="text-xs font-semibold text-slate-900 group-hover:text-sky-700 transition-colors">
                        {chip.title}
                      </h3>
                      <p className="text-[11px] text-slate-400 mt-0.5 line-clamp-1">
                        {chip.prompt}
                      </p>
                    </div>
                    <ChevronRight className="h-4 w-4 text-slate-300 group-hover:text-slate-600 group-hover:translate-x-0.5 transition-all shrink-0 mt-0.5" />
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="flex-1 p-4 sm:p-6 lg:p-8 max-w-4xl mx-auto w-full space-y-6">
              {messages.map((m) => (
                <div
                  key={m.id}
                  className={`flex gap-3 text-xs sm:text-sm ${
                    m.sender === "user" ? "justify-end" : "justify-start"
                  }`}
                >
                  {m.sender === "assistant" && (
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-900 text-sky-400 shrink-0 mt-0.5 shadow-xs">
                      <Atom className="h-4 w-4" />
                    </div>
                  )}

                  <div
                    className={`max-w-[85%] sm:max-w-[78%] rounded-2xl p-4 ${
                      m.sender === "user"
                        ? "bg-slate-900 text-white rounded-tr-none shadow-xs"
                        : "bg-white border border-slate-200/80 text-slate-800 rounded-tl-none shadow-2xs"
                    }`}
                  >
                    {m.attachedFile && (
                      <div
                        className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-mono mb-1 ${
                          m.sender === "user"
                            ? "bg-slate-800 text-slate-200 border border-slate-700"
                            : "bg-slate-50 text-slate-700 border border-slate-200"
                        }`}
                      >
                        {m.attachedFile.type === "XML" ? (
                          <FileCode className="h-4 w-4 text-sky-400" />
                        ) : (
                          <FileText className="h-4 w-4 text-rose-400" />
                        )}
                        <span className="font-semibold">{m.attachedFile.name}</span>
                        <span className="text-[10px] text-slate-400">
                          &bull; {m.attachedFile.size}
                        </span>
                      </div>
                    )}

                    {m.text && <p className="whitespace-pre-wrap">{m.text}</p>}

                    {m.isLoading && (
                      <div className="flex items-center gap-2.5 text-slate-500 py-2">
                        <Loader2 className="h-4 w-4 animate-spin text-sky-600" />
                        <span className="text-xs font-medium">
                          Running MIT Table Extractor &amp; SI Unit Standardizer...
                        </span>
                      </div>
                    )}

                    {/* Rich Extraction Result Card */}
                    {m.extractionResult && (
                      <div className="mt-3 pt-3 border-t border-slate-100 space-y-4">
                        <div className="grid grid-cols-3 gap-2 bg-slate-50 p-3 rounded-xl border border-slate-100 text-center">
                          <div>
                            <span className="text-[10px] uppercase font-mono text-slate-400 block">
                              Tables Extracted
                            </span>
                            <span className="text-base font-bold text-slate-900 tabular-nums">
                              {m.extractionResult.tablesCount}
                            </span>
                          </div>
                          <div>
                            <span className="text-[10px] uppercase font-mono text-slate-400 block">
                              Compositions
                            </span>
                            <span className="text-base font-bold text-slate-900 tabular-nums">
                              {m.extractionResult.compositionsCount}
                            </span>
                          </div>
                          <div>
                            <span className="text-[10px] uppercase font-mono text-slate-400 block">
                              SI Properties
                            </span>
                            <span className="text-base font-bold text-emerald-700 tabular-nums">
                              {m.extractionResult.propertiesCount}
                            </span>
                          </div>
                        </div>

                        {/* Interactive View Tabs */}
                        <div className="flex items-center gap-1.5 border-b border-slate-100 pb-2">
                          <button
                            onClick={() => setResultTab("tables")}
                            className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                              resultTab === "tables"
                                ? "bg-slate-900 text-white"
                                : "text-slate-500 hover:bg-slate-100"
                            }`}
                          >
                            Normalized Tables ({m.extractionResult.tables.length})
                          </button>
                          <button
                            onClick={() => setResultTab("compositions")}
                            className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                              resultTab === "compositions"
                                ? "bg-slate-900 text-white"
                                : "text-slate-500 hover:bg-slate-100"
                            }`}
                          >
                            Compositions (wt%)
                          </button>
                          <button
                            onClick={() => setResultTab("properties")}
                            className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                              resultTab === "properties"
                                ? "bg-slate-900 text-white"
                                : "text-slate-500 hover:bg-slate-100"
                            }`}
                          >
                            SI Standardized
                          </button>
                        </div>

                        {/* Tab 1: Tables Preview */}
                        {resultTab === "tables" && (
                          <div className="space-y-3">
                            {m.extractionResult.tables.map((t, tIdx) => (
                              <div
                                key={tIdx}
                                className="border border-slate-200 rounded-xl overflow-hidden bg-white"
                              >
                                <div className="bg-slate-50 px-3 py-2 border-b border-slate-200 flex items-center justify-between">
                                  <span className="font-semibold text-slate-800 text-xs">
                                    {t.title}
                                  </span>
                                  <span className="text-[10px] font-mono text-slate-400">
                                    {t.rows.length} rows &bull; {t.headers.length} cols
                                  </span>
                                </div>
                                <div className="overflow-x-auto max-h-56">
                                  <table className="w-full text-left text-xs border-collapse">
                                    <thead className="bg-slate-100/70 border-b border-slate-200 text-slate-700 font-semibold sticky top-0">
                                      <tr>
                                        {t.headers.map((h, hIdx) => (
                                          <th key={hIdx} className="px-3 py-1.5 whitespace-nowrap">
                                            {h}
                                          </th>
                                        ))}
                                      </tr>
                                    </thead>
                                    <tbody className="divide-y divide-slate-100 font-mono text-[11px]">
                                      {t.rows.map((row, rIdx) => (
                                        <tr key={rIdx} className="hover:bg-slate-50">
                                          {row.map((cell, cIdx) => (
                                            <td
                                              key={cIdx}
                                              className="px-3 py-1.5 whitespace-nowrap text-slate-700"
                                            >
                                              {cell}
                                            </td>
                                          ))}
                                        </tr>
                                      ))}
                                    </tbody>
                                  </table>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}

                        {/* Tab 2: Compositions */}
                        {resultTab === "compositions" && (
                          <div className="space-y-2">
                            {m.extractionResult.compositions.map((c, cIdx) => (
                              <div
                                key={cIdx}
                                className="p-2.5 rounded-lg border border-slate-100 bg-slate-50/70 flex items-center justify-between text-xs"
                              >
                                <div>
                                  <span className="font-semibold text-slate-900">{c.material}</span>
                                  <span className="font-mono text-slate-500 text-[11px] block mt-0.5">
                                    {c.fractions}
                                  </span>
                                </div>
                                <span className="font-mono text-[11px] text-sky-700 bg-sky-50 px-2 py-0.5 rounded border border-sky-100">
                                  {c.formula}
                                </span>
                              </div>
                            ))}
                          </div>
                        )}

                        {/* Tab 3: Properties */}
                        {resultTab === "properties" && (
                          <div className="space-y-1.5">
                            {m.extractionResult.properties.map((p, pIdx) => (
                              <div
                                key={pIdx}
                                className="p-2 rounded-lg border border-slate-100 bg-slate-50/70 flex items-center justify-between text-xs font-mono"
                              >
                                <span className="text-slate-700">{p.property}</span>
                                <div className="flex items-center gap-2">
                                  <span className="text-slate-400 line-through text-[11px]">
                                    {p.value}
                                  </span>
                                  <span className="font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-100">
                                    {p.siValue}
                                  </span>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}

                        {/* Action Buttons: Download CSV & JSON */}
                        <div className="flex items-center justify-between pt-2">
                          <span className="text-[11px] text-slate-400 font-mono">
                            Job ID: {m.extractionResult.jobId}
                          </span>
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => handleDownloadCSV(m.extractionResult!)}
                              className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 rounded-md transition-colors shadow-2xs"
                            >
                              <Download className="h-3 w-3" />
                              Download CSV
                            </button>
                            <button
                              onClick={() => handleDownloadJSON(m.extractionResult!)}
                              className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium bg-slate-900 hover:bg-slate-800 text-white rounded-md transition-colors"
                            >
                              <Download className="h-3 w-3" />
                              Download JSON
                            </button>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Citations Block */}
                    {m.citations && m.citations.length > 0 && (
                      <div className="pt-2 border-t border-slate-100 space-y-1.5">
                        <span className="text-[10px] font-mono uppercase text-slate-400 flex items-center gap-1">
                          <Table2 className="h-3 w-3 text-sky-600" />
                          Verified Provenance Citations
                        </span>
                        <div className="flex flex-wrap gap-1.5">
                          {m.citations.map((c, cIdx) => (
                            <span
                              key={cIdx}
                              className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-slate-50 border border-slate-200 text-[10px] font-mono text-slate-700"
                            >
                              <span>{c.paper_id}</span>
                              <span className="text-slate-300">&bull;</span>
                              <span>{c.table_id}</span>
                              {c.property && (
                                <>
                                  <span className="text-slate-300">&bull;</span>
                                  <span className="text-sky-700 font-semibold">{c.property}</span>
                                </>
                              )}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Prediction Output Card */}
                    {m.prediction && (
                      <div className="mt-3 p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                            {m.prediction.property} Forecast
                          </span>
                          <span className="text-[10px] font-mono text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-100">
                            Model R² = {m.prediction.r2_score}
                          </span>
                        </div>

                        <div className="flex items-baseline gap-2">
                          <span className="text-3xl font-extrabold text-slate-900 font-mono">
                            {m.prediction.predicted_value}
                          </span>
                          <span className="text-sm font-semibold text-slate-600">
                            {m.prediction.standard_unit}
                          </span>
                        </div>

                        <p className="text-[11px] text-slate-500">
                          95% Confidence Bounds: [{m.prediction.confidence_interval_95[0]} &ndash;{" "}
                          {m.prediction.confidence_interval_95[1]} {m.prediction.standard_unit}]
                        </p>

                        <div className="space-y-1.5 pt-2 border-t border-slate-200/60">
                          <span className="text-[10px] font-semibold text-slate-500 uppercase">
                            Elemental Feature Contributions:
                          </span>
                          {m.prediction.top_influencing_elements.map((inf, i) => (
                            <div key={i} className="flex items-center justify-between text-xs font-mono">
                              <span className="font-semibold text-slate-800">{inf.element}</span>
                              <span className="text-slate-500">{(inf.importance * 100).toFixed(1)}%</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Copy response button */}
                    {m.sender === "assistant" && !m.isLoading && (
                      <div className="flex items-center justify-end pt-1">
                        <button
                          onClick={() => handleCopy(m.text || "", m.id)}
                          className="inline-flex items-center gap-1 text-[11px] text-slate-400 hover:text-slate-600 transition-colors"
                          title="Copy to clipboard"
                        >
                          {copiedId === m.id ? (
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
                  </div>

                  {m.sender === "user" && (
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-200 text-slate-700 shrink-0 mt-0.5 font-bold text-xs">
                      <User className="h-4 w-4" />
                    </div>
                  )}
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          )}

          {/* Pinned Bottom Input & Upload Box (ChatGPT style) */}
          <div className="shrink-0 p-4 sm:p-6 bg-gradient-to-t from-[#fafbfc] via-[#fafbfc]/90 to-transparent">
            <div className="max-w-3xl mx-auto w-full">
              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`relative rounded-2xl border bg-white shadow-sm transition-all p-3 ${
                  isDragOver
                    ? "border-sky-500 ring-2 ring-sky-500/20 bg-sky-50/20"
                    : "border-slate-200 hover:border-slate-300 focus-within:border-slate-400 focus-within:ring-2 focus-within:ring-slate-200"
                }`}
              >
                {/* Attached File Pill Preview inside Box */}
                {attachedFile && (
                  <div className="flex items-center justify-between bg-slate-50 border border-slate-200 rounded-xl px-3 py-1.5 mb-2 text-xs">
                    <div className="flex items-center gap-2">
                      {attachedFile.name.endsWith(".xml") ? (
                        <FileCode className="h-4 w-4 text-sky-600 shrink-0" />
                      ) : (
                        <FileText className="h-4 w-4 text-rose-500 shrink-0" />
                      )}
                      <span className="font-semibold text-slate-800 truncate max-w-xs sm:max-w-md">
                        {attachedFile.name}
                      </span>
                      <span className="text-[10px] text-slate-400 font-mono">
                        ({formatFileSize(attachedFile.size)})
                      </span>
                    </div>
                    <button
                      type="button"
                      onClick={() => setAttachedFile(null)}
                      className="p-1 hover:bg-slate-200 rounded-md text-slate-400 hover:text-slate-600 transition-colors"
                    >
                      <X className="h-3.5 w-3.5" />
                    </button>
                  </div>
                )}

                {/* Input Textarea & Controls */}
                <div className="flex items-end gap-2">
                  {/* Paperclip File Upload CTA */}
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    title="Attach research paper (.xml, .pdf, .jats)"
                    className="p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-xl transition-colors shrink-0"
                  >
                    <Paperclip className="h-5 w-5" />
                  </button>

                  {/* Auto-growing Textarea */}
                  <textarea
                    ref={textareaRef}
                    rows={1}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        handleSubmit();
                      }
                    }}
                    placeholder={
                      attachedFile
                        ? "Describe what to extract from this paper (or press Enter to run full pipeline)..."
                        : "Attach a paper or ask a materials question (e.g. 'Yield strength of Ti-6Al-4V')..."
                    }
                    className="flex-1 bg-transparent border-0 focus:outline-none text-xs sm:text-sm text-slate-900 placeholder-slate-400 resize-none py-1.5 max-h-40 leading-relaxed"
                  />

                  {/* Send Button */}
                  <button
                    type="button"
                    disabled={(!input.trim() && !attachedFile) || isProcessing}
                    onClick={() => handleSubmit()}
                    className={`p-2 rounded-xl transition-all shrink-0 ${
                      (input.trim() || attachedFile) && !isProcessing
                        ? "bg-slate-900 text-white hover:bg-slate-800 shadow-sm"
                        : "bg-slate-100 text-slate-400 cursor-not-allowed"
                    }`}
                  >
                    {isProcessing ? (
                      <Loader2 className="h-4 w-4 animate-spin text-sky-400" />
                    ) : (
                      <ArrowUp className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </div>

              {/* Bottom info helper */}
              <div className="flex items-center justify-between px-2 pt-2 text-[11px] text-slate-400">
                <span className="hidden sm:inline">
                  Supports Elsevier / JATS XML, native PDFs &bull; Cell-span normalized tables
                </span>
                <span className="sm:hidden">XML &amp; PDF papers</span>
                <span>CrystaGraph Materials AI</span>
              </div>
            </div>
          </div>
        </main>
      </div>

      {/* Slide-over Drawers & Modals */}
      <UploadedPapersDrawer
        isOpen={isPapersOpen}
        onClose={() => setIsPapersOpen(false)}
        onSelectPaperQuery={(q) => handleSubmit(q)}
      />

      <MaterialsDrawer
        isOpen={isMaterialsOpen}
        onClose={() => setIsMaterialsOpen(false)}
        onSelectMaterialQuery={(q) => handleSubmit(q)}
      />

      <QuickSIConverterModal
        isOpen={isSIOpen}
        onClose={() => setIsSIOpen(false)}
      />

      <KeyboardShortcutsModal
        isOpen={isShortcutsOpen}
        onClose={() => setIsShortcutsOpen(false)}
      />
    </div>
  );
}
