"""
Paper Explorer Page: Multi-Paper Table Extraction, Batch Exploration, and Cleaned CSV Exporter.
"""

import streamlit as st
import os
import sys
import pandas as pd
import json
import io
import zipfile
import datetime

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, APP_DIR)

from components.db_utils import get_all_papers, get_tables_for_paper, get_tables_for_papers, query_df

st.set_page_config(page_title="Paper Explorer | CrystaGraph", page_icon="📄", layout="wide")

st.title("📄 Scientific Paper & Multi-Table Explorer")
st.caption("Select multiple research papers, inspect extracted table structures, and batch download all cleaned CSV tables in one click.")

papers_df = get_all_papers()
if papers_df.empty:
    st.warning("No papers found in database. Please run the processing pipeline first.")
    st.stop()

# Helper function to generate Zip file of all cleaned tables
def create_tables_zip(selected_papers_df, selected_tables_df):
    """Creates an in-memory zip file containing all cleaned CSV tables and a manifest index."""
    zip_buffer = io.BytesIO()
    manifest_records = []
    
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for _, tbl in selected_tables_df.iterrows():
            paper_info = selected_papers_df[selected_papers_df["paper_id"] == tbl["paper_id"]]
            paper_title = paper_info["title"].values[0] if not paper_info.empty else "Unknown"
            doi = paper_info["doi"].values[0] if not paper_info.empty else "N/A"
            
            cleaned_rows = json.loads(tbl["cleaned_data_json"]) if tbl["cleaned_data_json"] else []
            df_cleaned = pd.DataFrame(cleaned_rows)
            csv_str = df_cleaned.to_csv(index=False)
            
            safe_paper_id = tbl["paper_id"].replace("/", "_")
            csv_filename = f"{safe_paper_id}_{tbl['table_id']}_cleaned.csv"
            
            # Add CSV to zip
            zip_file.writestr(f"cleaned_tables/{csv_filename}", csv_str)
            
            # Record in manifest
            manifest_records.append({
                "paper_id": tbl["paper_id"],
                "paper_title": paper_title,
                "doi": doi,
                "table_id": tbl["table_id"],
                "caption": tbl["caption"],
                "num_rows": tbl["num_rows"],
                "num_cols": tbl["num_cols"],
                "footnote": tbl["footnote"],
                "csv_file": csv_filename
            })
            
        # Add manifest CSV
        df_manifest = pd.DataFrame(manifest_records)
        zip_file.writestr("manifest_tables_index.csv", df_manifest.to_csv(index=False))
        
        # Add README in zip
        readme_content = f"""CrystaGraph Cleaned Tables Export
Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Papers Selected: {len(selected_papers_df)}
Total Tables Exported: {len(selected_tables_df)}

Directory Structure:
- manifest_tables_index.csv : Summary metadata index of all tables and paper sources
- cleaned_tables/           : Individual sanitized CSV files for each extracted table
"""
        zip_file.writestr("README.txt", readme_content)
        
    zip_buffer.seek(0)
    return zip_buffer.getvalue()

# Helper function to generate Master Merged CSV
def create_master_merged_csv(selected_papers_df, selected_tables_df):
    """Concatenates all cleaned tables into a unified dataframe with lineage metadata."""
    merged_rows = []
    for _, tbl in selected_tables_df.iterrows():
        paper_info = selected_papers_df[selected_papers_df["paper_id"] == tbl["paper_id"]]
        paper_title = paper_info["title"].values[0] if not paper_info.empty else "Unknown"
        doi = paper_info["doi"].values[0] if not paper_info.empty else "N/A"
        
        cleaned_rows = json.loads(tbl["cleaned_data_json"]) if tbl["cleaned_data_json"] else []
        for row_idx, row_dict in enumerate(cleaned_rows, start=1):
            record = {
                "paper_id": tbl["paper_id"],
                "paper_title": paper_title,
                "doi": doi,
                "table_id": tbl["table_id"],
                "table_caption": tbl["caption"],
                "table_footnote": tbl["footnote"],
                "row_index": row_idx
            }
            # Append all table column values
            for col_k, col_v in row_dict.items():
                record[f"col_{col_k}"] = col_v
            merged_rows.append(record)
            
    df_merged = pd.DataFrame(merged_rows)
    return df_merged.to_csv(index=False).encode('utf-8')

# View Mode Selection
mode = st.radio(
    "Explore Mode:",
    ["📚 Multi-Paper Batch Table Miner (Select Multiple Papers & Download Cleaned CSVs)", "🔍 Single Paper Deep Dive"],
    horizontal=True
)

st.markdown("---")

