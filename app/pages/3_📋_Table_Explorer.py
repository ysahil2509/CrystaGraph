"""
Table Explorer Page: Interactive inspection of Raw vs Cleaned tables, captions, footnotes, dimensions, and multi-table batch export.
"""

import streamlit as st
import os
import sys
import pandas as pd
import json
import io
import zipfile

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, APP_DIR)

from components.db_utils import get_all_papers, get_tables_for_papers, query_df

st.set_page_config(page_title="Table Explorer | CrystaGraph", page_icon="📋", layout="wide")

st.title("📋 Scientific Table Explorer")
st.caption("Deep-dive inspection comparing Raw vs Preprocessed tables, captions, spans, notes, with multi-paper batch export.")

papers_df = get_all_papers()
if papers_df.empty:
    st.warning("No papers available in the database.")
    st.stop()

# Helper for zip creation
def create_batch_tables_zip(tables_records):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for tbl in tables_records:
            cleaned_rows = json.loads(tbl["cleaned_data_json"]) if tbl["cleaned_data_json"] else []
            df = pd.DataFrame(cleaned_rows)
            csv_str = df.to_csv(index=False)
            safe_paper_id = tbl["paper_id"].replace("/", "_")
            zip_file.writestr(f"{safe_paper_id}_{tbl['table_id']}_cleaned.csv", csv_str)
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

# Filter Controls
col_sel1, col_sel2 = st.columns([1.2, 1])

all_paper_ids = papers_df["paper_id"].tolist()
with col_sel1:
    selected_papers = st.multiselect(
        "Select Paper(s):",
        options=all_paper_ids,
        default=[all_paper_ids[0]],
        help="Choose one or more papers to view their extracted tables."
    )

if not selected_papers:
    st.info("Please select at least one paper.")
    st.stop()

tables_df = get_tables_for_papers(selected_papers)
if tables_df.empty:
    st.warning("No tables found for selected paper(s).")
    st.stop()

with col_sel2:
    table_options = ["All Tables"] + [f"{row['paper_id']} | {row['table_id']}" for _, row in tables_df.iterrows()]
    selected_table_view = st.selectbox("Select Table View:", table_options)

# Action bar for batch download
st.markdown("---")
b_c1, b_c2, b_c3 = st.columns([2, 2, 2])
b_c1.metric("Selected Papers", len(selected_papers))
b_c2.metric("Available Tables", len(tables_df))
b_c3.metric("Total Extracted Rows", int(tables_df["num_rows"].sum()))

# Batch download of all cleaned tables for selected papers
zip_data = create_batch_tables_zip(tables_df.to_dict(orient="records"))
st.download_button(
    label=f"📦 Download All {len(tables_df)} Cleaned CSV Tables as ZIP",
    data=zip_data,
    file_name=f"Cleaned_Tables_{len(selected_papers)}_Papers.zip",
    mime="application/zip",
    type="primary",
    help="Download all cleaned tables from the selected papers as individual CSVs in a ZIP."
)

st.markdown("---")

# Display Tables
if selected_table_view != "All Tables":
    p_id_sel, t_id_sel = selected_table_view.split(" | ")
    active_tables = tables_df[(tables_df["paper_id"] == p_id_sel) & (tables_df["table_id"] == t_id_sel)]
else:
    active_tables = tables_df

for _, tbl in active_tables.iterrows():
    with st.expander(f"📌 [{tbl['paper_id']}] {tbl['table_id']}: {tbl['caption'] or 'Untitled Table'} ({tbl['num_rows']} rows × {tbl['num_cols']} cols)", expanded=(len(active_tables) == 1)):
        if tbl["footnote"]:
            st.info(f"📝 **Table Footnote / Conditions:** {tbl['footnote']}")

        # Tabs for Cleaned Table, Raw Table, and Extracted Entities
        tab1, tab2, tab3 = st.tabs(["✨ Cleaned Table", "🔍 Raw Extracted Table", "🧬 Extracted Knowledge Entities"])

        with tab1:
            cleaned_rows = json.loads(tbl["cleaned_data_json"]) if tbl["cleaned_data_json"] else []
            df_cleaned = pd.DataFrame(cleaned_rows)
            st.dataframe(df_cleaned, use_container_width=True, hide_index=True)
            
            # Download Button
            st.download_button(
                label=f"📥 Download Cleaned CSV ({tbl['table_id']})",
                data=df_cleaned.to_csv(index=False).encode('utf-8'),
                file_name=f"{tbl['paper_id']}_{tbl['table_id']}_cleaned.csv",
                mime="text/csv",
                key=f"te_dl_csv_{tbl['paper_id']}_{tbl['table_id']}"
            )

        with tab2:
            raw_rows = json.loads(tbl["raw_data_json"]) if tbl["raw_data_json"] else []
            df_raw = pd.DataFrame(raw_rows)
            st.dataframe(df_raw, use_container_width=True, hide_index=True)

        with tab3:
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                st.markdown("#### 🧪 Composition Extractions")
                df_comp = query_df("SELECT material_name, component, percentage, unit FROM compositions WHERE paper_id = ? AND table_id = ?;", (tbl['paper_id'], tbl['table_id']))
                if not df_comp.empty:
                    st.dataframe(df_comp, use_container_width=True, hide_index=True)
                else:
                    st.caption("No composition records directly mapped to this table.")

            with col_e2:
                st.markdown("#### ⚙️ Property Extractions")
                df_prop = query_df("SELECT material_name, property_name, value_raw, unit FROM properties WHERE paper_id = ? AND table_id = ?;", (tbl['paper_id'], tbl['table_id']))
                if not df_prop.empty:
                    st.dataframe(df_prop, use_container_width=True, hide_index=True)
                else:
                    st.caption("No property measurements directly mapped to this table.")

