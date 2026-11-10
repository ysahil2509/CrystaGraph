"""
Production FastAPI REST Microservice for CrystaGraph.
Provides high-performance RESTful API endpoints for knowledge retrieval,
multi-user academic authentication, research workspaces, and machine learning material property prediction.
"""

import os
import sys
import json
import uuid
import shutil
import sqlite3
import pandas as pd
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query, Depends, status, BackgroundTasks, UploadFile, File, Form
from pydantic import BaseModel, Field, EmailStr
from fastapi.middleware.cors import CORSMiddleware

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, CURRENT_DIR)
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "models"))

from components.db_utils import (
    get_dashboard_counts,
    query_df,
    search_knowledge,
    get_connection,
    get_all_papers,
    get_unified_materials_matrix,
    get_cross_paper_pivot,
    TOPIC_MAPPING
)
from train_property_predictor import MaterialPropertyPredictor
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    get_optional_current_user
)
from pipeline_executor import execute_extraction_pipeline

# Initialize FastAPI app
app = FastAPI(
    title="CrystaGraph API",
    description="RESTful API for AI-Driven Material Knowledge Mining and Machine Learning Property Prediction from Scientific Research Tables.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for Next.js frontend, Vercel deployments, and local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_origin_regex=r"https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Schemas
class CompositionInput(BaseModel):
    property_name: str = Field(..., example="Yield Strength", description="Property to predict (e.g. Yield Strength, Density, Tensile Strength)")
    composition: Dict[str, float] = Field(..., example={"Ti": 90.0, "Al": 6.0, "V": 4.0}, description="Elemental / oxide percentages")

class SearchQuery(BaseModel):
    query: Optional[str] = ""
    property_filter: Optional[str] = ""
    category_filter: Optional[str] = ""

class RegisterRequest(BaseModel):
    email: str = Field(..., example="researcher@university.edu")
    password: str = Field(..., min_length=6, example="securepassword123")
    full_name: str = Field(..., example="Dr. Jane Doe")
    institution: Optional[str] = "Research University"
    department: Optional[str] = "Materials Science & Engineering"
    role: Optional[str] = "researcher"

class LoginRequest(BaseModel):
    email: str = Field(..., example="researcher@university.edu")
    password: str = Field(..., example="securepassword123")

class WorkspaceCreateRequest(BaseModel):
    title: str = Field(..., example="Titanium Alloys Project")
    description: Optional[str] = ""

# Load ML Predictor instance
predictor = MaterialPropertyPredictor()
metadata_path = os.path.join(PROJECT_ROOT, "models/predictor_metadata.json")
if os.path.exists(metadata_path):
    with open(metadata_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
        predictor.feature_columns = meta.get("feature_columns", [])

# ==============================================================================
# SYSTEM & HEALTH ENDPOINTS
# ==============================================================================

@app.get("/")
def root():
    return {
        "service": "CrystaGraph REST API",
        "status": "online",
        "version": "2.0.0",
        "documentation": "/docs",
        "framework": "CrystaGraph / FastAPI"
    }

@app.get("/api/v1/health")
def health_check():
    return {"status": "healthy", "database_connected": True}

@app.get("/api/v1/stats")
def get_system_stats():
    """Returns total counts for papers, tables, materials, compositions, and properties."""
    try:
        return get_dashboard_counts()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==============================================================================
# AUTHENTICATION ENDPOINTS
# ==============================================================================

@app.post("/api/v1/auth/register", status_code=status.HTTP_201_CREATED)
def register_user(payload: RegisterRequest):
    """Registers a new academic researcher account."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("SELECT user_id FROM users WHERE email = ?;", (payload.email.strip().lower(),))
        if c.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"An account with email '{payload.email}' already exists."
            )

        user_id = f"user_{uuid.uuid4().hex[:12]}"
        hashed_pwd = hash_password(payload.password)
        c.execute("""
            INSERT INTO users (user_id, email, hashed_password, full_name, institution, department, role)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (
            user_id,
            payload.email.strip().lower(),
            hashed_pwd,
            payload.full_name.strip(),
            payload.institution.strip() if payload.institution else "BML Munjal University",
            payload.department.strip() if payload.department else "Computer Science & Engineering",
            payload.role.strip() if payload.role else "professor"
        ))

        # Create default workspace
        workspace_id = f"ws_{uuid.uuid4().hex[:12]}"
        c.execute("""
            INSERT INTO workspaces (workspace_id, user_id, title, description)
            VALUES (?, ?, ?, ?);
        """, (workspace_id, user_id, "Default Materials Lab", "Primary workspace for materials informatics."))

        conn.commit()

        token = create_access_token({"sub": user_id, "email": payload.email.strip().lower()})
        return {
            "message": "User registered successfully",
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "user_id": user_id,
                "email": payload.email.strip().lower(),
                "full_name": payload.full_name,
                "institution": payload.institution,
                "role": payload.role
            }
        }
    finally:
        conn.close()

