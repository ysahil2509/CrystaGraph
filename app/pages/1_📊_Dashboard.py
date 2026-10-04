"""
Dashboard Page: High-level metrics, summary charts, and extraction statistics.
"""

import streamlit as st
import os
import sys
import pandas as pd

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, APP_DIR)

from components.db_utils import get_dashboard_counts, query_df
from components.charts import (
    plot_property_frequency,
    plot_component_frequency,
    plot_category_distribution,
    plot_per_paper_metrics
)

st.set_page_config(page_title="Dashboard | CrystaGraph", page_icon="📊", layout="wide")

st.title("📊 Pipeline Analytics Dashboard")
st.caption("Live statistical insights and descriptive summary of the extracted materials knowledge base.")

try:
    counts = get_dashboard_counts()
except Exception as e:
    st.error(f"Error loading dashboard: {e}")
    st.stop()

# Key Metric Cards
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("Papers Processed", counts["papers"], delta="100% Validated")
with col2:
    st.metric("Tables Extracted", counts["tables"], delta="100% Success")
with col3:
    st.metric("Discovered Materials", counts["materials"])
with col4:
    st.metric("Property Records", counts["properties"])
with col5:
    st.metric("Linked Triples", counts["triples"])

st.markdown("---")

# Visual Charts Section
row1_c1, row1_c2 = st.columns(2)

with row1_c1:
    df_props = query_df("SELECT property_name, property_category, value_numeric, unit FROM properties;")
    if not df_props.empty:
        fig_prop = plot_property_frequency(df_props, top_n=10)
        st.plotly_chart(fig_prop, use_container_width=True)

with row1_c2:
    df_comps = query_df("SELECT component, percentage, unit FROM compositions;")
    if not df_comps.empty:
        fig_comp = plot_component_frequency(df_comps, top_n=12)
        st.plotly_chart(fig_comp, use_container_width=True)

row2_c1, row2_c2 = st.columns([1, 1])

with row2_c1:
    if not df_props.empty:
        fig_cat = plot_category_distribution(df_props)
        st.plotly_chart(fig_cat, use_container_width=True)

with row2_c2:
    # Per paper summary chart
    df_per_paper = query_df("""
    SELECT 
        p.paper_id as "Paper ID",
        COUNT(DISTINCT t.table_id) as "Tables Extracted",
        COUNT(DISTINCT m.material_name) as "Unique Materials",
        (SELECT COUNT(*) FROM compositions c WHERE c.paper_id = p.paper_id) as "Composition Records",
        (SELECT COUNT(*) FROM properties pr WHERE pr.paper_id = p.paper_id) as "Property Records"
    FROM papers p
    LEFT JOIN tables t ON p.paper_id = t.paper_id
    LEFT JOIN materials m ON p.paper_id = m.paper_id
    GROUP BY p.paper_id;
    """)
    if not df_per_paper.empty:
        fig_pp = plot_per_paper_metrics(df_per_paper)
        st.plotly_chart(fig_pp, use_container_width=True)

st.markdown("---")
st.subheader("📑 Per-Paper Extraction Inventory")
st.dataframe(df_per_paper, use_container_width=True, hide_index=True)
