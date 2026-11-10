"""
Background Execution Pipeline for CrystaGraph.
Coordinates table extraction (MIT XML & PDF), composition extraction,
property mining, SI standardization, entity linking, and atomic SQLite ingestion.
"""

import os
import sys
import json
import sqlite3
import traceback
from typing import Dict, Any, Optional, List

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, CURRENT_DIR)
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "downloading_and_preprocessing"))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "Matskraft_composition"))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "Matskraft_property"))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "Linking_the_extracted_info_and_final_evaluation"))

from components.db_utils import get_connection
from mit_table_extractor import MITTableExtractor
from pdf_table_extractor import PDFTableExtractor
from composition_extractor import CompositionExtractor
from property_extractor import PropertyExtractor
from text_property_extractor import TextPropertyExtractor
from linker import KnowledgeLinker


def update_job_status(
    job_id: str,
    status: str,
    progress_pct: int,
    current_step: str,
    tables_cnt: int = 0,
    comp_cnt: int = 0,
    prop_cnt: int = 0,
    error_msg: Optional[str] = None,
    paper_id: Optional[str] = None,
):
    """Updates extraction job status in SQLite database."""
    conn = get_connection()
    c = conn.cursor()
    try:
        completed_clause = ", completed_at = CURRENT_TIMESTAMP" if status in ["completed", "failed"] else ""
        paper_clause = ", paper_id = ?" if paper_id else ""
        params: List[Any] = [status, progress_pct, current_step, tables_cnt, comp_cnt, prop_cnt, error_msg]
        if paper_id:
            params.append(paper_id)
        params.append(job_id)

        c.execute(f"""
            UPDATE extraction_jobs
            SET status = ?,
                progress_pct = ?,
                current_step = ?,
                extracted_tables_count = ?,
                extracted_compositions_count = ?,
                extracted_properties_count = ?,
                error_message = ?
                {completed_clause}
                {paper_clause}
            WHERE job_id = ?;
        """, params)
        conn.commit()
    finally:
        conn.close()


