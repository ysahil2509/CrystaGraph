"""
Production FastAPI REST Microservice for CrystaGraph.
Provides high-performance RESTful API endpoints for knowledge retrieval,
multi-paper querying, and machine learning material property prediction.
"""

import os
import sys
import json
import sqlite3
import pandas as pd
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, CURRENT_DIR)
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "models"))

from components.db_utils import get_dashboard_counts, query_df, search_knowledge
from train_property_predictor import MaterialPropertyPredictor

# Initialize FastAPI app
app = FastAPI(
    title="CrystaGraph API",
    description="RESTful API for AI-Driven Material Knowledge Mining and Machine Learning Property Prediction from Scientific Research Tables.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

# Load ML Predictor instance
predictor = MaterialPropertyPredictor()
metadata_path = os.path.join(PROJECT_ROOT, "models/predictor_metadata.json")
if os.path.exists(metadata_path):
    with open(metadata_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
        predictor.feature_columns = meta.get("feature_columns", [])

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

@app.get("/api/v1/papers")
def list_papers():
    """Lists all ingested scientific research papers."""
    df = query_df("SELECT paper_id, doi, pii, title, status FROM papers ORDER BY paper_id;")
    return df.to_dict(orient="records")

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
