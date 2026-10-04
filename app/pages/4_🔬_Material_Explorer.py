"""
Material Explorer Page: Search and profile material entities, chemical compositions, and properties.
"""

import streamlit as st
import os
import sys
import pandas as pd
import plotly.express as px

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, APP_DIR)

from components.db_utils import query_df

st.set_page_config(page_title="Material Explorer | CrystaGraph", page_icon="🔬", layout="wide")

st.title("🔬 Material Knowledge Explorer")
st.caption("Search, filter, and inspect material entities, chemical stoichiometry, and experimental properties.")

# Material Selection / Search
all_mats_df = query_df("SELECT DISTINCT material_name FROM materials ORDER BY material_name;")
if all_mats_df.empty:
    st.warning("No materials found in database.")
    st.stop()

mat_list = all_mats_df["material_name"].tolist()

c_search1, c_search2 = st.columns([2, 1])
with c_search1:
    selected_material = st.selectbox("Select Material / Alloy / Compound:", mat_list)
with c_search2:
    search_keyword = st.text_input("Or Filter by Text / Element:", placeholder="e.g. Ti, Li, Ba, Bioglass, Al")

if search_keyword:
    matching_mats = [m for m in mat_list if search_keyword.lower() in m.lower()]
    if matching_mats:
        selected_material = st.selectbox("Matching Materials:", matching_mats)
    else:
        st.warning(f"No materials found matching '{search_keyword}'. Showing default.")

st.markdown("---")
st.markdown(f"## 🧪 Material Profile: **{selected_material}**")

# Query Linked Knowledge for this Material
df_knowledge = query_df("""
SELECT DISTINCT paper_id, doi, table_id, composition_summary, property_name, property_category, value_raw, unit, condition_footnote as condition
FROM material_knowledge
WHERE material_name = ?
ORDER BY property_name;
""", (selected_material,))

# Query Compositions
df_comp = query_df("""
SELECT component, percentage, unit, paper_id, table_id
FROM compositions
WHERE material_name = ?
ORDER BY percentage DESC;
""", (selected_material,))

# Query Properties
df_prop = query_df("""
SELECT 
    property_name as "Property",
    property_category as "Category",
    value_raw as "Reported Value",
    unit as "Reported Unit",
    CASE 
        WHEN si_value IS NOT NULL AND si_unit != '' THEN PRINTF('%.2f %s', si_value, si_unit)
        ELSE value_raw 
    END as "Standard SI Measurement",
    source_type as "Source",
    paper_id as "Paper ID",
    table_id as "Table/Section"
FROM properties
WHERE material_name = ?
ORDER BY property_name;
""", (selected_material,))

col_info1, col_info2 = st.columns([1, 1.2])

with col_info1:
    st.markdown("### 🧩 Chemical Composition")
    if not df_comp.empty:
        st.dataframe(df_comp[["component", "percentage", "unit", "paper_id"]], use_container_width=True, hide_index=True)
        # Pie chart of composition
        fig_pie = px.pie(
            df_comp,
            names="component",
            values="percentage",
            title=f"Elemental / Oxide Fractions for {selected_material}",
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_pie.update_layout(height=320, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No detailed compositional breakdown tabulated for this entry.")

with col_info2:
    st.markdown("### ⚙️ Measured Properties (Standard SI Units)")
    if not df_prop.empty:
        st.dataframe(df_prop[["Property", "Standard SI Measurement", "Reported Value", "Category", "Source", "Paper ID"]], use_container_width=True, hide_index=True)
    else:
        st.info("No experimental properties linked to this entry.")

st.markdown("---")
st.markdown("### 📚 Source Research Papers & Tables")
if not df_knowledge.empty:
    sources = df_knowledge[["paper_id", "doi", "table_id"]].drop_duplicates()
    for _, s in sources.iterrows():
        st.markdown(f"• **Paper:** `{s['paper_id']}` | **DOI:** [`{s['doi']}`](https://doi.org/{s['doi']}) | **Table:** `{s['table_id']}`")