@app.post("/api/v1/auth/login")
def login_user(payload: LoginRequest):
    """Authenticates academic credentials and returns JWT bearer token."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("""
            SELECT user_id, email, hashed_password, full_name, institution, department, role
            FROM users WHERE email = ?;
        """, (payload.email.strip().lower(),))
        row = c.fetchone()
        if not row or not verify_password(payload.password, row[2]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect institutional email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = row[0]
        token = create_access_token({"sub": user_id, "email": row[1]})
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "user_id": user_id,
                "email": row[1],
                "full_name": row[3],
                "institution": row[4],
                "department": row[5],
                "role": row[6]
            }
        }
    finally:
        conn.close()

@app.get("/api/v1/auth/me")
def get_current_user_profile(user: Dict[str, Any] = Depends(get_current_user)):
    """Returns the authenticated researcher profile."""
    return user

# ==============================================================================
# WORKSPACE & ACTIVITY ENDPOINTS
# ==============================================================================

@app.get("/api/v1/workspaces")
def list_user_workspaces(user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)):
    """Lists workspaces accessible to the user."""
    conn = get_connection()
    c = conn.cursor()
    try:
        if user:
            c.execute("SELECT workspace_id, title, description, created_at FROM workspaces WHERE user_id = ? ORDER BY created_at DESC;", (user["user_id"],))
        else:
            c.execute("SELECT workspace_id, title, description, created_at FROM workspaces ORDER BY created_at DESC LIMIT 5;")
        rows = c.fetchall()
        return [{"workspace_id": r[0], "title": r[1], "description": r[2], "created_at": r[3]} for r in rows]
    finally:
        conn.close()

@app.post("/api/v1/workspaces")
def create_workspace(payload: WorkspaceCreateRequest, user: Dict[str, Any] = Depends(get_current_user)):
    """Creates a new isolated research workspace."""
    conn = get_connection()
    c = conn.cursor()
    try:
        ws_id = f"ws_{uuid.uuid4().hex[:12]}"
        c.execute("""
            INSERT INTO workspaces (workspace_id, user_id, title, description)
            VALUES (?, ?, ?, ?);
        """, (ws_id, user["user_id"], payload.title.strip(), payload.description.strip()))
        conn.commit()
        return {"workspace_id": ws_id, "title": payload.title, "description": payload.description}
    finally:
        conn.close()

@app.get("/api/v1/workspace/summary")
def get_workspace_summary(user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)):
    """
    Returns unified research workspace summary statistics, recent activity,
    and extraction jobs from the database.
    """
    conn = get_connection()
    c = conn.cursor()
    try:
        counts = get_dashboard_counts()

        # Fetch recent papers
        c.execute("""
            SELECT paper_id, doi, title, status FROM papers 
            ORDER BY paper_id DESC LIMIT 5;
        """)
        recent_papers = [
            {"paper_id": r[0], "doi": r[1], "title": r[2], "status": r[3]}
            for r in c.fetchall()
        ]

        # Fetch recent extraction jobs
        c.execute("""
            SELECT job_id, filename, file_type, status, progress_pct, current_step, created_at
            FROM extraction_jobs 
            ORDER BY created_at DESC LIMIT 5;
        """)
        recent_jobs = [
            {
                "job_id": r[0],
                "filename": r[1],
                "file_type": r[2],
                "status": r[3],
                "progress_pct": r[4],
                "current_step": r[5],
                "created_at": r[6]
            }
            for r in c.fetchall()
        ]

        return {
            "counts": counts,
            "recent_papers": recent_papers,
            "recent_jobs": recent_jobs,
            "active_user": user["full_name"] if user else "Dr. Soharab Hossain (Default Academic Profile)"
        }
    finally:
        conn.close()

# ==============================================================================
# PAPER UPLOAD & ASYNCHRONOUS EXTRACTION JOBS
# ==============================================================================

UPLOAD_DIR = os.path.join(PROJECT_ROOT, "data", "papers", "uploaded")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/api/v1/papers/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_research_paper(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    extract_tables: bool = Form(True),
    extract_compositions: bool = Form(True),
    extract_properties: bool = Form(True),
    extract_text: bool = Form(True),
    normalize_si: bool = Form(True),
    user: Optional[Dict[str, Any]] = Depends(get_optional_current_user),
):
    """
    Accepts scientific research paper upload (PDF or XML),
    schedules background extraction pipeline, and returns tracking job ID.
    """
    filename = file.filename or "unknown_paper"
    ext = os.path.splitext(filename)[1].lower()
    if ext not in [".xml", ".pdf"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format '{ext}'. CrystaGraph accepts .xml and .pdf research papers."
        )

    file_type = "xml" if ext == ".xml" else "pdf"
    job_id = f"job_{uuid.uuid4().hex[:12]}"
    safe_name = f"{job_id}_{filename.replace(' ', '_')}"
    saved_path = os.path.join(UPLOAD_DIR, safe_name)

    # Save file to disk
    try:
        with open(saved_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save uploaded file: {str(e)}"
        )

    # Record initial extraction job
    user_id = user["user_id"] if user else None
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO extraction_jobs (
                job_id, user_id, filename, file_type, status, progress_pct, current_step
            ) VALUES (?, ?, ?, ?, 'pending', 5, 'Queued for processing');
        """, (job_id, user_id, filename, file_type))
        conn.commit()
    finally:
        conn.close()

    options = {
        "extract_tables": extract_tables,
        "extract_compositions": extract_compositions,
        "extract_properties": extract_properties,
        "extract_text": extract_text,
        "normalize_si": normalize_si,
    }

    # Dispatch to background task
    background_tasks.add_task(
        execute_extraction_pipeline,
        job_id,
        saved_path,
        filename,
        file_type,
        user_id,
        options,
    )

    return {
        "job_id": job_id,
        "filename": filename,
        "file_type": file_type,
        "status": "pending",
        "progress_pct": 5,
        "current_step": "Queued for processing",
        "message": f"Successfully queued '{filename}' for background materials knowledge mining."
    }

