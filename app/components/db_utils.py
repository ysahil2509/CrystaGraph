"""
Database access and query utilities for CrystaGraph.
Supports dual backends:
1. Production PostgreSQL (Render / Supabase / Neon / AWS RDS via DATABASE_URL)
2. Local embedded SQLite (matgraph.db) for zero-configuration local development.
"""

import os
import re
import json
import sqlite3
import pandas as pd
from typing import Optional, Any, List, Dict

try:
    import psycopg2
    from psycopg2 import sql as pg_sql
    from psycopg2.extras import RealDictCursor
    HAS_PSYCOPG2 = True
except ImportError:
    HAS_PSYCOPG2 = False

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/database/matgraph.db"))

def get_database_url() -> Optional[str]:
    """Retrieves and standardizes DATABASE_URL from environment."""
    url = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL")
    if url:
        url = url.strip()
        # SQLAlchemy & psycopg2 require postgresql:// rather than legacy postgres://
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
    return url

def adapt_sql_for_postgres(sql: str) -> str:
    """Adapts standard SQL / SQLite queries for PostgreSQL execution."""
    # 1. Adapt PRINTF to PostgreSQL string concatenation
    sql = re.sub(
        r"PRINTF\s*\(\s*['\"]%[.]2f\s+%s['\"]\s*,\s*([a-zA-Z0-9_.]+)\s*,\s*([a-zA-Z0-9_.]+)\s*\)",
        r"(ROUND(\1::numeric, 2)::text || ' ' || COALESCE(\2, ''))",
        sql,
        flags=re.IGNORECASE
    )
    
    # 2. Adapt INSERT OR REPLACE
    if "INSERT OR REPLACE INTO papers" in sql:
        sql = sql.replace("INSERT OR REPLACE INTO papers", "INSERT INTO papers")
        if "ON CONFLICT" not in sql:
            sql = sql.rstrip("; \n") + " ON CONFLICT (paper_id) DO UPDATE SET title = EXCLUDED.title, abstract = EXCLUDED.abstract, status = EXCLUDED.status;"
    elif "INSERT OR REPLACE INTO tables" in sql:
        sql = sql.replace("INSERT OR REPLACE INTO tables", "INSERT INTO tables")
        if "ON CONFLICT" not in sql:
            sql = sql.rstrip("; \n") + " ON CONFLICT (paper_id, table_id) DO UPDATE SET caption = EXCLUDED.caption, cleaned_data_json = EXCLUDED.cleaned_data_json;"

    # 3. Adapt ? to %s parameter placeholders outside of quotes
    parts = sql.split("'")
    for i in range(0, len(parts), 2):
        parts[i] = parts[i].replace("?", "%s")
    sql = "'".join(parts)

    return sql


class PostgresCursorWrapper:
    """Wraps a psycopg2 cursor to provide standard DB-API & SQLite compatibility."""

    def __init__(self, raw_cursor):
        self._cursor = raw_cursor

    def execute(self, query: str, params: Any = None):
        adapted = adapt_sql_for_postgres(query)
        if params is not None:
            # Handle list params
            if isinstance(params, (list, tuple)):
                clean_params = tuple(params)
            else:
                clean_params = (params,)
            return self._cursor.execute(adapted, clean_params)
        return self._cursor.execute(adapted)

    def executemany(self, query: str, seq_of_parameters: List[Any]):
        adapted = adapt_sql_for_postgres(query)
        return self._cursor.executemany(adapted, seq_of_parameters)

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    def fetchmany(self, size=None):
        return self._cursor.fetchmany(size)

    @property
    def rowcount(self):
        return self._cursor.rowcount

    @property
    def description(self):
        return self._cursor.description

    def close(self):
        self._cursor.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class PostgresConnectionWrapper:
    """Wraps psycopg2 connection to mirror SQLite connection semantics."""

    def __init__(self, raw_conn):
        self._conn = raw_conn

    def cursor(self):
        return PostgresCursorWrapper(self._conn.cursor())

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()
        self.close()


_SCHEMA_INITIALIZED = False

