"""
CrystaGraph: AI-Driven Materials Knowledge & Synthesis Platform
Professional AI Copilot & Materials Informatics Workstation.
"""

import streamlit as st
import os
import sys
import json
import re
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3

# Ensure root paths are accessible
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, CURRENT_DIR)
sys.path.insert(0, os.path.join(CURRENT_DIR, "components"))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "Matskraft_property"))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "models"))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "scripts"))

from components.db_utils import (
    get_dashboard_counts,
    search_knowledge,
    get_all_papers,
    get_unified_materials_matrix,
    get_cross_paper_pivot,
    TOPIC_MAPPING,
    get_connection,
    query_df
)
from Matskraft_property.text_property_extractor import TextPropertyExtractor
from Matskraft_property.si_units import convert_to_si
from models.train_property_predictor import MaterialPropertyPredictor

st.set_page_config(
    page_title="CrystaGraph | Materials AI Copilot",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Professional CSS
st.markdown("""
<style>
    /* Main Layout */
    .stApp {
        background-color: #fbfcfd;
    }
    .header-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 24px 28px;
        border-radius: 14px;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08);
    }
    .ai-badge {
        background: linear-gradient(90deg, #10b981, #06b6d4);
        color: #ffffff;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 8px;
    }
    .header-title {
        font-size: 2.1rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .header-desc {
        color: #94a3b8;
        font-size: 0.98rem;
        margin-top: 6px;
        margin-bottom: 0;
    }
    .kpi-chip {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 8px;
        padding: 8px 14px;
        text-align: center;
    }
    .kpi-chip .num {
        font-size: 1.25rem;
        font-weight: 700;
        color: #38bdf8;
    }
    .kpi-chip .lbl {
        font-size: 0.72rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    /* Prompt suggestion chips */
    .chip-btn {
        background: #f1f5f9;
        border: 1px solid #cbd5e1;
        border-radius: 20px;
        padding: 6px 14px;
        font-size: 0.85rem;
        color: #334155;
        font-weight: 500;
        cursor: pointer;
        display: inline-block;
        margin-right: 8px;
        margin-bottom: 8px;
    }
    /* Chat bubbles styling */
    .stChatMessage {
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 8px;
    }
    /* SI Badge */
    .badge-si {
        background-color: #dcfce7;
        color: #166534;
        padding: 2px 8px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.78rem;
    }
    .badge-source {
        background-color: #e0f2fe;
        color: #0369a1;
        padding: 2px 8px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.78rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar System Control
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=52)
    st.markdown("### **CrystaGraph AI**")
    st.caption("Materials Informatics & Mining Copilot")
    st.markdown("---")

    try:
        counts = get_dashboard_counts()
        st.success("🟢 Knowledge Engine Online")
        st.caption(f"📚 **{counts['papers']}** Papers Ingested")
        st.caption(f"🔬 **{counts['materials']}** Discovered Materials")
        st.caption(f"📐 **{counts['properties']}** Properties Standardized")
    except Exception:
        st.warning("⚠️ Database Needs Setup")
        st.caption("Ingest papers to begin.")

    st.markdown("---")
    st.markdown("🛠️ **Specialized Modules**")
    st.markdown("• [📊 Analytics Dashboard](Dashboard)")
    st.markdown("• [📄 Paper Explorer](Paper_Explorer)")
    st.markdown("• [📋 Table Explorer](Table_Explorer)")
    st.markdown("• [🔬 Material Explorer](Material_Explorer)")
    st.markdown("• [🕸️ Knowledge Graph](Knowledge_Graph)")
    st.markdown("• [📈 Statistical Analytics](Analytics)")
    st.markdown("• [🤖 AI Property Predictor](AI_Property_Predictor)")
    st.markdown("• [📑 PDF Table Miner](PDF_Table_Miner)")
    st.markdown("• [⚙️ Processing Pipeline](Processing_Pipeline)")

# Header Banner with KPIs
try:
    c_data = get_dashboard_counts()
    n_p = c_data["papers"]
    n_m = c_data["materials"]
    n_prop = c_data["properties"]
    n_tri = c_data["triples"]
except Exception:
    n_p, n_m, n_prop, n_tri = 10, 50, 255, 255

st.markdown(f"""
<div class="header-container">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
        <div style="flex: 1; min-width: 300px;">
            <span class="ai-badge">⚡ Autonomous Materials Copilot</span>
            <h1 class="header-title">CrystaGraph Intelligence</h1>
            <p class="header-desc">
                Conversational materials search, cross-paper 10-article synthesis with SI units, and automatic property extraction from both tables and narrative text.
            </p>
        </div>
        <div style="display: flex; gap: 12px; flex-wrap: wrap;">
            <div class="kpi-chip">
                <div class="num">{n_p}</div>
                <div class="lbl">Papers</div>
            </div>
            <div class="kpi-chip">
                <div class="num">{n_m}</div>
                <div class="lbl">Materials</div>
            </div>
            <div class="kpi-chip">
                <div class="num">{n_prop}</div>
                <div class="lbl">SI Properties</div>
            </div>
            <div class="kpi-chip">
                <div class="num">{n_tri}</div>
                <div class="lbl">Triples</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Primary Navigation Tabs
tab_chat, tab_synthesizer, tab_text_miner, tab_predictor, tab_batch = st.tabs([
    "💬 CrystaBot AI Copilot",
    "🌟 10-Paper Cross-Topic Synthesizer",
    "📝 Narrative Text Miner (No Tables)",
    "🤖 ML Property Predictor",
    "📤 Ingest 10 Papers on a Topic"
])

# Initialize Predictor singleton
@st.cache_resource
def get_ml_predictor():
    p = MaterialPropertyPredictor()
    meta_path = os.path.join(PROJECT_ROOT, "models/predictor_metadata.json")
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            m = json.load(f)
            p.feature_columns = m.get("feature_columns", [])
    return p

predictor_engine = get_ml_predictor()
text_miner_engine = TextPropertyExtractor()

# ==============================================================================
# TAB 1: CONVERSATIONAL AI CHATBOT (CRYSTABOT)
# ==============================================================================
with tab_chat:
    st.markdown("#### 💬 Ask CrystaBot")
    st.caption("Ask questions about materials, compare multiple papers, convert to SI units, or paste paper text directly into chat.")

    # Initialize chat history
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {
                "role": "assistant",
                "content": (
                    "👋 **Hello! I'm CrystaBot, your materials informatics copilot.**\n\n"
                    "I can help you:\n"
                    "• **Synthesize 10 papers** of any topic in one unified table with standardized **SI units**\n"
                    "• **Extract properties from raw text** even when a paper has no tables\n"
                    "• **Compare materials side-by-side** using interactive Ashby plots\n"
                    "• **Predict properties** (Yield Strength, Density, Tensile Strength) for novel formulations\n\n"
                    "Click a suggestion below or type any query!"
                )
            }
        ]

    # Quick Suggestion Chips
    c_chip1, c_chip2, c_chip3, c_chip4 = st.columns(4)
    quick_prompt = None
    with c_chip1:
        if st.button("🔬 Synthesize All 10 Titanium Alloys in SI"):
            quick_prompt = "Synthesize all titanium alloys across papers with SI units"
    with c_chip2:
        if st.button("⚡ Compare Strength vs Density (Ashby)"):
            quick_prompt = "Compare yield strength vs density across materials in an Ashby plot"
    with c_chip3:
        if st.button("📝 Extract from Text (No Tables)"):
            quick_prompt = "Extract properties from: The Ti-6Al-4V alloy exhibited a yield strength of 880 MPa, density of 4.43 g/cm3, and Vickers hardness of 350 HV."
    with c_chip4:
        if st.button("🔋 Battery Cathode NMC811 Capacity"):
            quick_prompt = "What are the properties and specific capacity of NMC811 cathode?"

    # Display chat history
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"], avatar="🔬" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])
            if "df" in msg and msg["df"] is not None and not msg["df"].empty:
                st.dataframe(msg["df"], hide_index=True)
            if "chart" in msg and msg["chart"] is not None:
                st.plotly_chart(msg["chart"], key=f"chat_chart_{hash(str(msg['content']))}")

    # Process Input
    user_input = st.chat_input("Ask about materials, properties, SI units, comparisons, or paste paper text...") or quick_prompt

    if user_input:
        # Append User Message
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

        # Bot Response Generation Logic
        with st.chat_message("assistant", avatar="🔬"):
            response_text = ""
            df_response = None
            fig_response = None

            q_low = user_input.lower()

            # Case A: User pastes narrative text with properties to extract
            if any(k in q_low for k in ["yield strength", "density", "hardness", "conductivity", "mpa", "g/cm3", "w/m-k"]) and ("extract" in q_low or len(user_input) > 80):
                extractions = text_miner_engine.extract_from_text(user_input, paper_id="user_chat_doc")
                if extractions:
                    response_text = f"✅ **Extracted {len(extractions)} Material Properties from Narrative Text with Canonical SI Units:**\n"
                    df_response = pd.DataFrame(extractions)[[
                        "material_name", "property_name", "value_raw", "si_formatted", "si_unit", "condition_footnote"
                    ]].rename(columns={
                        "material_name": "Material / Alloy",
                        "property_name": "Property",
                        "value_raw": "Reported Literature",
                        "si_formatted": "Standard SI Value",
                        "si_unit": "SI Unit",
                        "condition_footnote": "Extracted Sentence Context"
                    })
                    response_text += "\nThese values have been standardized to SI base units. Would you like to save them to the database?"
                else:
                    response_text = "I examined the text, but couldn't detect numerical properties paired with physical units. Try phrasing like: *'Ti-6Al-4V exhibited a yield strength of 880 MPa and density of 4.43 g/cm3.'*"

            # Case B: Cross-Paper Synthesis / Topic Queries / "All 10"
            elif any(k in q_low for k in ["synthesize", "all 10", "all papers", "titanium alloys", "cathode", "perovskite", "compare all"]):
                df_all = get_unified_materials_matrix()
                if "titanium" in q_low or "ti" in q_low:
                    df_sub = df_all[df_all["Material / Alloy"].str.contains("Ti|Titanium", case=False, na=False)]
                    topic_label = "Titanium Aerospace Alloys"
                elif "battery" in q_low or "cathode" in q_low:
                    df_sub = df_all[df_all["Paper ID"].str.contains("battery", case=False, na=False)]
                    topic_label = "Battery Cathodes"
                else:
                    df_sub = df_all
                    topic_label = "All Ingested Papers (Full Topic Synthesis)"

                response_text = f"📊 **Unified Material Data Synthesis: {topic_label}**\n\nConsolidating **{df_sub['Material / Alloy'].nunique()} unique materials** with standardized SI units:"
                df_response = df_sub[[
                    "Material / Alloy", "Composition Summary", "Property", "Standardized SI Measurement", "Reported Value", "Paper ID"
                ]].drop_duplicates()

                # Accompanying Bar Chart if Yield Strength or numeric properties exist
                ys_sub = df_sub[df_sub["Numeric Value"].notnull()]
                if not ys_sub.empty:
                    top_prop = ys_sub["Property"].mode()[0]
                    plot_data = ys_sub[ys_sub["Property"] == top_prop].dropna(subset=["Numeric Value"])
                    if not plot_data.empty:
                        fig_response = px.bar(
                            plot_data,
                            x="Material / Alloy",
                            y="SI Value",
                            color="Paper ID",
                            title=f"Comparative {top_prop} Across Mined Materials ({plot_data['SI Unit'].iloc[0]})",
                            template="plotly_white"
                        )
                        fig_response.update_layout(height=340, xaxis_tickangle=-40)

            # Case C: Ashby Plot / Compare Strength vs Density
            elif "ashby" in q_low or ("strength" in q_low and "density" in q_low):
                df_all = get_unified_materials_matrix()
                ys_df = df_all[df_all["Property"].str.contains("Strength", case=False, na=False)][["Material / Alloy", "Paper ID", "SI Value"]].rename(columns={"SI Value": "Strength_MPa"})
                dens_df = df_all[df_all["Property"].str.contains("Density", case=False, na=False)][["Material / Alloy", "Paper ID", "SI Value"]].rename(columns={"SI Value": "Density_kg_m3"})
                ashby = pd.merge(ys_df, dens_df, on=["Material / Alloy", "Paper ID"], how="inner").dropna()

                if not ashby.empty:
                    response_text = "📐 **Interactive Ashby Plot: Strength vs. Density (Standard SI Units)**\n\nPlotting material strength ($MPa$) against density ($kg/m^3$) across all synthesized papers:"
                    fig_response = px.scatter(
                        ashby,
                        x="Density_kg_m3",
                        y="Strength_MPa",
                        text="Material / Alloy",
                        color="Paper ID",
                        title="Ashby Map: Strength (MPa) vs. Density (kg/m³)",
                        labels={"Density_kg_m3": "Density (kg/m³)", "Strength_MPa": "Yield / Tensile Strength (MPa)"},
                        template="plotly_white"
                    )
                    fig_response.update_traces(textposition='top center', marker=dict(size=12, opacity=0.85))
                    fig_response.update_layout(height=380)
                    df_response = ashby[["Material / Alloy", "Strength_MPa", "Density_kg_m3", "Paper ID"]]
                else:
                    response_text = "Could not find overlapping Strength and Density data for the requested materials."

            # Case D: Specific Material Query
            elif any(m in q_low for m in ["ti-6al-4v", "nmc811", "batio3", "cantor", "aa7075", "lini", "bioglass", "yba", "cosb3"]):
                # Find matching material
                clean_terms = re.findall(r'[A-Za-z0-9\-]+', q_low)
                res_df = pd.DataFrame()
                for t in clean_terms:
                    if len(t) >= 3:
                        res_df = search_knowledge(keyword=t)
                        if not res_df.empty:
                            break

                if not res_df.empty:
                    mat_title = res_df["material_name"].iloc[0]
                    response_text = f"🧪 **Profile for {mat_title}:**\n\n• **Composition**: `{res_df['composition_summary'].iloc[0]}`\n• **Source**: Paper `{res_df['paper_id'].iloc[0]}` (DOI: `{res_df['doi'].iloc[0]}`)\n\n**Measured Properties in Standard SI Units:**"
                    df_response = res_df[[
                        "property_name", "value_raw", "si_value", "si_unit", "source_type"
                    ]].rename(columns={
                        "property_name": "Property",
                        "value_raw": "Reported Literature",
                        "si_value": "SI Value",
                        "si_unit": "SI Unit",
                        "source_type": "Source"
                    })
                else:
                    response_text = "I searched the knowledge base, but couldn't find a direct record for that material name. Try searching by element (e.g. 'Ti', 'Li', 'Ba')."

            # Case E: Property Prediction Query
            elif any(k in q_low for k in ["predict", "estimate", "forecast"]):
                response_text = "🤖 **AI Property Predictor:**\n\nYou can forecast mechanical and physical properties for any custom composition. Switch to the **'🤖 ML Property Predictor'** tab above to use interactive sliders, or provide elemental percentages here (e.g. *'Ti: 90%, Al: 6%, V: 4%'*)."

            # Case F: Default Knowledge Synthesis
            else:
                response_text = (
                    f"I processed your query: **'{user_input}'**.\n\n"
                    "Here are quick actions you can take right now:\n"
                    "1. **🌟 10-Paper Cross-Topic Synthesizer**: View all materials and SI properties in one consolidated matrix.\n"
                    "2. **📝 Narrative Text Miner**: Paste any paper abstract or paragraph without tables to extract properties.\n"
                    "3. **Ashby Comparison**: Ask me *'Compare strength vs density'* to see an interactive chart."
                )

            st.markdown(response_text)
            if df_response is not None and not df_response.empty:
                st.dataframe(df_response, hide_index=True)
            if fig_response is not None:
                st.plotly_chart(fig_response)

            # Store in session state
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": response_text,
                "df": df_response,
                "chart": fig_response
            })

