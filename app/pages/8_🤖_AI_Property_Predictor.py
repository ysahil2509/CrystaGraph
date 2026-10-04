"""
AI Property Predictor Page: Machine Learning inference tool for forecasting novel material properties.
"""

import streamlit as st
import os
import sys
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.dirname(CURRENT_DIR)
PROJECT_ROOT = os.path.dirname(APP_DIR)
sys.path.insert(0, APP_DIR)
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, "models"))

from models.train_property_predictor import MaterialPropertyPredictor

st.set_page_config(page_title="AI Property Predictor | CrystaGraph", page_icon="🤖", layout="wide")

st.title("🤖 AI Material Property Predictor")
st.caption("Machine Learning regression models (Random Forest) trained on extracted literature data to forecast physical properties for novel alloy and ceramic chemistries.")

# Load Predictor
predictor = MaterialPropertyPredictor()
meta_path = os.path.join(PROJECT_ROOT, "models/predictor_metadata.json")

if os.path.exists(meta_path):
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
        predictor.feature_columns = meta.get("feature_columns", [])
        trained_props = meta.get("trained_properties", ["Yield Strength", "Density", "Tensile Strength"])
        model_metrics = meta.get("metrics", {})
else:
    st.warning("⚠️ Model weights not found. Training models now...")
    model_metrics = predictor.train()
    trained_props = list(model_metrics.keys())

# Property Selection & Presets
c_sel1, c_sel2 = st.columns([1, 1])
with c_sel1:
    target_prop = st.selectbox("Select Target Property to Predict:", trained_props)
with c_sel2:
    preset_choice = st.selectbox("Or Load Preset Material System:", [
        "Custom Formulation",
        "Ti-6Al-4V (Grade 5 Titanium)",
        "Al 7075 (Aerospace Aluminum)",
        "CoCrFeNi (High-Entropy Alloy)",
        "BaTiO3 (Barium Titanate Ceramic)"
    ])

# Pre-fill based on preset
default_comps = {"Ti": 90.0, "Al": 6.0, "V": 4.0}
if preset_choice == "Ti-6Al-4V (Grade 5 Titanium)":
    default_comps = {"Ti": 90.0, "Al": 6.0, "V": 4.0}
elif preset_choice == "Al 7075 (Aerospace Aluminum)":
    default_comps = {"Al": 90.0, "Zn": 5.6, "Mg": 2.5, "Cu": 1.6}
elif preset_choice == "CoCrFeNi (High-Entropy Alloy)":
    default_comps = {"Co": 25.0, "Cr": 25.0, "Fe": 25.0, "Ni": 25.0}
elif preset_choice == "BaTiO3 (Barium Titanate Ceramic)":
    default_comps = {"BaO": 50.0, "TiO2": 50.0}

st.markdown("---")
st.subheader("🧪 Define Chemical Composition")
st.caption("Specify mass or atomic percentages ($wt\% / at\%$). The total sum will be normalized.")

comp_inputs = {}
cols = st.columns(4)

# Show common elements as quick number inputs
available_elements = ["Ti", "Al", "V", "Fe", "Ni", "Cr", "Co", "Mn", "Cu", "Mg", "Zn", "Li", "BaO", "TiO2", "PbO", "ZrO2"]
for i, elem in enumerate(available_elements):
    with cols[i % 4]:
        default_val = float(default_comps.get(elem, 0.0))
        val = st.number_input(f"{elem} (%):", min_value=0.0, max_value=100.0, value=default_val, step=0.5, key=f"elem_{elem}")
        if val > 0:
            comp_inputs[elem] = val

# Predict Button
st.markdown("---")
if st.button("🚀 Run AI Property Prediction", type="primary"):
    if not comp_inputs:
        st.warning("Please specify at least one chemical component percentage > 0%.")
    else:
        with st.spinner("Computing regression prediction across ensemble trees..."):
            res = predictor.predict(comp_inputs, target_prop)

        if "error" in res:
            st.error(res["error"])
        else:
            col_res1, col_res2 = st.columns([1.2, 0.8])
            
            with col_res1:
                st.success(f"### 🎯 Predicted {target_prop}: **{res['predicted_value']}**")
                st.info(f"**95% Confidence Interval:** `[{res['confidence_lower']}, {res['confidence_upper']}]`  \n**Model Uncertainty (Std Dev):** `±{res['std_dev']}`  \n**Algorithm:** Ensemble Random Forest Regressor")

                # Gauge / Range Chart
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=res["predicted_value"],
                    title={'text': f"Predicted {target_prop}"},
                    gauge={
                        'axis': {'range': [max(0, res['confidence_lower'] * 0.5), res['confidence_upper'] * 1.5]},
                        'bar': {'color': "#2b5c8f"},
                        'steps': [
                            {'range': [0, res['confidence_lower']], 'color': "#e9ecef"},
                            {'range': [res['confidence_lower'], res['confidence_upper']], 'color': "#cce5ff"}
                        ]
                    }
                ))
                fig_gauge.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig_gauge, use_container_width=True)

            with col_res2:
                st.markdown("#### 🔍 Model Feature Importance")
                top_feats = model_metrics.get(target_prop, {}).get("top_features", {})
                if top_feats:
                    df_fi = pd.DataFrame(list(top_feats.items()), columns=["Element / Oxide", "Relative Importance"])
                    fig_fi = px.bar(df_fi, x="Relative Importance", y="Element / Oxide", orientation="h", color="Relative Importance", color_continuous_scale="Viridis")
                    fig_fi.update_layout(yaxis=dict(autorange="reversed"), height=300, margin=dict(l=20, r=20, t=40, b=20))
                    st.plotly_chart(fig_fi, use_container_width=True)
                else:
                    st.caption("Feature importances not available.")
