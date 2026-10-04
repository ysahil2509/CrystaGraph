"""
Knowledge Graph Page: Interactive graph visualization of Paper -> Table -> Material -> Property -> Value.
"""

import streamlit as st
import os
import sys
import pandas as pd
import networkx as nx

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, APP_DIR)

from components.db_utils import query_df, get_all_papers
from components.graph import build_knowledge_graph, plot_interactive_graph

st.set_page_config(page_title="Knowledge Graph | CrystaGraph", page_icon="🕸️", layout="wide")

st.title("🕸️ Materials Knowledge Graph")
st.caption("Multi-relational graph visualization connecting scientific papers, tables, material entities, and properties.")

df_knowledge = query_df("""
SELECT material_name, composition_summary, property_name, property_category, value_raw, unit, paper_id, doi, table_id
FROM material_knowledge;
""")

if df_knowledge.empty:
    st.warning("No knowledge triples available to build graph.")
    st.stop()

# Controls & Filters
papers_list = ["All Papers"] + get_all_papers()["paper_id"].tolist()

c_ctrl1, c_ctrl2 = st.columns([1, 1])
with c_ctrl1:
    selected_paper = st.selectbox("Filter by Scientific Paper:", papers_list)
with c_ctrl2:
    max_mats = st.slider("Max Material Nodes to Display:", min_value=3, max_value=25, value=8)

# Build Graph
with st.spinner("Constructing multi-relational knowledge graph..."):
    G = build_knowledge_graph(df_knowledge, max_materials=max_mats, selected_paper=selected_paper)
    fig_graph = plot_interactive_graph(G)

st.plotly_chart(fig_graph, use_container_width=True)

# Graph Statistics
c_s1, c_s2, c_s3, c_s4 = st.columns(4)
with c_s1:
    st.metric("Graph Nodes", len(G.nodes))
with c_s2:
    st.metric("Graph Edges", len(G.edges))
with c_s3:
    st.metric("Graph Density", f"{len(G.edges)/(len(G.nodes)*(len(G.nodes)-1) + 1e-6):.3f}")
with c_s4:
    st.metric("Isolated Subgraphs", len(list(nx.weakly_connected_components(G))) if len(G.nodes)>0 else 0)

st.markdown("---")
st.markdown("""
**🎨 Graph Node Ontology & Edge Legend:**
- 🔵 **Paper Node**: Represents the scientific publication source (DOI metadata).
- 🟢 **Table Node**: Represents the extracted table node with captions.
- 🟠 **Material Node**: Represents the chemical alloy, compound, or formulation.
- 🟣 **Property Node**: Represents the target material property (e.g. Yield Strength, Hardness, Density).
- 🔴 **Value Node**: Represents the measured quantitative value and standardized physical unit.
""")