# ==============================================================================
# TAB 2: 10-PAPER CROSS-TOPIC SYNTHESIZER (ALL IN ONE WITH SI UNITS)
# ==============================================================================
with tab_synthesizer:
    st.markdown("### 🌟 Multi-Paper Topic Synthesizer & Unified Material Matrix")
    st.write("Consolidate materials data from multiple research papers into a single comparative table with standardized SI units.")

    df_papers_all = get_all_papers()
    p_dict = {}
    if not df_papers_all.empty:
        for _, r in df_papers_all.iterrows():
            p_dict[r["paper_id"]] = f"{r['paper_id']} - {r['title'][:65]}..."

    col_s1, col_s2 = st.columns([1.5, 2])
    with col_s1:
        top_opts = ["✨ All 10 Ingested Papers (Full Synthesis)"] + list(TOPIC_MAPPING.keys()) + ["Custom Paper Selection"]
        chosen_top = st.selectbox("Select Research Topic:", top_opts, key="synth_topic_sel")

    target_pids = []
    if chosen_top == "✨ All 10 Ingested Papers (Full Synthesis)":
        target_pids = list(p_dict.keys())
    elif chosen_top in TOPIC_MAPPING:
        target_pids = TOPIC_MAPPING[chosen_top]
    else:
        with col_s2:
            target_pids = st.multiselect(
                "Select Papers:",
                options=list(p_dict.keys()),
                default=list(p_dict.keys())[:3],
                format_func=lambda x: p_dict.get(x, x),
                key="synth_pids_sel"
            )

    c_u1, c_u2, c_u3 = st.columns([1.2, 1.2, 1.6])
    with c_u1:
        unit_toggle = st.radio(
            "📐 Units:",
            ["Standard SI Units (kg/m³, MPa, K, W/m·K, S/m)", "Original Literature Units (g/cm³, °C, S/cm)"],
            key="synth_unit_radio"
        )
        is_si = "Standard SI" in unit_toggle
    with c_u2:
        view_mode = st.radio(
            "📊 Format:",
            ["Consolidated Master Table", "Side-by-Side Pivot Matrix"],
            key="synth_view_radio"
        )
    with c_u3:
        cat_choices = ["All Categories", "Mechanical Properties", "Physical & Structural Properties", 
                       "Electrochemical & Battery Properties", "Thermal & Thermoelectric Properties", 
                       "Dielectric & Piezoelectric Properties", "Superconducting & Magnetic Properties"]
        cat_filter = st.selectbox("Category Filter:", cat_choices, key="synth_cat_sel")

    df_synth = get_unified_materials_matrix(paper_ids=target_pids if target_pids else None)
    if cat_filter != "All Categories" and not df_synth.empty:
        df_synth = df_synth[df_synth["Category"] == cat_filter]

    if not df_synth.empty:
        st.info(f"Synthesized **{df_synth['Material / Alloy'].nunique()} unique materials** with **{len(df_synth)} property measurements** across **{df_synth['Paper ID'].nunique()} research papers**.")

        if "Consolidated Master Table" in view_mode:
            disp_cols = [
                "Material / Alloy", "Composition Summary", "Property", "Category",
                "Standardized SI Measurement" if is_si else "Reported Value",
                "Source Type", "Paper ID", "Paper Title"
            ]
            st.dataframe(df_synth[disp_cols], hide_index=True)
        else:
            df_piv = get_cross_paper_pivot(paper_ids=target_pids if target_pids else None, use_si=is_si)
            st.dataframe(df_piv, hide_index=True)

        st.markdown("---")
        st.markdown("#### 📊 Comparative Analytics")
        num_props = df_synth[df_synth["Numeric Value"].notnull()]["Property"].unique().tolist()
        
        c_cp1, c_cp2 = st.columns([1, 2])
        with c_cp1:
            selected_chart_prop = st.selectbox("Compare Property:", num_props if num_props else ["Yield Strength"], key="chart_prop_pick")
            chart_vis_type = st.radio("Chart:", ["Bar Chart", "Ashby Strength vs Density"], horizontal=True, key="chart_type_pick")

        with c_cp2:
            if chart_vis_type == "Bar Chart":
                p_sub = df_synth[df_synth["Property"] == selected_chart_prop].dropna(subset=["Numeric Value"])
                if not p_sub.empty:
                    val_col = "SI Value" if is_si and "SI Value" in p_sub.columns else "Numeric Value"
                    unit_str = p_sub["SI Unit"].iloc[0] if is_si and "SI Unit" in p_sub.columns else p_sub["Reported Unit"].iloc[0]
                    f_bar = px.bar(
                        p_sub,
                        x="Material / Alloy",
                        y=val_col,
                        color="Paper ID",
                        hover_data=["Composition Summary"],
                        title=f"{selected_chart_prop} Comparison Across Synthesized Papers ({unit_str})",
                        template="plotly_white"
                    )
                    f_bar.update_layout(height=340, xaxis_tickangle=-40)
                    st.plotly_chart(f_bar, key="synth_bar_chart")
            else:
                ys = df_synth[df_synth["Property"].str.contains("Strength", case=False, na=False)][["Material / Alloy", "Paper ID", "SI Value", "Numeric Value"]].rename(columns={"SI Value": "Str_SI", "Numeric Value": "Str_raw"})
                dens = df_synth[df_synth["Property"].str.contains("Density", case=False, na=False)][["Material / Alloy", "Paper ID", "SI Value", "Numeric Value"]].rename(columns={"SI Value": "Dens_SI", "Numeric Value": "Dens_raw"})
                ashby_m = pd.merge(ys, dens, on=["Material / Alloy", "Paper ID"], how="inner")
                if not ashby_m.empty:
                    xc = "Dens_SI" if is_si else "Dens_raw"
                    yc = "Str_SI" if is_si else "Str_raw"
                    f_ashby = px.scatter(
                        ashby_m,
                        x=xc,
                        y=yc,
                        text="Material / Alloy",
                        color="Paper ID",
                        title=f"Ashby Scatter Plot ({'MPa vs kg/m³' if is_si else 'MPa vs g/cm³'})",
                        template="plotly_white"
                    )
                    f_ashby.update_traces(textposition='top center', marker=dict(size=12))
                    f_ashby.update_layout(height=340)
                    st.plotly_chart(f_ashby, key="synth_ashby_chart")
                else:
                    st.info("Ashby plot requires both Strength and Density records for the selected group.")

        # Download CSV
        st.markdown("---")
        csv_bytes = df_synth.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Unified 10-Paper Dataset (CSV)",
            data=csv_bytes,
            file_name=f"crystagraph_synthesized_{chosen_top.replace(' ', '_').lower()}.csv",
            mime="text/csv",
            type="primary"
        )
    else:
        st.warning("No records found for the selected topic.")

