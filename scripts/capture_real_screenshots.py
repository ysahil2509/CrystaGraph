"""
Capture real screenshots of the running Streamlit web platform for CrystaGraph presentation.
"""
import os
import sys
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

# Start Streamlit in background
print("Starting Streamlit server...")
proc = subprocess.Popen(
    ["streamlit", "run", "app/streamlit_app.py", "--server.port=8501", "--server.headless=true"],
    cwd=PROJECT_ROOT,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

try:
    # Wait for server to be responsive
    import urllib.request
    started = False
    for i in range(25):
        try:
            with urllib.request.urlopen("http://localhost:8501/_stcore/health", timeout=1) as resp:
                if resp.status == 200:
                    started = True
                    break
        except Exception:
            time.sleep(1)
    
    if not started:
        print("Error: Streamlit failed to start within timeout.")
        sys.exit(1)
    
    print("Streamlit server is online! Initializing Selenium...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1440,900")
    
    driver = webdriver.Chrome(options=options)
    
    pages = [
        ("http://localhost:8501", "screenshot_dashboard.png"),
        ("http://localhost:8501/Table_Explorer", "screenshot_table_explorer.png"),
        ("http://localhost:8501/Material_Explorer", "screenshot_material_explorer.png"),
        ("http://localhost:8501/Knowledge_Graph", "screenshot_knowledge_graph.png"),
        ("http://localhost:8501/AI_Property_Predictor", "screenshot_property_predictor.png"),
    ]
    
    for url, filename in pages:
        out_path = os.path.join(ASSETS_DIR, filename)
        print(f"Capturing {url} -> {out_path}...")
        driver.get(url)
        time.sleep(3) # Wait for Streamlit components & Plotly charts to render
        driver.save_screenshot(out_path)
        print(f"Saved: {out_path} ({os.path.getsize(out_path)} bytes)")
    
    driver.quit()
    print("All screenshots successfully captured!")

finally:
    print("Terminating Streamlit server...")
    proc.terminate()
    proc.wait()