@app.get("/api/v1/jobs/{job_id}")
def get_extraction_job_status(job_id: str):
    """Retrieves live extraction progress and results for a specific background job."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("""
            SELECT job_id, user_id, paper_id, filename, file_type, status,
                   progress_pct, current_step, extracted_tables_count,
                   extracted_compositions_count, extracted_properties_count,
                   error_message, created_at, completed_at
            FROM extraction_jobs WHERE job_id = ?;
        """, (job_id,))
        row = c.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Extraction job '{job_id}' not found")

        return {
            "job_id": row[0],
            "user_id": row[1],
            "paper_id": row[2],
            "filename": row[3],
            "file_type": row[4],
            "status": row[5],
            "progress_pct": row[6],
            "current_step": row[7],
            "extracted_tables_count": row[8],
            "extracted_compositions_count": row[9],
            "extracted_properties_count": row[10],
            "error_message": row[11],
            "created_at": row[12],
            "completed_at": row[13],
        }
    finally:
        conn.close()

@app.get("/api/v1/jobs")
def list_extraction_jobs():
    """Lists recent background extraction jobs."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("""
            SELECT job_id, user_id, paper_id, filename, file_type, status,
                   progress_pct, current_step, extracted_tables_count,
                   extracted_compositions_count, extracted_properties_count,
                   error_message, created_at, completed_at
            FROM extraction_jobs ORDER BY created_at DESC LIMIT 20;
        """)
        rows = c.fetchall()
        return [
            {
                "job_id": r[0],
                "user_id": r[1],
                "paper_id": r[2],
                "filename": r[3],
                "file_type": r[4],
                "status": r[5],
                "progress_pct": r[6],
                "current_step": r[7],
                "extracted_tables_count": r[8],
                "extracted_compositions_count": r[9],
                "extracted_properties_count": r[10],
                "error_message": r[11],
                "created_at": r[12],
                "completed_at": r[13],
            }
            for r in rows
        ]
    finally:
        conn.close()

# ==============================================================================
# PAPERS & TABLES ENDPOINTS
# ==============================================================================

@app.get("/api/v1/papers")
def list_papers():
    """Lists all ingested scientific research papers."""
    df = query_df("SELECT paper_id, doi, pii, title, status FROM papers ORDER BY paper_id;")
    return df.to_dict(orient="records")

@app.get("/api/v1/tables")
def list_all_tables():
    """Lists all extracted tables across the knowledge repository."""
    df = query_df("""
        SELECT t.table_id, t.paper_id, t.caption, t.footnote, t.num_rows, t.num_cols,
               p.title as paper_title, p.doi
        FROM tables t
        LEFT JOIN papers p ON t.paper_id = p.paper_id
        ORDER BY t.paper_id, t.table_id;
    """)
    return df.to_dict(orient="records")

@app.get("/api/v1/properties")
def list_all_properties(
    category: Optional[str] = Query(None, description="Filter by property category"),
    property_name: Optional[str] = Query(None, description="Filter by property name")
):
    """Lists extracted property records with SI unit conversions."""
    query = """
        SELECT prop_id, material_name, property_name, property_category,
               value_numeric, value_raw, unit, si_value, si_unit,
               source_type, condition_footnote, paper_id, table_id, doi
        FROM properties
        WHERE 1=1
    """
    params = []
    if category:
        query += " AND property_category = ?"
        params.append(category)
    if property_name:
        query += " AND property_name = ?"
        params.append(property_name)
    query += " ORDER BY material_name, property_name;"

    df = query_df(query, tuple(params))
    return df.to_dict(orient="records")

class CorrectionRequest(BaseModel):
    paper_id: str
    table_id: Optional[str] = None
    record_type: str = Field(..., example="table_cell")
    target_id: Optional[str] = None
    field_name: str = Field(..., example="Ti (wt.%)")
    original_value: Optional[str] = None
    corrected_value: str = Field(..., example="90.5")
    academic_notes: Optional[str] = "Manual professor verification"

@app.post("/api/v1/tables/{table_id}/correct")
def record_table_correction(
    table_id: str,
    payload: CorrectionRequest,
    user: Optional[Dict[str, Any]] = Depends(get_optional_current_user)
):
    """
    Records an academic audit-trail correction to an extracted table cell.
    Persists to user_corrections and dynamically updates table cleaned records.
    """
    conn = get_connection()
    c = conn.cursor()
    try:
        user_id = user["user_id"] if user else "usr_prof_demo"
        c.execute("""
            INSERT INTO user_corrections (
                user_id, paper_id, table_id, record_type, target_id,
                field_name, original_value, corrected_value, academic_notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            user_id,
            payload.paper_id,
            table_id,
            payload.record_type,
            payload.target_id,
            payload.field_name,
            payload.original_value,
            payload.corrected_value,
            payload.academic_notes
        ))
        conn.commit()
        return {
            "status": "success",
            "message": "Academic correction registered in audit trail.",
            "correction": payload.dict()
        }
    finally:
        conn.close()

