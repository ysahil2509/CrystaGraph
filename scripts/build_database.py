"""
Database Creation and Ingestion Script for MatGraph Extractor.
Builds and populates SQLite database 'matgraph.db' with relational schema for papers, tables,
materials, compositions, properties, linked knowledge triples, and execution logs.
"""

import os
import sqlite3
import json
import pandas as pd
from typing import List, Dict, Any

DEFAULT_DB_PATH = "data/database/matgraph.db"

def init_database(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Initializes the SQLite schema with optimized indexes."""
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 1. PAPERS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS papers (
        paper_id TEXT PRIMARY KEY,
        doi TEXT,
        pii TEXT,
        title TEXT,
        abstract TEXT,
        source_file TEXT,
        status TEXT
    );
    """)

    # 2. TABLES
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tables (
        table_id TEXT,
        paper_id TEXT,
        caption TEXT,
        footnote TEXT,
        num_rows INTEGER,
        num_cols INTEGER,
        headers_json TEXT,
        raw_data_json TEXT,
        cleaned_data_json TEXT,
        PRIMARY KEY (paper_id, table_id),
        FOREIGN KEY (paper_id) REFERENCES papers(paper_id) ON DELETE CASCADE
    );
    """)

    # 3. MATERIALS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS materials (
        material_id INTEGER PRIMARY KEY AUTOINCREMENT,
        material_name TEXT NOT NULL,
        normalized_name TEXT,
        paper_id TEXT,
        table_id TEXT,
        FOREIGN KEY (paper_id) REFERENCES papers(paper_id) ON DELETE CASCADE
    );
    """)

    # 4. COMPOSITIONS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS compositions (
        comp_id INTEGER PRIMARY KEY AUTOINCREMENT,
        material_name TEXT NOT NULL,
        component TEXT NOT NULL,
        percentage REAL,
        unit TEXT,
        paper_id TEXT,
        table_id TEXT,
        doi TEXT,
        FOREIGN KEY (paper_id) REFERENCES papers(paper_id) ON DELETE CASCADE
    );
    """)

    # 5. PROPERTIES
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS properties (
        prop_id INTEGER PRIMARY KEY AUTOINCREMENT,
        material_name TEXT NOT NULL,
        property_name TEXT NOT NULL,
        property_category TEXT,
        value_numeric REAL,
        value_raw TEXT,
        unit TEXT,
        si_value REAL,
        si_unit TEXT,
        source_type TEXT DEFAULT 'table',
        condition_footnote TEXT,
        paper_id TEXT,
        table_id TEXT,
        doi TEXT,
        FOREIGN KEY (paper_id) REFERENCES papers(paper_id) ON DELETE CASCADE
    );
    """)

    # 6. MATERIAL KNOWLEDGE (Linked N-Tuples)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS material_knowledge (
        record_id INTEGER PRIMARY KEY AUTOINCREMENT,
        material_name TEXT NOT NULL,
        normalized_material TEXT,
        composition_summary TEXT,
        property_name TEXT NOT NULL,
        property_category TEXT,
        value_numeric REAL,
        value_raw TEXT,
        unit TEXT,
        si_value REAL,
        si_unit TEXT,
        source_type TEXT DEFAULT 'table',
        condition_footnote TEXT,
        paper_id TEXT,
        doi TEXT,
        table_id TEXT,
        caption TEXT
    );
    """)

    # Automatic non-destructive schema migrations for existing SQLite databases
    for col, col_type in [("si_value", "REAL"), ("si_unit", "TEXT"), ("source_type", "TEXT DEFAULT 'table'")]:
        try:
            cursor.execute(f"ALTER TABLE properties ADD COLUMN {col} {col_type};")
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute(f"ALTER TABLE material_knowledge ADD COLUMN {col} {col_type};")
        except sqlite3.OperationalError:
            pass

    # 7. PIPELINE LOGS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pipeline_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        execution_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        total_papers INTEGER,
        total_tables INTEGER,
        total_materials INTEGER,
        total_properties INTEGER,
        total_compositions INTEGER,
        execution_time_sec REAL,
        metrics_json TEXT
    );
    """)

    # 8. USERS (Multi-tenant Academic Auth)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        hashed_password TEXT NOT NULL,
        full_name TEXT NOT NULL,
        institution TEXT DEFAULT 'BML Munjal University',
        department TEXT DEFAULT 'Computer Science & Engineering',
        role TEXT DEFAULT 'professor',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 9. WORKSPACES
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS workspaces (
        workspace_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );
    """)

    # 10. EXTRACTION JOBS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS extraction_jobs (
        job_id TEXT PRIMARY KEY,
        user_id TEXT,
        paper_id TEXT,
        filename TEXT NOT NULL,
        file_type TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        progress_pct INTEGER DEFAULT 0,
        current_step TEXT DEFAULT 'Uploaded',
        extracted_tables_count INTEGER DEFAULT 0,
        extracted_compositions_count INTEGER DEFAULT 0,
        extracted_properties_count INTEGER DEFAULT 0,
        error_message TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        completed_at DATETIME,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
    );
    """)

    # 11. USER CORRECTIONS (Academic Audit Trail)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_corrections (
        correction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        paper_id TEXT NOT NULL,
        table_id TEXT,
        record_type TEXT NOT NULL,
        target_id TEXT,
        field_name TEXT NOT NULL,
        original_value TEXT,
        corrected_value TEXT NOT NULL,
        academic_notes TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
    );
    """)

    # Add user_id and is_verified to core tables if not already present
    for tbl in ["papers", "tables", "materials", "compositions", "properties", "material_knowledge"]:
        for col, col_type in [("user_id", "TEXT"), ("is_verified", "INTEGER DEFAULT 1")]:
            try:
                cursor.execute(f"ALTER TABLE {tbl} ADD COLUMN {col} {col_type};")
            except sqlite3.OperationalError:
                pass

    # Create Indexes for lightning-fast search in Streamlit
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_comp_mat ON compositions(material_name);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_comp_component ON compositions(component);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_prop_mat ON properties(material_name);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_prop_name ON properties(property_name);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_know_mat ON material_knowledge(material_name);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_know_prop ON material_knowledge(property_name);")

    conn.commit()
    return conn

def populate_database(
    papers_meta: List[Dict[str, Any]],
    tables_list: List[Dict[str, Any]],
    compositions: List[Dict[str, Any]],
    properties: List[Dict[str, Any]],
    linked_knowledge: List[Dict[str, Any]],
    metrics: Dict[str, Any],
    db_path: str = DEFAULT_DB_PATH
):
    """Inserts all extracted records into SQLite database within an atomic transaction."""
    conn = init_database(db_path)
    cursor = conn.cursor()

    # Clear existing data for fresh reload
    cursor.execute("DELETE FROM material_knowledge;")
    cursor.execute("DELETE FROM properties;")
    cursor.execute("DELETE FROM compositions;")
    cursor.execute("DELETE FROM materials;")
    cursor.execute("DELETE FROM tables;")
    cursor.execute("DELETE FROM papers;")

    # Insert Papers
    for p in papers_meta:
        cursor.execute("""
        INSERT OR REPLACE INTO papers (paper_id, doi, pii, title, abstract, source_file, status)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (
            p["paper_id"],
            p.get("doi", ""),
            p.get("pii", ""),
            p.get("title", ""),
            p.get("abstract", ""),
            p.get("filename", ""),
            p.get("status", "success")
        ))

    # Insert Tables
    for tbl in tables_list:
        cursor.execute("""
        INSERT OR REPLACE INTO tables (table_id, paper_id, caption, footnote, num_rows, num_cols, headers_json, raw_data_json, cleaned_data_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
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

    # Insert Unique Materials
    mat_set = set()
    for item in linked_knowledge:
        key = (item["material_name"], item["normalized_material"], item["paper_id"], item["table_id"])
        if key not in mat_set:
            mat_set.add(key)
            cursor.execute("""
            INSERT INTO materials (material_name, normalized_name, paper_id, table_id)
            VALUES (?, ?, ?, ?);
            """, key)

    # Insert Compositions
    for c in compositions:
        cursor.execute("""
        INSERT INTO compositions (material_name, component, percentage, unit, paper_id, table_id, doi)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (
            c["material_name"],
            c["component"],
            c.get("percentage"),
            c.get("unit", ""),
            c["paper_id"],
            c.get("table_id", ""),
            c.get("doi", "")
        ))

    # Insert Properties
    for pr in properties:
        cursor.execute("""
        INSERT INTO properties (material_name, property_name, property_category, value_numeric, value_raw, unit, si_value, si_unit, source_type, condition_footnote, paper_id, table_id, doi)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
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
            pr["paper_id"],
            pr.get("table_id", ""),
            pr.get("doi", "")
        ))

    # Insert Linked Knowledge
    for k in linked_knowledge:
        cursor.execute("""
        INSERT INTO material_knowledge (material_name, normalized_material, composition_summary, property_name, property_category, value_numeric, value_raw, unit, si_value, si_unit, source_type, condition_footnote, paper_id, doi, table_id, caption)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
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
            k["paper_id"],
            k.get("doi", ""),
            k.get("table_id", ""),
            k.get("caption", "")
        ))

    # Insert Pipeline Execution Log
    summary = metrics.get("summary_metrics", {})
    cursor.execute("""
    INSERT INTO pipeline_logs (total_papers, total_tables, total_materials, total_properties, total_compositions, execution_time_sec, metrics_json)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """, (
        summary.get("Total Papers Processed", 0),
        summary.get("Tables Successfully Extracted", 0),
        summary.get("Unique Materials Discovered", 0),
        summary.get("Total Property Measurements", 0),
        summary.get("Total Composition Entries", 0),
        summary.get("Total Pipeline Execution Time (s)", 0.0),
        json.dumps(summary)
    ))

    conn.commit()
    conn.close()
    print(f"[MatGraph Database] Successfully populated SQLite database at: {db_path}")

if __name__ == "__main__":
    init_database()
    print("Database schema created successfully.")
