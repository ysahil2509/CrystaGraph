import Link from "next/link";
import {
  Atom,
  ArrowRight,
} from "lucide-react";

const SAMPLE_EXTRACTIONS = [
  {
    material: "Ti-6Al-4V (Grade 5)",
    composition: "Ti: 90.0%, Al: 6.0%, V: 4.0%",
    property: "Yield Strength",
    reported: "880 MPa",
    siValue: "880.0 MPa",
    source: "10.1016/j.msea.2023.144890",
    paper: "Microstructural evolution of α-β titanium alloys",
  },
  {
    material: "LiNi0.8Co0.1Mn0.1O2",
    composition: "Ni: 80%, Co: 10%, Mn: 10%",
    property: "Specific Capacity",
    reported: "201.5 mAh/g",
    siValue: "201.5 mAh/g",
    source: "10.1016/j.ensm.2023.102844",
    paper: "High-capacity single-crystal NMC811 cathodes",
  },
  {
    material: "BaTiO3 Perovskite",
    composition: "BaO: 50.0%, TiO2: 50.0%",
    property: "Dielectric Constant",
    reported: "1850",
    siValue: "1850 (εr)",
    source: "10.1016/j.jeurceramsoc.2023.05.012",
    paper: "Lead-free ferroelectric BaTiO3 ceramics",
  },
  {
    material: "CoCrFeNi Cantor Alloy",
    composition: "Co: 25%, Cr: 25%, Fe: 25%, Ni: 25%",
    property: "Tensile Strength",
    reported: "720 MPa",
    siValue: "720.0 MPa",
    source: "10.1016/j.actamat.2023.118942",
    paper: "Cryogenic mechanical behavior of Cantor HEAs",
  },
  {
    material: "45S5 Bioglass",
    composition: "SiO2: 45%, Na2O: 24.5%, CaO: 24.5%, P2O5: 6%",
    property: "Density",
    reported: "2.70 g/cm³",
    siValue: "2,700.0 kg/m³",
    source: "10.1016/j.jnoncrysol.2023.122119",
    paper: "Bioactive silicate glass crystallization kinetics",
  },
];

const METHODOLOGY_STAGES = [
  {
    step: "01",
    title: "Document Ingestion",
    description:
      "Ingests scientific literature in Elsevier/JATS XML and native PDF formats, extracting article metadata, DOIs, abstracts, and table sections.",
  },
  {
    step: "02",
    title: "Table Geometry Parsing",
    description:
      "Resolves complex multi-row headers, spanning cells (morerows, namest, nameend), captions, and footnotes without corrupting chemical notation.",
  },
  {
    step: "03",
    title: "Stoichiometry & Composition Mining",
    description:
      "Extracts elemental fractions, ceramic oxide formulas, and mass/atomic percentages (wt.%, at.%, mol%) with strict boundary validation.",
  },
  {
    step: "04",
    title: "Property Extraction & SI Standardization",
    description:
      "Identifies 32 canonical physical properties and converts reported units (g/cm³, °C, S/cm) into standard SI units (kg/m³, K, S/m, MPa, GPa).",
  },
  {
    step: "05",
    title: "Relational Knowledge Linking",
    description:
      "Associates compositions in Table 1 with experimental measurements in Table 2, constructing a structured, queryable SQLite knowledge base.",
  },
];