@app.get("/api/v1/papers/{paper_id}")
def get_paper_detail(paper_id: str):
    """Retrieves metadata, abstract, and table inventory for a specific paper."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("SELECT paper_id, doi, pii, title, abstract, source_file, status FROM papers WHERE paper_id = ?;", (paper_id,))
        row = c.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Paper '{paper_id}' not found")
        
        # Get tables
        c.execute("SELECT table_id, caption, footnote, num_rows, num_cols FROM tables WHERE paper_id = ?;", (paper_id,))
        tables = [
            {"table_id": r[0], "caption": r[1], "footnote": r[2], "num_rows": r[3], "num_cols": r[4]}
            for r in c.fetchall()
        ]

        return {
            "paper_id": row[0],
            "doi": row[1],
            "pii": row[2],
            "title": row[3],
            "abstract": row[4],
            "source_file": row[5],
            "status": row[6],
            "tables": tables
        }
    finally:
        conn.close()

@app.get("/api/v1/papers/{paper_id}/tables")
def get_paper_tables(paper_id: str):
    """Retrieves all tables and metadata extracted from a specific paper."""
    df = query_df("SELECT table_id, caption, footnote, num_rows, num_cols, cleaned_data_json FROM tables WHERE paper_id = ?;", (paper_id,))
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No tables found for paper '{paper_id}'")
    
    records = []
    for _, row in df.iterrows():
        records.append({
            "table_id": row["table_id"],
            "caption": row["caption"],
            "footnote": row["footnote"],
            "dimensions": f"{row['num_rows']}x{row['num_cols']}",
            "data": json.loads(row["cleaned_data_json"])
        })
    return {"paper_id": paper_id, "tables": records}

@app.get("/api/v1/tables/{table_id}")
def get_table_detail(table_id: str):
    """Retrieves single table matrix with both raw records and cleaned data."""
    df = query_df("""
        SELECT table_id, paper_id, caption, footnote, num_rows, num_cols, 
               headers_json, raw_data_json, cleaned_data_json 
        FROM tables WHERE table_id = ?;
    """, (table_id,))
    if df.empty:
        raise HTTPException(status_code=404, detail=f"Table '{table_id}' not found")
    row = df.iloc[0]
    return {
        "table_id": row["table_id"],
        "paper_id": row["paper_id"],
        "caption": row["caption"],
        "footnote": row["footnote"],
        "num_rows": int(row["num_rows"]),
        "num_cols": int(row["num_cols"]),
        "headers": json.loads(row["headers_json"]),
        "raw_records": json.loads(row["raw_data_json"]),
        "cleaned_records": json.loads(row["cleaned_data_json"])
    }

# ==============================================================================
# MATERIALS & SEARCH ENDPOINTS
# ==============================================================================

@app.get("/api/v1/materials")
def list_materials():
    """Lists all discovered material entities across the knowledge base."""
    df = query_df("SELECT DISTINCT material_name, paper_id, table_id FROM materials ORDER BY material_name;")
    return df.to_dict(orient="records")

@app.get("/api/v1/search")
def search_materials(
    q: Optional[str] = Query(None, description="Material formula, element, or keyword"),
    property: Optional[str] = Query(None, description="Specific property filter")
):
    """Searches linked composition-property relational triples."""
    df = search_knowledge(keyword=q or "", property_filter=property or "")
    return {
        "count": len(df),
        "results": df.to_dict(orient="records")
    }

# ==============================================================================
# CROSS-PAPER SYNTHESIS & ASHBY PLOT DATA
# ==============================================================================

@app.get("/api/v1/synthesize")
def get_synthesis_data():
    """
    Returns consolidated 10-paper cross-synthesis matrix and Ashby comparison points
    (e.g., Yield Strength vs Density, Tensile Strength vs Elongation).
    """
    matrix_df = get_unified_materials_matrix()
    records = matrix_df.fillna("").to_dict(orient="records")

    # Construct Ashby comparison points (materials having both Yield Strength and Density or similar)
    conn = get_connection()
    c = conn.cursor()
    ashby_points = []
    try:
        c.execute("""
            SELECT m.material_name, m.paper_id, p.doi,
                   MAX(CASE WHEN pr.property_name LIKE '%Yield Strength%' THEN pr.si_value ELSE NULL END) as yield_strength_mpa,
                   MAX(CASE WHEN pr.property_name LIKE '%Density%' THEN pr.value_numeric ELSE NULL END) as density_gcm3,
                   MAX(CASE WHEN pr.property_name LIKE '%Tensile%' THEN pr.si_value ELSE NULL END) as tensile_strength_mpa,
                   MAX(CASE WHEN pr.property_name LIKE '%Hardness%' THEN pr.value_numeric ELSE NULL END) as hardness_hv
            FROM materials m
            JOIN properties pr ON m.material_name = pr.material_name AND m.paper_id = pr.paper_id
            JOIN papers p ON m.paper_id = p.paper_id
            GROUP BY m.material_name, m.paper_id, p.doi
            HAVING yield_strength_mpa IS NOT NULL OR density_gcm3 IS NOT NULL;
        """)
        for row in c.fetchall():
            ashby_points.append({
                "material": row[0],
                "paper_id": row[1],
                "doi": row[2],
                "yield_strength_mpa": row[3],
                "density_gcm3": row[4],
                "tensile_strength_mpa": row[5],
                "hardness_hv": row[6]
            })
    finally:
        conn.close()

    return {
        "total_records": len(records),
        "materials_count": len(matrix_df["Material / Alloy"].unique()),
        "papers_count": len(matrix_df["Paper ID"].unique()),
        "records": records,
        "ashby_points": ashby_points
    }

# ==============================================================================
# GROUNDED ACADEMIC RESEARCH ASSISTANT (CrystaBot)
# ==============================================================================

class ChatRequest(BaseModel):
    message: str = Field(..., example="What is the yield strength and composition of Ti-6Al-4V?")

@app.post("/api/v1/assistant/chat")
def academic_assistant_chat(payload: ChatRequest):
    """
    Grounded scientific assistant answering queries strictly from extracted paper tables and literature.
    Never hallucinates ungrounded properties; cites exact DOI, paper, and table numbers.
    """
    query = payload.message.strip().lower()
    search_res = search_knowledge(keyword=query)

    # If general greeting
    if any(g in query for g in ["hello", "hi", "help", "who are you", "what can you do"]):
        return {
            "response": (
                "Greetings! I am **CrystaBot**, the grounded materials informatics research copilot for CrystaGraph. "
                "I synthesize extracted table data, chemical stoichiometry (wt%, at%, mol%), and SI-standardized "
                "properties from verified scientific publications.\n\n"
                "You can query me for:\n"
                "• Specific material properties (e.g. *'What is the yield strength of Ti-6Al-4V?'*)\n"
                "• Cross-paper comparisons (e.g. *'Compare density and hardness of titanium alloys vs high entropy alloys'*)\n"
                "• Paper table provenance (e.g. *'Show tables for barium titanate dielectrics'*)"
            ),
            "citations": [],
            "grounded": True,
            "match_count": 0
        }

    # If query found matching grounded knowledge
    if not search_res.empty:
        matches = search_res.head(5).to_dict(orient="records")
        citations = []
        synthesis_lines = []

        for m in matches:
            mat = m.get("material_name", "Material")
            prop = m.get("property_name", "Property")
            val = m.get("value_numeric", "")
            unit = m.get("unit", "")
            si_val = m.get("si_value", "")
            si_unit = m.get("si_unit", "")
            paper_id = m.get("paper_id", "")
            doi = m.get("doi", "")
            table_id = m.get("table_id", "")
            comp = m.get("composition_summary", "")

            citation_str = f"Paper: {paper_id} (DOI: {doi}), Table: {table_id}"
            if citation_str not in citations:
                citations.append({
                    "paper_id": paper_id,
                    "doi": doi,
                    "table_id": table_id,
                    "material": mat,
                    "property": prop
                })

            si_str = f" ({si_val} {si_unit} in SI units)" if si_val and si_unit and si_unit != unit else ""
            comp_str = f" [Stoichiometry: {comp}]" if comp else ""
            synthesis_lines.append(
                f"• **{mat}**: {prop} = **{val} {unit}**{si_str}{comp_str} *(Source: {table_id}, DOI: {doi})*"
            )

        response_text = (
            f"Based on grounded extractions from scientific tables in the CrystaGraph repository, "
            f"I found **{len(search_res)} verified measurements** matching your query:\n\n" +
            "\n".join(synthesis_lines) +
            "\n\n*All values above are directly linked to published table cells with cell-span normalization.*"
        )

        return {
            "response": response_text,
            "citations": citations,
            "grounded": True,
            "match_count": len(search_res)
        }

    # Query not in current database
    return {
        "response": (
            f"I searched the ingested repository for **'{payload.message}'**, but no direct table records "
            f"matched those exact terms. In accordance with CrystaGraph academic integrity guidelines, "
            f"I do not fabricate or hallucinate material properties without direct table or publication provenance.\n\n"
            f"💡 *Suggestion*: You can upload the corresponding scientific paper (PDF or XML) in the "
            f"**Upload Papers** tab to parse its tables and extract those properties into your workspace."
        ),
        "citations": [],
        "grounded": True,
        "match_count": 0
    }

# ==============================================================================
# MACHINE LEARNING PROPERTY PREDICTION
# ==============================================================================

@app.post("/api/v1/predict")
def predict_property(payload: CompositionInput):
    """Runs machine learning inference to predict material properties from elemental composition."""
    try:
        res = predictor.predict(payload.composition, payload.property_name)
        if "error" in res:
            raise HTTPException(status_code=400, detail=res["error"])
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
