#!/bin/bash
# Startup script for CrystaGraph

echo "======================================================================="
echo "   🔬 CrystaGraph: AI-Driven Material Knowledge Mining"
echo "======================================================================="

# Step 1: Run automated paper processing and database population
echo "[1/3] Processing 10 scientific XML papers and updating SQLite database..."
python3 scripts/process_papers.py

# Step 2: Train Machine Learning Property Prediction Models
echo "[2/3] Training Random Forest property prediction models..."
python3 models/train_property_predictor.py

# Step 3: Launch Streamlit web platform
echo "[3/3] Launching interactive Streamlit application..."
streamlit run app/streamlit_app.py
