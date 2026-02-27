import streamlit as st
import pandas as pd
import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from src.trainer import DraftPredictor

# Page config
st.set_page_config(
    page_title="LoL Draft Predictor",
    page_icon="⚔️",
    layout="wide"
)

# Load model and champion list
@st.cache_resource
def load_model():
    return DraftPredictor.load('models/draft_predictor.pkl')

@st.cache_data
def load_champions():
    with open('data/champion_name_map.json') as f:
        data = json.load(f)
    return sorted(data.values())

predictor = load_model()
all_champions = load_champions()

# Title
st.title("⚔️ LoL Draft Win Predictor")
st.caption("Challenger-trained model · Ranked Solo/Duo")

# Team columns
blue_col, mid_col, red_col = st.columns([2, 1, 2])

with blue_col:
    st.header("🔵 Blue Team")
    blue_picks = st.multiselect(
        "Picks (up to 5)",
        options=all_champions,
        max_selections=5,
        key="blue_picks"
    )

with red_col:
    st.header("🔴 Red Team")
    red_picks = st.multiselect(
        "Picks (up to 5)",
        options=all_champions,
        max_selections=5,
        key="red_picks"
    )

with mid_col:
    st.header("Prediction")
    predict_btn = st.button("Predict", use_container_width=True)

# Prediction
if predict_btn:
    if len(blue_picks) != 5 or len(red_picks) != 5:
        st.warning("Please select 5 champions for each team")
    else:
        result = predictor.predict(blue_picks, red_picks)
        blue_prob = result['blue_win_prob']
        red_prob = result['red_win_prob']

        with mid_col:
            st.metric("Blue Win", f"{blue_prob:.1%}")
            st.metric("Red Win", f"{red_prob:.1%}")
            st.progress(blue_prob)