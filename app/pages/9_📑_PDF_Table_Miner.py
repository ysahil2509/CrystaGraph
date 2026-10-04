"""
PDF Table Miner Page: Direct table extraction from scientific PDF papers.
"""

import streamlit as st
import os
import sys
import pandas as pd

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(CURRENT_DIR)
PROJECT_ROOT = os.path.dirname(APP_DIR)
sys.path.insert(0, APP_DIR)
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "downloading_and_preprocessing"))

from pdf_table_extractor import PDFTableExtractor

st.set_page_config(page_title="PDF Table Miner | CrystaGraph", page_icon="📑", layout="wide")

st.title("📑 Native PDF Research Paper Miner")
st.caption("Directly extract tabular matrices, column headers, and material entries from scientific PDF documents.")

extractor = PDFTableExtractor()

uploaded_pdf = st.file_uploader("Upload a Scientific PDF Paper:", type=["pdf"])

if uploaded_pdf is not None:
    temp_dir = os.path.join(PROJECT_ROOT, "data/temp_pdf")
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, uploaded_pdf.name)
    
    with open(temp_path, "wb") as f:
        f.write(uploaded_pdf.getbuffer())

    st.success(f"Uploaded `{uploaded_pdf.name}`. Parsing document layout and extracting table bounding boxes...")

    with st.spinner("Extracting tables using pdfplumber & PyMuPDF..."):
        tables = extractor.extract_tables_from_pdf(temp_path)

    if not tables:
        st.warning("No structured tables were automatically detected in this PDF. Ensure the PDF contains digital (non-scanned) table lines.")
    else:
        st.success(f"🎉 Successfully detected and extracted **{len(tables)} table(s)** from `{uploaded_pdf.name}`!")

        for idx, tbl in enumerate(tables):
            with st.expander(f"📌 {tbl['table_id']}: {tbl['caption']} ({tbl['num_rows']} rows × {tbl['num_cols']} cols)", expanded=True):
                df_tbl = tbl["cleaned_df"]
                st.dataframe(df_tbl, use_container_width=True, hide_index=True)

                csv_data = df_tbl.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=f"📥 Download Extracted Table as CSV",
                    data=csv_data,
                    file_name=f"{tbl['table_id']}.csv",
                    mime="text/csv",
                    key=f"dl_pdf_tbl_{idx}"
                )
else:
    st.info("💡 Upload any scientific research paper in PDF format to test real-time native PDF table mining.")
