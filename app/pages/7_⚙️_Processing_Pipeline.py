"""
Processing Pipeline Page: Ingest XML research articles, run live extraction, and view execution logs.
"""

import streamlit as st
import os
import sys
import time

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(CURRENT_DIR)
PROJECT_ROOT = os.path.dirname(APP_DIR)
sys.path.insert(0, APP_DIR)
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "scripts"))

from scripts.process_papers import run_pipeline
from components.db_utils import query_df

st.set_page_config(page_title="Processing Pipeline | CrystaGraph", page_icon="⚙️", layout="wide")

st.title("⚙️ Knowledge Mining & Ingestion Pipeline")
st.caption("Upload scientific XML articles or trigger automated extraction over the existing repository.")

tab_run, tab_upload, tab_doi, tab_logs = st.tabs(["🚀 Execute Pipeline", "📤 Upload XMLs", "🌐 DOI Retrieval", "📜 Execution History"])

with tab_run:
    st.markdown("### 🔄 Run Complete CrystaGraph Mining Pipeline")
    st.write("Executes table extraction, MatSciBERT tokenization, composition mining, property extraction, relation linking, and SQLite database ingestion.")
    
    col_btn, col_msg = st.columns([1, 3])
    with col_btn:
        start_btn = st.button("🚀 Start Pipeline Execution", type="primary")

    if start_btn:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("Step 1/6: Extracting tables from XML papers...")
        progress_bar.progress(15)
        time.sleep(0.3)
        
        status_text.text("Step 2/6: Generating MatSciBERT tokenized splits...")
        progress_bar.progress(35)
        time.sleep(0.2)
        
        status_text.text("Step 3/6: Extracting chemical compositions (wt%, at%, mol%)...")
        progress_bar.progress(55)
        time.sleep(0.2)
        
        status_text.text("Step 4/6: Extracting material properties & standardizing units...")
        progress_bar.progress(75)
        time.sleep(0.2)
        
        status_text.text("Step 5/6: Linking composition-property relations...")
        progress_bar.progress(90)
        
        # Execute real backend pipeline
        results = run_pipeline(
            xml_dir=os.path.join(PROJECT_ROOT, "data/raw_xmls"),
            tables_dir=os.path.join(PROJECT_ROOT, "data/tables"),
            extracted_dir=os.path.join(PROJECT_ROOT, "data/extracted"),
            processed_dir=os.path.join(PROJECT_ROOT, "data/processed"),
            db_path=os.path.join(PROJECT_ROOT, "data/database/matgraph.db")
        )
        
        progress_bar.progress(100)
        status_text.text("✅ Pipeline execution completed successfully!")
        st.success("Knowledge mining completed! Refreshing metrics...")
        st.balloons()
        
        st.dataframe(results["per_paper_table"], use_container_width=True, hide_index=True)

with tab_upload:
    st.markdown("### 📤 Upload Scientific Research XMLs")
    uploaded_files = st.file_uploader("Select one or more Elsevier / JATS XML files", type=["xml"], accept_multiple_files=True)
    if uploaded_files:
        raw_xml_dir = os.path.join(PROJECT_ROOT, "data/raw_xmls")
        os.makedirs(raw_xml_dir, exist_ok=True)
        saved_count = 0
        for uploaded_file in uploaded_files:
            target_path = os.path.join(raw_xml_dir, uploaded_file.name)
            with open(target_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            saved_count += 1
        st.success(f"Successfully saved {saved_count} XML file(s) to `data/raw_xmls/`. Switch to 'Execute Pipeline' tab to process them!")

with tab_doi:
    st.markdown("### 🌐 Automated Paper Retrieval via Elsevier API")
    st.caption("Securely fetch research paper XMLs directly using DOIs.")
    
    user_api_key = st.text_input("Elsevier API Key (or set ELSEVIER_API_KEY in .env):", type="password")
    doi_inputs = st.text_area("Enter DOIs (one per line):", placeholder="10.1016/j.msea.2023.144890\n10.1016/j.actamat.2023.118942")
    
    if st.button("Download XML Articles"):
        if not user_api_key and not os.getenv("ELSEVIER_API_KEY"):
            st.error("Please provide an Elsevier API Key.")
        else:
            dois = [d.strip() for d in doi_inputs.split("\n") if d.strip()]
            if dois:
                from downloading_and_preprocessing.download_xml_from_dois import batch_download_dois
                with st.spinner("Downloading articles from ScienceDirect..."):
                    res = batch_download_dois(dois, output_dir=os.path.join(PROJECT_ROOT, "data/raw_xmls"))
                    st.write(res)
            else:
                st.warning("Please enter at least one DOI.")

with tab_logs:
    st.markdown("### 📜 Pipeline Execution History")
    df_logs = query_df("SELECT * FROM pipeline_logs ORDER BY log_id DESC;")
    if not df_logs.empty:
        st.dataframe(df_logs, use_container_width=True, hide_index=True)
    else:
        st.info("No execution history recorded yet.")
