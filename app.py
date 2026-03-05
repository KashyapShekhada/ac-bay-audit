"""
app.py — AC Bay Store Image Viewer
Run with: streamlit run app.py
"""

import os
import json
import pandas as pd
import streamlit as st
from PIL import Image

# ── Config ────────────────────────────────────────────────────────────────────
STORE_IMAGES_DIR = "store_images"
INDEX_FILE = os.path.join(STORE_IMAGES_DIR, "store_index.json")
MAPPING_FILE = "store_mapping.xlsx"

# ── Page Setup ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AC Bay Audit Viewer",
    page_icon="❄️",
    layout="wide"
)

# ── Theme & CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    section[data-testid="stSidebar"] {
        background-color: #161b22; border-right: 1px solid #30363d;
    }
    .header-banner {
        background: linear-gradient(135deg, #0a3d62 0%, #1e3799 50%, #0c2461 100%);
        border-radius: 16px; padding: 32px 40px; margin-bottom: 24px;
        border: 1px solid #1f6feb; position: relative; overflow: hidden;
    }
    .header-banner::before {
        content: "❄️"; position: absolute; font-size: 120px;
        right: 40px; top: -10px; opacity: 0.12;
    }
    .header-title { font-size: 2.2rem; font-weight: 800; color: #ffffff; margin: 0; }
    .header-tag {
        display: inline-block; background: #1f6feb; color: white;
        font-size: 0.75rem; font-weight: 600; padding: 3px 12px;
        border-radius: 20px; margin-top: 12px; text-transform: uppercase; letter-spacing: 0.5px;
    }
    .filter-title {
        font-size: 0.8rem; font-weight: 600; color: #8b949e;
        text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px;
    }
    .store-card {
        background: #161b22; border: 1px solid #30363d;
        border-radius: 12px; padding: 20px 24px; margin-bottom: 16px;
    }
    .badge {
        display: inline-block; padding: 3px 10px; border-radius: 20px;
        font-size: 0.75rem; font-weight: 600; margin-right: 6px; margin-top: 8px;
    }
    .badge-region { background: #1f3a5f; color: #58a6ff; }
    .badge-city   { background: #1a2f1a; color: #3fb950; }
    .badge-state  { background: #2d1f3a; color: #d2a8ff; }
    .badge-cluster{ background: #3a2a1a; color: #ffa657; }
    .img-label {
        font-size: 0.8rem; color: #8b949e; margin: 12px 0 6px 0;
        font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;
    }
    hr { border-color: #30363d !important; }
    [data-testid="stMetricValue"] { color: #58a6ff !important; font-weight: 700; }
    [data-testid="stMetricLabel"] { color: #8b949e !important; }
    .stDownloadButton > button {
        background-color: #21262d !important; border: 1px solid #30363d !important;
        color: #58a6ff !important; border-radius: 8px !important; font-size: 0.8rem !important;
    }
    .stDownloadButton > button:hover {
        border-color: #58a6ff !important; background-color: #1f3a5f !important;
    }
    .placeholder {
        text-align: center; padding: 80px 20px; background: #161b22;
        border-radius: 16px; border: 2px dashed #30363d; color: #484f58; font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)


# ── Load Data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_index():
    if not os.path.exists(INDEX_FILE):
        return None
    with open(INDEX_FILE) as f:
        return json.load(f)

@st.cache_data
def load_mapping():
    if not os.path.exists(MAPPING_FILE):
        return None
    df = pd.read_excel(MAPPING_FILE, dtype={"Site": str})
    df.columns = df.columns.str.strip()
    df["Site"] = df["Site"].astype(str).str.strip()
    return df


store_index = load_index()
mapping_df = load_mapping()

if store_index is None:
    st.error("❌ store_index.json not found.")
    st.stop()
if mapping_df is None:
    st.error("❌ store_mapping.xlsx not found.")
    st.stop()

store_index = {str(k).strip(): v for k, v in store_index.items()}


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-banner">
    <div class="header-title">❄️ AC Bay Audit — Store Display Tracker</div>
    <span class="header-tag">🌡️ AC Season 2026 Audit</span>
</div>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📊 Audit Overview")
    total_stores = len(store_index)
    total_images = sum(len(v) if isinstance(v, list) else 1 for v in store_index.values())
    mapped = mapping_df[mapping_df["Site"].isin(store_index.keys())]
    st.metric("Stores Submitted", total_stores)
    st.metric("Total Photos", total_images)
    st.metric("Regions Covered", mapped["Region"].nunique() if not mapped.empty else 0)
    st.divider()
    st.markdown("##### 📍 Stores by Region")
    if not mapped.empty:
        for region, count in mapped["Region"].value_counts().items():
            st.markdown(
                f"<span style='color:#58a6ff'>{region}</span>"
                f"<span style='color:#484f58'> — {count} store(s)</span>",
                unsafe_allow_html=True
            )


# ── Interconnected Filters ────────────────────────────────────────────────────
st.markdown('<p class="filter-title">🔍 Filter Stores</p>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

all_regions = sorted(mapping_df["Region"].dropna().unique().tolist())
with col1:
    selected_region = st.selectbox("📌 Region", ["All Regions"] + all_regions)

city_df = mapping_df[mapping_df["Region"] == selected_region] if selected_region != "All Regions" else mapping_df
all_cities = sorted(city_df["City"].dropna().unique().tolist())
with col2:
    selected_city = st.selectbox("🏙️ City", ["All Cities"] + all_cities)

filtered_df = mapping_df.copy()
if selected_region != "All Regions":
    filtered_df = filtered_df[filtered_df["Region"] == selected_region]
if selected_city != "All Cities":
    filtered_df = filtered_df[filtered_df["City"] == selected_city]

available_sites = filtered_df[filtered_df["Site"].isin(store_index.keys())]
store_options = [(f"{r['Site']} — {r['Store']} ({r['City']})", str(r["Site"])) for _, r in available_sites.iterrows()]

with col3:
    selected_label = st.selectbox("🏪 Store", ["Select a Store"] + [s[0] for s in store_options])

st.divider()

final_store = None
if selected_label != "Select a Store":
    final_store = next((s[1] for s in store_options if s[0] == selected_label), None)


# ── Display ───────────────────────────────────────────────────────────────────
if final_store:
    meta = mapping_df[mapping_df["Site"] == final_store]
    if not meta.empty:
        row = meta.iloc[0]
        store_name = row.get("Store", "—")
        city       = row.get("City", "—")
        state      = row.get("State", "—")
        region     = row.get("Region", "—")
        cluster    = row.get("Cluster", "—")
    else:
        store_name = city = state = region = cluster = "—"

    filenames = store_index.get(final_store, [])
    if isinstance(filenames, str):
        filenames = [filenames]
    img_count = len(filenames)

    st.markdown(f"""
    <div class="store-card">
        <div style="font-size:1.5rem;font-weight:800;color:#ffffff">{store_name}</div>
        <div style="font-size:0.9rem;color:#8b949e;margin-top:4px">Site Code: {final_store}</div>
        <div style="margin-top:10px">
            <span class="badge badge-region">📌 {region}</span>
            <span class="badge badge-city">🏙️ {city}</span>
            <span class="badge badge-state">🗺️ {state}</span>
            <span class="badge badge-cluster">🔷 {cluster}</span>
            <span class="badge" style="background:#1a2d2d;color:#39d353">📷 {img_count} photo(s)</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    for i, filename in enumerate(filenames):
        image_path = os.path.join(STORE_IMAGES_DIR, filename)
        if os.path.exists(image_path):
            if img_count > 1:
                st.markdown(f'<p class="img-label">Photo {i+1} of {img_count}</p>', unsafe_allow_html=True)
            img = Image.open(image_path)
            st.image(img, use_column_width=True)
            with open(image_path, "rb") as f:
                st.download_button(
                    label=f"⬇️ Download Photo {i+1}",
                    data=f.read(), file_name=filename,
                    mime="image/jpeg", key=f"dl_{i}"
                )
            if i < img_count - 1:
                st.divider()
        else:
            st.warning(f"Image file not found: {filename}")
else:
    st.markdown("""
    <div class="placeholder">
        ❄️ Select a region, city and store above to view AC bay photos
    </div>
    """, unsafe_allow_html=True)

st.divider()
st.markdown(
    "<p style='text-align:center;color:#484f58;font-size:0.8rem'>"
    "AC Bay Audit Dashboard · Confidential · For Internal Use Only</p>",
    unsafe_allow_html=True
)