def init_postgres_schema(conn):
    """Creates all required tables in PostgreSQL if they do not exist."""
    c = conn.cursor()
    
    # 1. PAPERS
    c.execute("""
    CREATE TABLE IF NOT EXISTS papers (
        paper_id VARCHAR(255) PRIMARY KEY,
        doi TEXT,
        pii TEXT,
        title TEXT,
        abstract TEXT,
        source_file TEXT,
        status TEXT
    );
    """)

    # 2. TABLES
    c.execute("""
    CREATE TABLE IF NOT EXISTS tables (
        table_id VARCHAR(255),
        paper_id VARCHAR(255),
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
    c.execute("""
    CREATE TABLE IF NOT EXISTS materials (
        material_id SERIAL PRIMARY KEY,
        material_name TEXT NOT NULL,
        normalized_name TEXT,
        paper_id VARCHAR(255),
        table_id VARCHAR(255),
        FOREIGN KEY (paper_id) REFERENCES papers(paper_id) ON DELETE CASCADE
    );
    """)

    # 4. COMPOSITIONS
    c.execute("""
    CREATE TABLE IF NOT EXISTS compositions (
        comp_id SERIAL PRIMARY KEY,
        material_name TEXT NOT NULL,
        component TEXT NOT NULL,
        percentage DOUBLE PRECISION,
        unit VARCHAR(100),
        paper_id VARCHAR(255),
        table_id VARCHAR(255),
        doi TEXT,
        FOREIGN KEY (paper_id) REFERENCES papers(paper_id) ON DELETE CASCADE
    );
    """)

    # 5. PROPERTIES
    c.execute("""
    CREATE TABLE IF NOT EXISTS properties (
        prop_id SERIAL PRIMARY KEY,
        material_name TEXT NOT NULL,
        property_name TEXT NOT NULL,
        property_category VARCHAR(100),
        value_numeric DOUBLE PRECISION,
        value_raw TEXT,
        unit VARCHAR(100),
        si_value DOUBLE PRECISION,
        si_unit VARCHAR(100),
        source_type VARCHAR(50) DEFAULT 'table',
        condition_footnote TEXT,
        paper_id VARCHAR(255),
        table_id VARCHAR(255),
        doi TEXT,
        FOREIGN KEY (paper_id) REFERENCES papers(paper_id) ON DELETE CASCADE
    );
    """)

    # 6. MATERIAL KNOWLEDGE
    c.execute("""
    CREATE TABLE IF NOT EXISTS material_knowledge (
        record_id SERIAL PRIMARY KEY,
        material_name TEXT NOT NULL,
        normalized_material TEXT,
        composition_summary TEXT,
        property_name TEXT NOT NULL,
        property_category VARCHAR(100),
        value_numeric DOUBLE PRECISION,
        value_raw TEXT,
        unit VARCHAR(100),
        si_value DOUBLE PRECISION,
        si_unit VARCHAR(100),
        source_type VARCHAR(50) DEFAULT 'table',
        condition_footnote TEXT,
        paper_id VARCHAR(255),
        doi TEXT,
        table_id VARCHAR(255),
        caption TEXT
    );
    """)

    # 7. PIPELINE LOGS
    c.execute("""
    CREATE TABLE IF NOT EXISTS pipeline_logs (
        log_id SERIAL PRIMARY KEY,
        execution_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        total_papers INTEGER,
        total_tables INTEGER,
        total_materials INTEGER,
        total_properties INTEGER,
        total_compositions INTEGER,
        execution_time_sec DOUBLE PRECISION,
        metrics_json TEXT
    );
    """)

    # 8. USERS (Multi-tenant Academic Auth)
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id VARCHAR(255) PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        hashed_password TEXT NOT NULL,
        full_name VARCHAR(255) NOT NULL,
        institution VARCHAR(255) DEFAULT 'BML Munjal University',
        department VARCHAR(255) DEFAULT 'Computer Science & Engineering',
        role VARCHAR(50) DEFAULT 'researcher',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 9. WORKSPACES
    c.execute("""
    CREATE TABLE IF NOT EXISTS workspaces (
        workspace_id VARCHAR(255) PRIMARY KEY,
        user_id VARCHAR(255) NOT NULL,
        title VARCHAR(255) NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );
    """)

    # 10. EXTRACTION JOBS
    c.execute("""
    CREATE TABLE IF NOT EXISTS extraction_jobs (
        job_id VARCHAR(255) PRIMARY KEY,
        user_id VARCHAR(255),
        paper_id VARCHAR(255),
        filename VARCHAR(255) NOT NULL,
        file_type VARCHAR(50) NOT NULL,
        status VARCHAR(50) NOT NULL DEFAULT 'pending',
        progress_pct INTEGER DEFAULT 0,
        current_step VARCHAR(255) DEFAULT 'Uploaded',
        extracted_tables_count INTEGER DEFAULT 0,
        extracted_compositions_count INTEGER DEFAULT 0,
        extracted_properties_count INTEGER DEFAULT 0,
        error_message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
    );
    """)

    # 11. USER CORRECTIONS
    c.execute("""
    CREATE TABLE IF NOT EXISTS user_corrections (
        correction_id SERIAL PRIMARY KEY,
        user_id VARCHAR(255) NOT NULL,
        paper_id VARCHAR(255) NOT NULL,
        table_id VARCHAR(255),
        record_type VARCHAR(50) NOT NULL,
        target_id VARCHAR(255),
        field_name VARCHAR(255) NOT NULL,
        original_value TEXT,
        corrected_value TEXT NOT NULL,
        academic_notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
    );
    """)

    conn.commit()

    # Seed initial papers and benchmark data from local SQLite if PostgreSQL is empty
    try:
        c.execute("SELECT COUNT(*) FROM papers;")
        row = c.fetchone()
        if row and row[0] == 0 and os.path.exists(DB_PATH):
            print("[Database] PostgreSQL is empty. Seeding initial benchmark knowledge from local SQLite...")
            seed_postgres_from_sqlite(conn)
    except Exception as e:
        print(f"[Database Seed Warning]: {e}")


def seed_postgres_from_sqlite(pg_conn):
    """Copies existing benchmark papers, tables, materials, and properties to PostgreSQL."""
    if not os.path.exists(DB_PATH):
        return

    sqlite_conn = sqlite3.connect(DB_PATH)
    pg_c = pg_conn.cursor()

    tables_to_copy = [
        ("papers", ["paper_id", "doi", "pii", "title", "abstract", "source_file", "status"]),
        ("tables", ["table_id", "paper_id", "caption", "footnote", "num_rows", "num_cols", "headers_json", "raw_data_json", "cleaned_data_json"]),
        ("materials", ["material_name", "normalized_name", "paper_id", "table_id"]),
        ("compositions", ["material_name", "component", "percentage", "unit", "paper_id", "table_id", "doi"]),
        ("properties", ["material_name", "property_name", "property_category", "value_numeric", "value_raw", "unit", "si_value", "si_unit", "source_type", "condition_footnote", "paper_id", "table_id", "doi"]),
        ("material_knowledge", ["material_name", "normalized_material", "composition_summary", "property_name", "property_category", "value_numeric", "value_raw", "unit", "si_value", "si_unit", "source_type", "condition_footnote", "paper_id", "doi", "table_id", "caption"]),
        ("users", ["user_id", "email", "hashed_password", "full_name", "institution", "department", "role", "created_at"]),
        ("workspaces", ["workspace_id", "user_id", "title", "description", "created_at"]),
    ]

    for tbl_name, cols in tables_to_copy:
        try:
            sql_lite = f"SELECT {', '.join(cols)} FROM {tbl_name};"
            rows = sqlite_conn.execute(sql_lite).fetchall()
            if rows:
                col_names = ", ".join(cols)
                placeholders = ", ".join(["%s"] * len(cols))
                insert_sql = f"INSERT INTO {tbl_name} ({col_names}) VALUES ({placeholders}) ON CONFLICT DO NOTHING;"
                pg_c.executemany(insert_sql, rows)
                pg_conn.commit()
                print(f"[Database Seed] Migrated {len(rows)} records into PostgreSQL table '{tbl_name}'.")
        except Exception as ex:
            print(f"[Database Seed Warning for {tbl_name}]: {ex}")

    sqlite_conn.close()


def get_connection():
    """Returns a connection to PostgreSQL (if DATABASE_URL is set) or SQLite."""
    global _SCHEMA_INITIALIZED
    db_url = get_database_url()

    if db_url and HAS_PSYCOPG2:
        raw_conn = psycopg2.connect(db_url)
        conn = PostgresConnectionWrapper(raw_conn)
        if not _SCHEMA_INITIALIZED:
            try:
                init_postgres_schema(conn)
                _SCHEMA_INITIALIZED = True
            except Exception as e:
                print(f"[PostgreSQL Schema Init Error]: {e}")
        return conn

    # Fallback to local SQLite
    if not os.path.exists(DB_PATH):
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn


def query_df(sql: str, params: tuple = ()) -> pd.DataFrame:
    """Executes a SQL query and returns a pandas DataFrame."""
    conn = get_connection()
    try:
        db_url = get_database_url()
        if db_url and HAS_PSYCOPG2:
            adapted_sql = adapt_sql_for_postgres(sql)
            df = pd.read_sql_query(adapted_sql, conn._conn, params=params)
        else:
            df = pd.read_sql_query(sql, conn, params=params)
    finally:
        conn.close()
    return df


def get_dashboard_counts() -> Dict[str, Any]:
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
    df_dedup = df.drop_duplicates(subset=["Material / Alloy", "Paper ID", "Property"])
    pivot = df_dedup.pivot(
        index=["Material / Alloy", "Paper ID", "Composition Summary"],
        columns="Property",
        values=val_col
    ).fillna("-").reset_index()
    return pivot
