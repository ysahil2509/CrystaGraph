"""
Database access and query utilities for the MatGraph Extractor Streamlit application.
Utilizes SQLite with pandas for fast querying and caching.
"""

import sqlite3
import pandas as pd
import json
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/database/matgraph.db"))

def get_connection():
    """Returns a connection to the SQLite database."""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at {DB_PATH}. Run scripts/process_papers.py first.")
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn

def query_df(sql: str, params: tuple = ()) -> pd.DataFrame:
    """Executes a SQL query and returns a pandas DataFrame."""
    conn = get_connection()
    try:
        df = pd.read_sql_query(sql, conn, params=params)
    finally:
        conn.close()
    return df

def get_dashboard_counts():
    """Returns total counts for dashboard cards."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("SELECT COUNT(*) FROM papers;")
        n_papers = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM tables;")
        n_tables = c.fetchone()[0]

        c.execute("SELECT COUNT(DISTINCT material_name) FROM materials;")
        n_materials = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM compositions;")
        n_compositions = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM properties;")
        n_properties = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM material_knowledge;")
        n_triples = c.fetchone()[0]

        c.execute("SELECT execution_time_sec, metrics_json FROM pipeline_logs ORDER BY log_id DESC LIMIT 1;")
        log_row = c.fetchone()
        exec_time = log_row[0] if log_row else 0.0
        metrics = json.loads(log_row[1]) if log_row and log_row[1] else {}
    finally:
        conn.close()

    return {
        "papers": n_papers,
        "tables": n_tables,
        "materials": n_materials,
        "compositions": n_compositions,
        "properties": n_properties,
        "triples": n_triples,
        "exec_time": exec_time,
        "metrics": metrics
    }

def get_all_papers() -> pd.DataFrame:
    return query_df("SELECT * FROM papers ORDER BY paper_id;")

def get_tables_for_paper(paper_id: str) -> pd.DataFrame:
    return query_df("SELECT * FROM tables WHERE paper_id = ? ORDER BY table_id;", (paper_id,))

def get_tables_for_papers(paper_ids: list) -> pd.DataFrame:
    """Returns all tables belonging to a list of paper IDs."""
    if not paper_ids:
        return pd.DataFrame()
    placeholders = ",".join(["?"] * len(paper_ids))
    return query_df(f"SELECT * FROM tables WHERE paper_id IN ({placeholders}) ORDER BY paper_id, table_id;", tuple(paper_ids))


def get_all_materials() -> pd.DataFrame:
    return query_df("""
    SELECT DISTINCT material_name, paper_id, table_id 
    FROM materials 
    ORDER BY material_name;
    """)

def search_knowledge(keyword: str = "", property_filter: str = "", category_filter: str = "") -> pd.DataFrame:
    """Searches linked material knowledge records with dynamic filters."""
    conditions = ["1=1"]
    params = []

    if keyword:
        conditions.append("(material_name LIKE ? OR composition_summary LIKE ? OR paper_id LIKE ? OR doi LIKE ?)")
        kw = f"%{keyword}%"
        params.extend([kw, kw, kw, kw])

    if property_filter:
        conditions.append("property_name = ?")
        params.append(property_filter)

    if category_filter and category_filter != "All":
        conditions.append("property_category = ?")
        params.append(category_filter)

    sql = f"""
    SELECT record_id, material_name, composition_summary, property_name, property_category, 
           value_numeric, value_raw, unit, si_value, si_unit, source_type,
           condition_footnote as condition, paper_id, doi, table_id, caption
    FROM material_knowledge
    WHERE {' AND '.join(conditions)}
    ORDER BY material_name, property_name;
    """
    return query_df(sql, tuple(params))

TOPIC_MAPPING = {
    "Titanium Aerospace Alloys": ["paper_01_ti_alloys"],
    "Lithium Battery Cathodes": ["paper_02_battery_cathodes"],
    "Perovskite Dielectrics & Piezoelectrics": ["paper_03_perovskite_dielectrics"],
    "High Entropy Alloys (HEAs)": ["paper_04_high_entropy_alloys"],
    "Bioactive Glasses & Bioceramics": ["paper_05_bioactive_glasses"],
    "High-Temperature Superconductors": ["paper_06_superconductors"],
    "Thermoelectric Energy Materials": ["paper_07_thermoelectrics"],
    "High-Strength Aerospace Aluminum": ["paper_08_aerospace_aluminum"],
    "Solid Oxide Fuel Cell (SOFC) Electrolytes": ["paper_09_sofc_electrolytes"],
    "Shape Memory Alloys (SMAs)": ["paper_10_shape_memory_alloys"]
}

def get_unified_materials_matrix(paper_ids: list = None) -> pd.DataFrame:
    """
    Returns consolidated material data across selected papers or all 10 papers in one view,
    including paper metadata, material name, composition, and standardized SI property units.
    """
    where_clause = ""
    params = ()
    if paper_ids:
        placeholders = ",".join(["?"] * len(paper_ids))
        where_clause = f"WHERE k.paper_id IN ({placeholders})"
        params = tuple(paper_ids)

    sql = f"""
    SELECT 
        p.title as "Paper Title",
        k.paper_id as "Paper ID",
        k.doi as "DOI",
        k.material_name as "Material / Alloy",
        k.composition_summary as "Composition Summary",
        k.property_name as "Property",
        k.property_category as "Category",
        k.value_raw as "Reported Value",
        k.unit as "Reported Unit",
        k.value_numeric as "Numeric Value",
        k.si_value as "SI Value",
        k.si_unit as "SI Unit",
        CASE 
            WHEN k.si_value IS NOT NULL AND k.si_unit != '' THEN PRINTF('%.2f %s', k.si_value, k.si_unit)
            ELSE k.value_raw 
        END as "Standardized SI Measurement",
        k.source_type as "Source Type",
        k.table_id as "Table/Section ID",
        k.condition_footnote as "Context / Notes"
    FROM material_knowledge k
    LEFT JOIN papers p ON k.paper_id = p.paper_id
    {where_clause}
    ORDER BY k.paper_id, k.material_name, k.property_name;
    """
    return query_df(sql, params)

def get_cross_paper_pivot(paper_ids: list = None, use_si: bool = True) -> pd.DataFrame:
    """
    Creates a cross-paper comparison pivot table:
    Rows = Material (with Paper ID)
    Columns = Standard Properties
    Values = Property value in SI units or reported units
    """
    df = get_unified_materials_matrix(paper_ids)
    if df.empty:
        return pd.DataFrame()

    val_col = "Standardized SI Measurement" if use_si else "Reported Value"
    # Deduplicate before pivot
    df_dedup = df.drop_duplicates(subset=["Material / Alloy", "Paper ID", "Property"])
    pivot = df_dedup.pivot(
        index=["Material / Alloy", "Paper ID", "Composition Summary"],
        columns="Property",
        values=val_col
    ).fillna("-").reset_index()
    return pivot