if mode.startswith("📚 Multi-Paper"):
    st.subheader("📚 Select Papers & Batch Extract Cleaned Tables")
    st.caption("Select one or more research papers to extract and download all their cleaned CSV tables in a single batch package.")

    all_paper_ids = papers_df["paper_id"].tolist()
    paper_title_map = {row["paper_id"]: f"{row['paper_id']} — {row['title'][:70]}..." for _, row in papers_df.iterrows()}

    # Action buttons for quick select
    c_btn1, c_btn2, c_space = st.columns([1.2, 1.2, 4])
    with c_btn1:
        if st.button("✅ Select All Papers", use_container_width=True):
            st.session_state["selected_multi_papers"] = all_paper_ids
            st.rerun()
    with c_btn2:
        if st.button("❌ Clear Selection", use_container_width=True):
            st.session_state["selected_multi_papers"] = []
            st.rerun()

    if "selected_multi_papers" not in st.session_state:
        st.session_state["selected_multi_papers"] = all_paper_ids[:3]

    selected_paper_ids = st.multiselect(
        "Choose Research Papers to Extract Tables From:",
        options=all_paper_ids,
        default=st.session_state["selected_multi_papers"],
        format_func=lambda x: paper_title_map.get(x, x),
        help="You can select multiple papers from the list"
    )
    st.session_state["selected_multi_papers"] = selected_paper_ids

    if not selected_paper_ids:
        st.info("ℹ️ Please select at least one paper above to view and download its extracted tables.")
        st.stop()

    # Query tables for selected papers
    selected_papers_subset = papers_df[papers_df["paper_id"].isin(selected_paper_ids)]
    batch_tables_df = get_tables_for_papers(selected_paper_ids)

    # Compute aggregate stats
    total_tables_count = len(batch_tables_df)
    total_rows_count = int(batch_tables_df["num_rows"].sum()) if not batch_tables_df.empty else 0

    # Summary KPI banner
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    kpi_col1.metric("Selected Papers", len(selected_paper_ids))
    kpi_col2.metric("Cleaned Tables Extracted", total_tables_count)
    kpi_col3.metric("Total Tabular Rows", total_rows_count)

    if batch_tables_df.empty:
        st.warning("⚠️ No tables were found for the selected papers.")
        st.stop()

    st.markdown("### 📥 Batch Cleaned CSV Download Options")
    st.caption("Download all cleaned tables across the selected papers in your preferred format:")

    # Generate Export Buffers
    zip_bytes = create_tables_zip(selected_papers_subset, batch_tables_df)
    master_csv_bytes = create_master_merged_csv(selected_papers_subset, batch_tables_df)

    d_col1, d_col2 = st.columns(2)
    with d_col1:
        st.download_button(
            label=f"📦 Download All {total_tables_count} Cleaned Tables (.ZIP Archive)",
            data=zip_bytes,
            file_name=f"CrystaGraph_Cleaned_Tables_{len(selected_paper_ids)}_Papers.zip",
            mime="application/zip",
            type="primary",
            use_container_width=True,
            help="Contains individual cleaned CSV files for each table + manifest metadata index."
        )
    with d_col2:
        st.download_button(
            label=f"📊 Download Master Consolidated CSV ({total_rows_count} Rows)",
            data=master_csv_bytes,
            file_name=f"CrystaGraph_Consolidated_Tables_{len(selected_paper_ids)}_Papers.csv",
            mime="text/csv",
            type="secondary",
            use_container_width=True,
            help="Single CSV concatenating all table rows with paper title, DOI, and table captions."
        )

    st.markdown("---")
    st.subheader(f"📋 Extracted Tables Preview ({total_tables_count} tables from {len(selected_paper_ids)} papers)")

    # Group by Paper for organized inspection
    for p_id in selected_paper_ids:
        p_row = selected_papers_subset[selected_papers_subset["paper_id"] == p_id].iloc[0]
        p_tables = batch_tables_df[batch_tables_df["paper_id"] == p_id]

        with st.expander(f"📄 **{p_id}**: {p_row['title']} ({len(p_tables)} Tables)", expanded=True):
            st.markdown(f"**DOI:** [`{p_row['doi']}`](https://doi.org/{p_row['doi']}) | **Source File:** `{p_row['source_file']}`")
            
            if p_tables.empty:
                st.caption("No tables found for this paper.")
            else:
                for _, tbl in p_tables.iterrows():
                    st.markdown(f"##### 📌 **{tbl['table_id']}**: {tbl['caption'] or 'Untitled Table'} `({tbl['num_rows']} rows × {tbl['num_cols']} cols)`")
                    if tbl["footnote"]:
                        st.caption(f"📝 *Footnote / Conditions:* {tbl['footnote']}")

                    cleaned_rows = json.loads(tbl["cleaned_data_json"]) if tbl["cleaned_data_json"] else []
                    df_cleaned = pd.DataFrame(cleaned_rows)
                    st.dataframe(df_cleaned, use_container_width=True, hide_index=True)

                    # Individual Table Download Row
                    btn_c1, btn_c2, _ = st.columns([1.5, 1.5, 3])
                    with btn_c1:
                        table_csv = df_cleaned.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label=f"📥 Download {tbl['table_id']} CSV",
                            data=table_csv,
                            file_name=f"{p_id}_{tbl['table_id']}_cleaned.csv",
                            mime="text/csv",
                            key=f"multi_dl_csv_{p_id}_{tbl['table_id']}"
                        )
                    with btn_c2:
                        table_json = json.dumps(cleaned_rows, indent=2)
                        st.download_button(
                            label=f"📥 Download {tbl['table_id']} JSON",
                            data=table_json,
                            file_name=f"{p_id}_{tbl['table_id']}_cleaned.json",
                            mime="application/json",
                            key=f"multi_dl_json_{p_id}_{tbl['table_id']}"
                        )
                    st.markdown("---")