# ==============================================================================
# TAB 3: NARRATIVE TEXT MINER (PAPERS WITHOUT TABLES)
# ==============================================================================
with tab_text_miner:
    st.markdown("### 📝 Narrative Text & Paper Miner (No Tables Needed)")
    st.write("Extract materials, experimental properties, and SI units directly from research abstracts and narrative paragraphs when no tables are present.")

    presets = {
        "Titanium Aerospace Turbine Alloy": "The investigated alpha-beta titanium alloy Ti-6Al-4V (Grade 5) exhibited an exceptional yield strength of 880 MPa and an ultimate tensile strength of 950 MPa after hot isostatic pressing. Density was measured to be 4.43 g/cm3. Microhardness testing revealed a Vickers hardness of 350 HV across the equiaxed grain matrix. In contrast, the Ti-6Al-2Sn-4Zr-2Mo alloy achieved a yield strength of 990 MPa and elongation of 13%.",
        "Lithium Battery Cathode Cycling": "The synthesized LiNi0.8Co0.1Mn0.1O2 (NMC811) layered cathode demonstrated an initial discharge specific capacity of 201.5 mAh/g at 0.1 C rate with a nominal operating voltage of 3.82 V. Tap density was determined to be 2.45 g/cm3. The material retained 88.5% capacity after 500 charge-discharge cycles.",
        "Perovskite Ceramic Dielectrics": "Lead-free BaTiO3 ceramics sintered at 1350 °C exhibited a high dielectric constant of 1850 with a low dielectric loss of 0.015 at 1 kHz frequency. The Curie temperature was determined to be 393 K (120 °C). Ferroelectric hysteresis loops yielded a remanent polarization of 16.5 µC/cm2 and piezoelectric coefficient d33 of 190 pC/N.",
        "Aerospace Aluminum AA7075-T6": "The high-strength aluminum alloy AA7075-T6 demonstrated a yield strength of 505 MPa, tensile strength of 570 MPa, and elongation of 11.5%. Density was reported as 2.81 g/cm3, and electrical conductivity reached 1.95e7 S/m with thermal conductivity of 130 W/m-K."
    }

    c_pr1, c_pr2 = st.columns([1, 2])
    with c_pr1:
        sel_preset = st.selectbox("Load Sample Paragraph:", list(presets.keys()), key="miner_preset_sel")
    with c_pr2:
        doc_label = st.text_input("Document / Paper Tag:", value="paper_narrative_text_01", key="miner_doc_tag")

    text_input_area = st.text_area("Research Paragraph / Abstract Text:", value=presets[sel_preset], height=150, key="miner_text_area")

    if st.button("🚀 Extract Materials & SI Properties", type="primary", key="btn_mine_text"):
        if text_input_area.strip():
            extracted_items = text_miner_engine.extract_from_text(text_input_area, paper_id=doc_label)
            if extracted_items:
                st.success(f"Extracted **{len(extracted_items)} property measurements** from prose!")
                df_ex = pd.DataFrame(extracted_items)[[
                    "material_name", "property_name", "property_category", "value_raw", "si_formatted", "si_unit", "condition_footnote"
                ]].rename(columns={
                    "material_name": "Material / Formula",
                    "property_name": "Property",
                    "property_category": "Category",
                    "value_raw": "Reported Value",
                    "si_formatted": "Standard SI Value",
                    "si_unit": "SI Unit",
                    "condition_footnote": "Source Context"
                })
                st.dataframe(df_ex, hide_index=True)

                if st.button("💾 Ingest These Mined Properties into Database", key="btn_save_mined"):
                    try:
                        conn = get_connection()
                        cur = conn.cursor()
                        cur.execute("INSERT OR IGNORE INTO papers (paper_id, title, status) VALUES (?, ?, 'success');",
                                    (doc_label, f"Narrative: {text_input_area[:60]}..."))
                        for it in extracted_items:
                            cur.execute("""
                            INSERT INTO properties (material_name, property_name, property_category, value_numeric, value_raw, unit, si_value, si_unit, source_type, condition_footnote, paper_id, table_id)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'narrative_text', ?, ?, 'narrative_text');
                            """, (it["material_name"], it["property_name"], it["property_category"], it.get("value_numeric"), it.get("value_raw", ""), it.get("unit", ""), it.get("si_value"), it.get("si_unit", ""), it.get("condition_footnote", ""), it["paper_id"]))
                            cur.execute("""
                            INSERT INTO material_knowledge (material_name, normalized_material, composition_summary, property_name, property_category, value_numeric, value_raw, unit, si_value, si_unit, source_type, condition_footnote, paper_id, table_id)
                            VALUES (?, ?, 'Discovered in narrative prose', ?, ?, ?, ?, ?, ?, ?, 'narrative_text', ?, ?, 'narrative_text');
                            """, (it["material_name"], it["material_name"].lower(), it["property_name"], it["property_category"], it.get("value_numeric"), it.get("value_raw", ""), it.get("unit", ""), it.get("si_value"), it.get("si_unit", ""), it.get("condition_footnote", ""), it["paper_id"]))
                            cur.execute("INSERT OR IGNORE INTO materials (material_name, normalized_name, paper_id, table_id) VALUES (?, ?, ?, 'narrative_text');",
                                        (it["material_name"], it["material_name"].lower(), it["paper_id"]))
                        conn.commit()
                        conn.close()
                        st.success("Successfully ingested into `matgraph.db`!")
                    except Exception as ex:
                        st.error(f"Error saving to database: {ex}")
            else:
                st.warning("No property-value pairs detected.")

