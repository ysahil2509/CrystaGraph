"""
Production Render Server Entrypoint for CrystaGraph FastAPI Backend.
Handles environment detection, PostgreSQL schema initialization, port binding, and Uvicorn ASGI startup.
"""

import os
import sys
import uvicorn

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CURRENT_DIR)
sys.path.insert(0, os.path.join(CURRENT_DIR, "app"))

from app.components.db_utils import get_connection, get_database_url

def main():
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    print("=" * 70)
    print("🚀 STARTING CRYSTAGRAPH API PRODUCTION SERVER")
    print("=" * 70)
    
    db_url = get_database_url()
    if db_url:
        print("[Database] PostgreSQL DATABASE_URL detected. Connecting to managed Postgres...")
    else:
        print("[Database] No DATABASE_URL detected. Using local SQLite database...")
        
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM papers;")
        n_papers = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM users;")
        n_users = c.fetchone()[0]
        print(f"[Database Health] Connected! Repository has {n_papers} papers and {n_users} registered users.")
        conn.close()
    except Exception as e:
        print(f"[Database Warning]: {e}")

    print(f"[Server] Listening on http://{host}:{port}")
    uvicorn.run("app.api:app", host=host, port=port, log_level="info")

if __name__ == "__main__":
    main()