const BOT_VS_CRYSTAGRAPH = [
  {
    feature: "Numerical Integrity",
    llm: "Prone to hallucination; invented decimals or percentage sums drifting from 100%.",
    crystagraph: "Deterministic rule extraction with boundary checking and stoichiometric validation.",
  },
  {
    feature: "2D Table Geometry",
    llm: "Flattens tables into 1D text tokens; loses cell span alignments and multi-row headers.",
    crystagraph: "Explicit XML/PDF cell tree parser preserving exact row/column coordinate matrices.",
  },
  {
    feature: "Cross-Table Association",
    llm: "Fails to reliably link alloy formulations in Table 1 with test properties in Table 2.",
    crystagraph: "Relational Knowledge Linker establishes cross-table N-tuples with exact paper context.",
  },
  {
    feature: "Data Persistence & Audit",
    llm: "Ephemeral conversational replies; cannot be queried with SQL or reviewed in-cell.",
    crystagraph: "Indexed SQLite database (matgraph.db) with user review logs and academic audit trail.",
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      {/* Top Quiet Academic Navigation */}
      <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/95 backdrop-blur-sm">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-md bg-slate-900 text-white font-semibold">
              <Atom className="h-5 w-5 text-sky-400" />
            </div>
            <div>
              <span className="text-base font-semibold tracking-tight text-slate-900">
                CrystaGraph
              </span>
              <span className="ml-2 hidden text-xs font-normal text-slate-500 sm:inline">
                Materials Knowledge Mining Platform
              </span>
            </div>
          </div>

          <nav className="flex items-center gap-6">
            <a
              href="#methodology"
              className="hidden text-sm font-medium text-slate-600 hover:text-slate-900 md:inline"
            >
              Methodology
            </a>
            <a
              href="#benchmarks"
              className="hidden text-sm font-medium text-slate-600 hover:text-slate-900 md:inline"
            >
              Benchmark Data
            </a>
            <a
              href="#comparison"
              className="hidden text-sm font-medium text-slate-600 hover:text-slate-900 md:inline"
            >
              Grounded AI vs LLMs
            </a>

            <div className="flex items-center gap-3">
              <Link
                href="/login"
                className="text-sm font-medium text-slate-700 hover:text-slate-900 px-3 py-1.5"
              >
                Sign in
              </Link>
              <Link
                href="/dashboard"
                className="inline-flex items-center gap-2 rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-slate-800 transition-colors"
              >
                Enter Workspace
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative border-b border-slate-200 bg-white pt-16 pb-20 sm:pt-20 sm:pb-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl">
            <div className="inline-flex items-center gap-2 rounded-full border border-sky-200 bg-sky-50 px-3 py-1 text-xs font-medium text-sky-800 mb-6">
              <span className="flex h-1.5 w-1.5 rounded-full bg-sky-600" />
              Academic Research Platform &bull; BML Munjal University
            </div>

            <h1 className="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl lg:text-5xl">
              Extract structured material knowledge from scientific tables and literature
            </h1>

            <p className="mt-5 text-lg leading-relaxed text-slate-600">
              Over 80% of published material compositions and experimental properties are locked
              inside complex tabular matrices. CrystaGraph automatically parses research articles,
              resolves merged cell geometry, extracts stoichiometric fractions, standardizes
              canonical SI units, and links composition-property relationships for accelerated
              materials discovery.
            </p>

            <div className="mt-8 flex flex-wrap items-center gap-4">
              <Link
                href="/dashboard"
                className="inline-flex items-center gap-2 rounded-md bg-sky-600 px-5 py-2.5 text-sm font-medium text-white shadow-sm hover:bg-sky-500 transition-colors"
              >
                Launch Research Workspace
                <ArrowRight className="h-4 w-4" />
              </Link>
              <a
                href="#benchmarks"
                className="inline-flex items-center gap-2 rounded-md border border-slate-300 bg-white px-5 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors"
              >
                View 10 Benchmark Papers
              </a>
            </div>

            <div className="mt-10 grid grid-cols-2 gap-6 border-t border-slate-100 pt-6 sm:grid-cols-4">
              <div>
                <p className="text-2xl font-bold text-slate-900 tabular-nums">10</p>
                <p className="text-xs text-slate-500 mt-0.5">Benchmark Papers</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900 tabular-nums">20 / 20</p>
                <p className="text-xs text-slate-500 mt-0.5">Tables Extracted (100%)</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900 tabular-nums">255</p>
                <p className="text-xs text-slate-500 mt-0.5">SI Property Triples</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-900 tabular-nums">98.4%</p>
                <p className="text-xs text-slate-500 mt-0.5">Numeric Validity Ratio</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Interactive Live Data Preview (The Moment) */}
      <section id="benchmarks" className="py-16 sm:py-20 bg-slate-50">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-8">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-sky-700">
                Grounded Literature Records
              </p>
              <h2 className="text-2xl font-bold tracking-tight text-slate-900 mt-1">
                Sample Extracted Material Knowledge
              </h2>
              <p className="text-sm text-slate-500 mt-1">
                Every value preserves exact provenance, original units, and converted SI standards.
              </p>
            </div>
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-1.5 text-sm font-medium text-sky-700 hover:text-sky-800"
            >
              Open in Table Explorer &rarr;
            </Link>
          </div>

          <div className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-700">
                <thead className="border-b border-slate-200 bg-slate-50/80 text-xs font-semibold uppercase text-slate-600">
                  <tr>
                    <th scope="col" className="px-5 py-3.5">
                      Material System
                    </th>
                    <th scope="col" className="px-5 py-3.5">
                      Elemental Composition
                    </th>
                    <th scope="col" className="px-5 py-3.5">
                      Property
                    </th>
                    <th scope="col" className="px-5 py-3.5">
                      Reported Value
                    </th>
                    <th scope="col" className="px-5 py-3.5">
                      Standard SI
                    </th>
                    <th scope="col" className="px-5 py-3.5">
                      Source Literature (DOI)
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-normal">
                  {SAMPLE_EXTRACTIONS.map((row, idx) => (
                    <tr key={idx} className="hover:bg-slate-50/80 transition-colors">
                      <td className="px-5 py-3.5 font-medium text-slate-900 whitespace-nowrap">
                        {row.material}
                      </td>
                      <td className="px-5 py-3.5 text-xs text-slate-600 font-mono">
                        {row.composition}
                      </td>
                      <td className="px-5 py-3.5 font-medium text-slate-800 whitespace-nowrap">
                        {row.property}
                      </td>
                      <td className="px-5 py-3.5 tabular-nums whitespace-nowrap text-slate-600">
                        {row.reported}
                      </td>
                      <td className="px-5 py-3.5 whitespace-nowrap">
                        <span className="inline-flex items-center rounded bg-emerald-50 px-2 py-0.5 text-xs font-medium text-emerald-800 border border-emerald-200/60 tabular-nums">
                          {row.siValue}
                        </span>
                      </td>
                      <td className="px-5 py-3.5 text-xs text-slate-500 whitespace-nowrap">
                        <span className="font-mono text-slate-600">{row.source}</span>
                        <span className="block text-[11px] text-slate-400 truncate max-w-xs">
                          {row.paper}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>

      {/* Methodology Section */}
      <section id="methodology" className="border-t border-slate-200 bg-white py-16 sm:py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="max-w-2xl mb-12">
            <p className="text-xs font-semibold uppercase tracking-wider text-sky-700">
              Architectural Pipeline
            </p>
            <h2 className="text-2xl font-bold tracking-tight text-slate-900 mt-1">
              End-to-End Scientific Extraction Pipeline
            </h2>
            <p className="text-sm text-slate-500 mt-2">
              How CrystaGraph converts unstructured scientific XML and PDF research articles into
              traceable, queryable material knowledge.
            </p>
          </div>

          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-5">
            {METHODOLOGY_STAGES.map((st, i) => (
              <div
                key={i}
                className="flex flex-col justify-between rounded-lg border border-slate-200 bg-slate-50/50 p-5 hover:border-slate-300 transition-colors"
              >
                <div>
                  <span className="text-xs font-mono font-semibold text-sky-700">{st.step}</span>
                  <h3 className="text-base font-semibold text-slate-900 mt-2">{st.title}</h3>
                  <p className="text-xs leading-relaxed text-slate-600 mt-2">{st.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Comparison: Grounded Extraction vs Chatbots */}
      <section id="comparison" className="border-t border-slate-200 bg-slate-50 py-16 sm:py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="max-w-2xl mb-10">
            <p className="text-xs font-semibold uppercase tracking-wider text-sky-700">
              Academic Trust & Rigor
            </p>
            <h2 className="text-2xl font-bold tracking-tight text-slate-900 mt-1">
              Why Deterministic Table Extraction Beats General AI Chatbots
            </h2>
            <p className="text-sm text-slate-500 mt-2">
              For materials informatics, statistical hallucination and lost table coordinates make
              conversational LLMs unsuitable for empirical science.
            </p>
          </div>

          <div className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
            <table className="w-full text-left text-sm text-slate-700">
              <thead className="border-b border-slate-200 bg-slate-50 text-xs font-semibold uppercase text-slate-600">
                <tr>
                  <th scope="col" className="px-6 py-3.5 w-1/4">
                    Technical Capability
                  </th>
                  <th scope="col" className="px-6 py-3.5 w-3/8 text-rose-900 bg-rose-50/40">
                    General AI Chatbots (LLMs)
                  </th>
                  <th scope="col" className="px-6 py-3.5 w-3/8 text-sky-900 bg-sky-50/40">
                    CrystaGraph Grounded Engine
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {BOT_VS_CRYSTAGRAPH.map((item, idx) => (
                  <tr key={idx}>
                    <td className="px-6 py-4 font-semibold text-slate-900">{item.feature}</td>
                    <td className="px-6 py-4 text-xs text-slate-600 leading-relaxed bg-rose-50/20">
                      {item.llm}
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-800 leading-relaxed bg-sky-50/20 font-medium">
                      {item.crystagraph}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Academic Citation & Institutional Credits */}
      <section className="border-t border-slate-200 bg-white py-14">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="rounded-lg border border-slate-200 bg-slate-50/60 p-6 sm:p-8">
            <h3 className="text-base font-semibold text-slate-900">
              Academic Context & Literature Foundation
            </h3>
            <p className="mt-2 text-xs leading-relaxed text-slate-600">
              CrystaGraph builds upon foundations established in materials science natural language
              processing and table informatics:
            </p>

            <ul className="mt-4 space-y-2 text-xs text-slate-600">
              <li className="flex items-start gap-2">
                <span className="font-mono text-slate-400">[1]</span>
                <span>
                  <strong>MatSciBERT</strong> (Gupta et al., 2022) — Materials-aware domain
                  transformer language model representation.
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="font-mono text-slate-400">[2]</span>
                <span>
                  <strong>Zhang et al.</strong> (Digital Discovery, 2023) — Literature mining
                  integrating text and tabular materials parsing.
                </span>
              </li>
              <li className="flex items-start gap-2">
                <span className="font-mono text-slate-400">[3]</span>
                <span>
                  <strong>MatSKRAFT</strong> (Hira et al., 2025) — Graph representation and
                  constraint-driven composition-property table extraction.
                </span>
              </li>
            </ul>

            <div className="mt-6 pt-5 border-t border-slate-200 text-xs text-slate-500 flex flex-wrap justify-between items-center gap-4">
              <p>
                Department of Computer Science & Engineering &bull; School of Engineering and
                Technology, BML Munjal University
              </p>
              <p className="font-mono text-slate-400">Project-4 Capstone Evaluation</p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-slate-50 py-8 text-xs text-slate-500">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p>&copy; {new Date().getFullYear()} CrystaGraph Materials Informatics Platform. MIT License.</p>
          <div className="flex items-center gap-6">
            <Link href="/login" className="hover:text-slate-900">
              Researcher Sign In
            </Link>
            <Link href="/dashboard" className="hover:text-slate-900">
              Workspace Dashboard
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