else:
    # Single Paper Deep Dive Mode
    paper_options = papers_df["paper_id"].tolist()
    selected_paper_id = st.selectbox(
        "Select a Research Paper:",
        paper_options,
        format_func=lambda x: f"{x} — {papers_df[papers_df['paper_id']==x]['title'].values[0][:75]}..."
    )

    paper_row = papers_df[papers_df["paper_id"] == selected_paper_id].iloc[0]

    # Display Paper Details
    col_meta1, col_meta2 = st.columns([2.5, 1])
    with col_meta1:
        st.markdown(f"### {paper_row['title']}")
        st.markdown(f"**DOI:** [`{paper_row['doi']}`](https://doi.org/{paper_row['doi']}) | **PII:** `{paper_row['pii']}`")
        st.markdown(f"**Source File:** `{paper_row['source_file']}`")

    with col_meta2:
        st.info(f"**Status:** {paper_row['status'].upper()} ✅\n\n**Format:** Elsevier / JATS XML")

    st.markdown("#### 📖 Abstract")
    st.write(paper_row['abstract'])

    st.markdown("---")
    st.subheader("📋 Extracted Tables in this Paper")

    tables_df = get_tables_for_paper(selected_paper_id)
    if tables_df.empty:
        st.info("No tables recorded for this paper.")
    else:
        # Batch download for this single paper
        single_paper_df = papers_df[papers_df["paper_id"] == selected_paper_id]
        zip_data = create_tables_zip(single_paper_df, tables_df)
        st.download_button(
            label=f"📦 Download All {len(tables_df)} Cleaned Tables for this Paper (.ZIP)",
            data=zip_data,
            file_name=f"{selected_paper_id}_all_cleaned_tables.zip",
            mime="application/zip",
            type="primary"
        )
        st.markdown("<br>", unsafe_allow_html=True)

        for _, tbl in tables_df.iterrows():
            with st.expander(f"📌 {tbl['table_id']}: {tbl['caption'] or 'Untitled Table'} ({tbl['num_rows']} rows × {tbl['num_cols']} cols)", expanded=True):
                if tbl["footnote"]:
                    st.caption(f"**Footnote/Conditions:** {tbl['footnote']}")
                
                # Load cleaned table
                cleaned_rows = json.loads(tbl["cleaned_data_json"]) if tbl["cleaned_data_json"] else []
                df_cleaned = pd.DataFrame(cleaned_rows)
                st.dataframe(df_cleaned, use_container_width=True, hide_index=True)

                # Show download options
                c_d1, c_d2 = st.columns(2)
                with c_d1:
                    csv_data = df_cleaned.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label=f"📥 Download {tbl['table_id']} as CSV",
                        data=csv_data,
                        file_name=f"{selected_paper_id}_{tbl['table_id']}_cleaned.csv",
                        mime="text/csv",
                        key=f"dl_csv_{selected_paper_id}_{tbl['table_id']}"
                    )
                with c_d2:
                    json_data = json.dumps(cleaned_rows, indent=2)
                    st.download_button(
                        label=f"📥 Download {tbl['table_id']} as JSON",
                        data=json_data,
                        file_name=f"{selected_paper_id}_{tbl['table_id']}_cleaned.json",
                        mime="application/json",
                        key=f"dl_json_{selected_paper_id}_{tbl['table_id']}"
                    )