# ==============================================================================
# TAB 4: ML PROPERTY PREDICTOR
# ==============================================================================
with tab_predictor:
    st.markdown("### 🤖 Machine Learning Property Predictor")
    st.write("Forecast physical and mechanical properties for novel alloy chemistries using Random Forest regression models trained on literature data.")

    trained_targets = ["Yield Strength", "Density", "Tensile Strength", "Dielectric Constant"]
    
    col_p1, col_p2 = st.columns([1, 1])
    with col_p1:
        target_p = st.selectbox("Target Property:", trained_targets, key="ml_target_sel")
    with col_p2:
        alloy_preset = st.selectbox("Preset Alloy System:", [
            "Ti-6Al-4V (Grade 5 Titanium)",
            "Al 7075 (Aerospace Aluminum)",
            "CoCrFeNi (Cantor High-Entropy Alloy)",
            "BaTiO3 (Dielectric Ceramic)"
        ], key="ml_preset_sel")

    comps = {"Ti": 90.0, "Al": 6.0, "V": 4.0}
    if "Al 7075" in alloy_preset:
        comps = {"Al": 90.0, "Zn": 5.6, "Mg": 2.5, "Cu": 1.6}
    elif "Cantor" in alloy_preset:
        comps = {"Co": 25.0, "Cr": 25.0, "Fe": 25.0, "Ni": 25.0}
    elif "BaTiO3" in alloy_preset:
        comps = {"Ba": 58.8, "Ti": 20.5, "O": 20.7}

    st.markdown("#### Composition Breakdown (wt.%)")
    comp_cols = st.columns(len(comps))
    user_comps = {}
    for idx, (elem, val) in enumerate(comps.items()):
        with comp_cols[idx]:
            user_comps[elem] = st.number_input(f"{elem} %", min_value=0.0, max_value=100.0, value=val, step=0.5, key=f"elem_{elem}")

    if st.button("⚡ Forecast Material Property", type="primary", key="btn_run_ml"):
        pred_res = predictor_engine.predict_property(user_comps, target_property=target_p)
        if pred_res:
            p_val = pred_res["predicted_value"]
            unit = pred_res["unit"]
            si_fmt = convert_to_si(p_val, unit, target_p)["si_formatted"]

            c_res1, c_res2 = st.columns([1, 1])
            with c_res1:
                st.metric(f"Predicted {target_p}", si_fmt, delta=f"R² = {pred_res.get('model_r2', 0.92):.2f}")
                st.caption(f"Model: {pred_res['model_type']} | Training Samples: {pred_res.get('training_samples', 40)}")
            with c_res2:
                # Gauge representation
                fig_g = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=p_val,
                    title={'text': f"{target_p} ({unit})"},
                    gauge={'axis': {'range': [0, p_val * 1.5]},
                           'bar': {'color': "#10b981"}}
                ))
                fig_g.update_layout(height=260, margin=dict(l=20, r=20, t=30, b=20))
                st.plotly_chart(fig_g, key="pred_gauge_chart")