def execute_extraction_pipeline(
    job_id: str,
    file_path: str,
    filename: str,
    file_type: str,
    user_id: Optional[str] = None,
    options: Optional[Dict[str, bool]] = None,
):
    """
    Executes complete asynchronous extraction pipeline for an uploaded document.
    """
    if options is None:
        options = {
            "extract_tables": True,
            "extract_compositions": True,
            "extract_properties": True,
            "extract_text": True,
            "normalize_si": True,
        }

    try:
        # Step 1: Initialize
        update_job_status(job_id, "processing", 15, "Parsing document structure & metadata...")

        paper_id = os.path.splitext(filename)[0]
        # Clean paper_id to safe alphanumeric with underscores
        paper_id = "".join([c if c.isalnum() or c in "_-" else "_" for c in paper_id]).lower()
        if not paper_id.startswith("paper_"):
            paper_id = f"paper_{paper_id}"

        paper_meta = {
            "paper_id": paper_id,
            "doi": "",
            "pii": "",
            "title": filename,
            "abstract": "",
            "filename": filename,
            "status": "success",
            "paragraphs": [],
        }
        tables = []

        if file_type.lower() == "xml":
            xml_extractor = MITTableExtractor()
            res = xml_extractor.parse_xml_file(file_path)
            if not res.get("success", False) and not res.get("tables"):
                raise ValueError(res.get("error", "Failed to parse XML document"))

            parsed_meta = res.get("metadata", {})
            paper_meta["doi"] = parsed_meta.get("doi") or f"10.1016/j.extracted.{job_id[:8]}"
            paper_meta["pii"] = parsed_meta.get("pii") or f"S{job_id[:12]}"
            paper_meta["title"] = parsed_meta.get("title") or filename
            paper_meta["abstract"] = parsed_meta.get("abstract") or ""
            paper_meta["paragraphs"] = res.get("paragraphs", [])

            raw_tables = res.get("tables", [])
            for idx, tbl in enumerate(raw_tables):
                t_id = tbl.get("table_id") or f"tbl_{idx+1:04d}"
                tables.append({
                    "paper_id": paper_id,
                    "table_id": t_id,
                    "doi": paper_meta["doi"],
                    "caption": tbl.get("caption", f"Extracted Table {idx+1}"),
                    "footnote": tbl.get("footnote", ""),
                    "headers": tbl.get("headers", []),
                    "num_rows": tbl.get("num_rows", len(tbl.get("rows", []))),
                    "num_cols": tbl.get("num_cols", len(tbl.get("headers", []))),
                    "raw_records": tbl.get("raw_records", tbl.get("rows", [])),
                    "cleaned_records": tbl.get("cleaned_records", tbl.get("rows", [])),
                })
        else:
            # PDF file
            pdf_extractor = PDFTableExtractor()
            pdf_tables = pdf_extractor.extract_tables_from_pdf(file_path)
            paper_meta["doi"] = f"10.1016/j.pdf.{job_id[:8]}"
            paper_meta["pii"] = f"S_PDF_{job_id[:10]}"
            paper_meta["title"] = os.path.splitext(filename)[0].replace("_", " ").title()

            for idx, pt in enumerate(pdf_tables):
                if "error" in pt:
                    continue
                tables.append({
                    "paper_id": paper_id,
                    "table_id": pt.get("table_id") or f"tbl_{idx+1:04d}",
                    "doi": paper_meta["doi"],
                    "caption": pt.get("caption", f"Table from {filename}"),
                    "footnote": pt.get("footnote", ""),
                    "headers": pt.get("headers", []),
                    "num_rows": pt.get("num_rows", len(pt.get("cleaned_records", []))),
                    "num_cols": pt.get("num_cols", len(pt.get("headers", []))),
                    "raw_records": pt.get("cleaned_records", []),
                    "cleaned_records": pt.get("cleaned_records", []),
                })

        # Step 2: Table extraction complete
        update_job_status(
            job_id,
            "processing",
            35,
            f"Extracted {len(tables)} tables. Extracting chemical compositions...",
            tables_cnt=len(tables),
            paper_id=paper_id,
        )

        # Step 3: Chemical Composition Extraction
        extracted_compositions = []
        if options.get("extract_compositions", True) and tables:
            comp_extractor = CompositionExtractor()
            extracted_compositions = comp_extractor.batch_extract(tables)

        update_job_status(
            job_id,
            "processing",
            55,
            f"Found {len(extracted_compositions)} composition records. Mining physical properties...",
            tables_cnt=len(tables),
            comp_cnt=len(extracted_compositions),
            paper_id=paper_id,
        )

        # Step 4: Material Property Extraction & SI Standardizations
        extracted_properties = []
        if options.get("extract_properties", True):
            if tables:
                prop_extractor = PropertyExtractor()
                table_properties = prop_extractor.batch_extract(tables)
                extracted_properties.extend(table_properties)

            if options.get("extract_text", True) and paper_meta.get("paragraphs"):
                text_extractor = TextPropertyExtractor()
                text_properties = text_extractor.batch_extract_from_papers([{
                    "paper_id": paper_id,
                    "doi": paper_meta["doi"],
                    "paragraphs": paper_meta["paragraphs"]
                }])
                extracted_properties.extend(text_properties)

        update_job_status(
            job_id,
            "processing",
            75,
            f"Extracted {len(extracted_properties)} property measurements. Linking knowledge triples...",
            tables_cnt=len(tables),
            comp_cnt=len(extracted_compositions),
            prop_cnt=len(extracted_properties),
            paper_id=paper_id,
        )

        # Step 5: Entity Linking
        linker = KnowledgeLinker()
        linked_knowledge = linker.link_extractions(
            extracted_compositions,
            extracted_properties,
            tables
        )

        update_job_status(
            job_id,
            "processing",
            90,
            f"Linked {len(linked_knowledge)} material knowledge records. Persisting to SQLite...",
            tables_cnt=len(tables),
            comp_cnt=len(extracted_compositions),
            prop_cnt=len(extracted_properties),
            paper_id=paper_id,
        )

        # Step 6: Database Ingestion
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # 1. Insert Paper
            cursor.execute("""
                INSERT OR REPLACE INTO papers (paper_id, doi, pii, title, abstract, source_file, status)
                VALUES (?, ?, ?, ?, ?, ?, ?);
            """, (
                paper_meta["paper_id"],
                paper_meta["doi"],
                paper_meta["pii"],
                paper_meta["title"],
                paper_meta["abstract"],
                filename,
                "success"
            ))

            # 2. Insert Tables
            for tbl in tables:
                cursor.execute("""
                    INSERT OR REPLACE INTO tables (
                        table_id, paper_id, caption, footnote, num_rows, num_cols,
                        headers_json, raw_data_json, cleaned_data_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    tbl["table_id"],
                    tbl["paper_id"],
                    tbl.get("caption", ""),
                    tbl.get("footnote", ""),
                    tbl.get("num_rows", 0),
                    tbl.get("num_cols", 0),
                    json.dumps(tbl.get("headers", [])),
                    json.dumps(tbl.get("raw_records", [])),
                    json.dumps(tbl.get("cleaned_records", []))
                ))

            # 3. Insert Unique Materials
            for item in linked_knowledge:
                cursor.execute("""
                    INSERT INTO materials (material_name, normalized_name, paper_id, table_id)
                    VALUES (?, ?, ?, ?);
                """, (
                    item["material_name"],
                    item.get("normalized_material", item["material_name"]),
                    paper_id,
                    item.get("table_id", "")
                ))

            # 4. Insert Compositions
            for c in extracted_compositions:
                cursor.execute("""
                    INSERT INTO compositions (material_name, component, percentage, unit, paper_id, table_id, doi)
                    VALUES (?, ?, ?, ?, ?, ?, ?);
                """, (
                    c["material_name"],
                    c["component"],
                    c.get("percentage"),
                    c.get("unit", ""),
                    paper_id,
                    c.get("table_id", ""),
                    paper_meta["doi"]
                ))

            # 5. Insert Properties
            for pr in extracted_properties:
                cursor.execute("""
                    INSERT INTO properties (
                        material_name, property_name, property_category, value_numeric,
                        value_raw, unit, si_value, si_unit, source_type, condition_footnote,
                        paper_id, table_id, doi
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    pr["material_name"],
                    pr["property_name"],
                    pr.get("property_category", "General"),
                    pr.get("value_numeric"),
                    pr.get("value_raw", ""),
                    pr.get("unit", ""),
                    pr.get("si_value"),
                    pr.get("si_unit", ""),
                    pr.get("source_type", "table"),
                    pr.get("condition_footnote", ""),
                    paper_id,
                    pr.get("table_id", ""),
                    paper_meta["doi"]
                ))

            # 6. Insert Linked Knowledge
            for k in linked_knowledge:
                cursor.execute("""
                    INSERT INTO material_knowledge (
                        material_name, normalized_material, composition_summary,
                        property_name, property_category, value_numeric, value_raw,
                        unit, si_value, si_unit, source_type, condition_footnote,
                        paper_id, doi, table_id, caption
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    k["material_name"],
                    k.get("normalized_material", ""),
                    k.get("composition_summary", ""),
                    k["property_name"],
                    k.get("property_category", "General"),
                    k.get("value_numeric"),
                    k.get("value_raw", ""),
                    k.get("unit", ""),
                    k.get("si_value"),
                    k.get("si_unit", ""),
                    k.get("source_type", "table"),
                    k.get("condition", ""),
                    paper_id,
                    paper_meta["doi"],
                    k.get("table_id", ""),
                    k.get("caption", "")
                ))

            conn.commit()
        finally:
            conn.close()

        # Step 7: Completed successfully
        update_job_status(
            job_id,
            "completed",
            100,
            "Knowledge extraction completed and ingested into repository.",
            tables_cnt=len(tables),
            comp_cnt=len(extracted_compositions),
            prop_cnt=len(extracted_properties),
            paper_id=paper_id,
        )

    except Exception as e:
        err_msg = f"{str(e)}\n{traceback.format_exc()}"
        print(f"[Pipeline Error on Job {job_id}]: {err_msg}")
        update_job_status(
            job_id,
            "failed",
            100,
            f"Error: {str(e)}",
            error_msg=str(e),
        )
