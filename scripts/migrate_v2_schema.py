"""
Database Migration Script for CrystaGraph V2 Web Platform.
Adds multi-user authentication, workspaces, background extraction jobs,
and academic correction audit trail tables to matgraph.db without disturbing
existing extracted research data.
"""

import os
import sqlite3
import hashlib
import uuid

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
DB_PATH = os.path.join(PROJECT_ROOT, "data/database/matgraph.db")

def hash_password(password: str) -> str:
    """Computes SHA-256 hash with salt for secure password storage."""
    salt = "crystagraph_academic_salt_2026"
    return hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

def migrate_database(db_path: str = DB_PATH):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    print(f"[Migration] Upgrading database schema at: {db_path}")

    # 1. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        hashed_password TEXT NOT NULL,
        full_name TEXT NOT NULL,
        institution TEXT DEFAULT 'BML Munjal University',
        department TEXT DEFAULT 'Computer Science & Engineering / Materials Informatics',
        role TEXT DEFAULT 'professor',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Workspaces Table
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

    # 3. Extraction Jobs (Background task tracker)
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

    # 4. User Corrections (Academic Audit Trail)
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

    # 5. Non-destructive column additions to existing tables
    tables_to_augment = ["papers", "tables", "materials", "compositions", "properties", "material_knowledge"]
    for table in tables_to_augment:
        for col, col_type in [("user_id", "TEXT"), ("is_verified", "INTEGER DEFAULT 1")]:
            try:
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type};")
            except sqlite3.OperationalError:
                pass  # column already exists

    # 6. Seed Default Professor Account for immediate zero-friction evaluation
    default_user_id = "user_prof_001"
    cursor.execute("SELECT user_id FROM users WHERE email = 'professor@bmu.edu.in';")
    if not cursor.fetchone():
        cursor.execute("""
        INSERT INTO users (user_id, email, hashed_password, full_name, institution, department, role)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (
            default_user_id,
            "professor@bmu.edu.in",
            hash_password("professor123"),
            "Dr. Soharab Hossain",
            "BML Munjal University",
            "School of Engineering & Technology",
            "professor"
        ))
        print(" -> Seeded default professor account: professor@bmu.edu.in / professor123")

        # Create default workspace
        cursor.execute("""
        INSERT OR REPLACE INTO workspaces (workspace_id, user_id, title, description)
        VALUES (?, ?, ?, ?);
        """, (
            "ws_default_01",
            default_user_id,
            "Advanced Materials & Alloys Lab",
            "Primary workspace for titanium alloys, battery cathodes, and piezoelectric ceramics research."
        ))

    conn.commit()
    conn.close()
    print("[Migration] V2 schema upgrade completed successfully.")

if __name__ == "__main__":
    migrate_database()