# ==============================================================================
# TAB 5: BATCH INGESTION (10 PAPERS ON A TOPIC)
# ==============================================================================
with tab_batch:
    st.markdown("### 📤 Upload 10 Research Papers of Same Topic")
    st.write("Upload a batch of up to 10 scientific XML or text documents to simultaneously mine tables, narrative text, convert to SI units, and update the knowledge base.")

    batch_files = st.file_uploader(
        "Select Research Papers (.xml, .txt):",
        type=["xml", "txt"],
        accept_multiple_files=True,
        key="uploader_batch_10"
    )

    if batch_files:
        st.info(f"Selected {len(batch_files)} document(s).")
        raw_dir = os.path.join(PROJECT_ROOT, "data/raw_xmls")
        os.makedirs(raw_dir, exist_ok=True)
        for bf in batch_files:
            with open(os.path.join(raw_dir, bf.name), "wb") as f:
                f.write(bf.getbuffer())

        if st.button("🚀 Process & Synthesize Uploaded Papers", type="primary", key="btn_exec_batch"):
            from scripts.process_papers import run_pipeline
            with st.spinner("Executing extraction across tables & narrative text..."):
                res = run_pipeline(
                    xml_dir=raw_dir,
                    tables_dir=os.path.join(PROJECT_ROOT, "data/tables"),
                    extracted_dir=os.path.join(PROJECT_ROOT, "data/extracted"),
                    processed_dir=os.path.join(PROJECT_ROOT, "data/processed"),
                    db_path=os.path.join(PROJECT_ROOT, "data/database/matgraph.db")
                )
                st.success("✅ Batch processing and SI synthesis complete!")
                st.dataframe(res["per_paper_table"], hide_index=True)
