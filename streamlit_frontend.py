import streamlit as st
import cv2
import numpy as np
from PIL import Image, ImageOps
import os

from landmark_detector import FaceLandmarkDetector
from filter_engine import FilterEngine


st.set_page_config(page_title="Bitmoji Filter App", layout="wide")

# -----------------------------
# Styling
# -----------------------------
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 1.5rem;
    max-width: 1200px;
}

.main-title {
    text-align: center;
    font-size: 2.3rem;
    font-weight: 700;
    margin-bottom: 0.2rem;
}

.sub-text {
    text-align: center;
    color: #8a8a8a;
    margin-bottom: 1.6rem;
    font-size: 1rem;
}

/* Make image preview area cleaner */
.preview-card {
    padding: 12px;
    border-radius: 16px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 10px;
}

.current-filter {
    text-align: center;
    color: #cfcfcf;
    font-size: 1rem;
    margin-top: 10px;
    margin-bottom: 12px;
}

.right-panel-box {
    padding: 14px 16px;
    border-radius: 16px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 12px;
}

.section-title {
    font-size: 1rem;
    font-weight: 700;
    margin-bottom: 10px;
    text-align: center;
}

.small-label {
    font-size: 0.95rem;
    font-weight: 600;
    margin-top: 10px;
    margin-bottom: 8px;
}

.selected-sample-box {
    margin-top: 10px;
    padding: 10px 12px;
    border-radius: 12px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.10);
    text-align: center;
    color: #e6e6e6;
    font-size: 0.95rem;
}

.selected-sample-label {
    color: #9ecbff;
    font-weight: 700;
}

/* Reduce vertical gap Streamlit adds between widgets */
div[data-testid="stVerticalBlock"] > div:has(.compact-gap) {
    margin-bottom: 0.35rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">Bitmoji Filter App</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-text">Apply fun face filters to sample Bitmojis or your own uploaded image.</div>',
    unsafe_allow_html=True
)

# -----------------------------
# Setup
# -----------------------------
detector = FaceLandmarkDetector()
engine = FilterEngine()

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(PROJECT_ROOT, "frontend", "public")
SAMPLE_FOLDER = os.path.join(PUBLIC_DIR, "sample_faces")
FILTERS_DIR = os.path.join(PUBLIC_DIR, "filters")
OUTPUT_FOLDER = "outputs"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

SAMPLE_MAP = {
    "2D Male": "2d_bitmoji_male.jpg",
    "2D Female": "2d_bitmoji_female.jpg",
    "3D Male": "3d_bitmoji_male.jpg",
    "3D Female": "3d_bitmoji_female.jpg"
}

# -----------------------------
# Session state
# -----------------------------
if "selected_filter" not in st.session_state:
    st.session_state.selected_filter = "Glasses"

if "selected_sample_label" not in st.session_state:
    st.session_state.selected_sample_label = "2D Male"

if "image_source" not in st.session_state:
    st.session_state.image_source = "Sample"

# -----------------------------
# Layout
# -----------------------------
left_col, right_col = st.columns([1.05, 1], gap="large")

selected_image = None
image_name = "output"

# =============================
# RIGHT SIDE = controls
# =============================
with right_col:
    st.markdown('<div class="right-panel-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Choose Image Source</div>', unsafe_allow_html=True)

    source = st.radio(
        "Source",
        ["Sample", "Upload"],
        horizontal=True,
        label_visibility="collapsed",
        index=0 if st.session_state.image_source == "Sample" else 1
    )
    st.session_state.image_source = source

    # -----------------------------
    # SAMPLE MODE
    # -----------------------------
    if source == "Sample":
        st.markdown('<div class="small-label">2D</div>', unsafe_allow_html=True)
        s1, s2 = st.columns(2)

        with s1:
            if st.button("👦 Male", use_container_width=True, key="sample_2d_male"):
                st.session_state.selected_sample_label = "2D Male"
                st.rerun()

        with s2:
            if st.button("👧 Female", use_container_width=True, key="sample_2d_female"):
                st.session_state.selected_sample_label = "2D Female"
                st.rerun()

        st.markdown('<div class="small-label">3D</div>', unsafe_allow_html=True)
        s3, s4 = st.columns(2)

        with s3:
            if st.button("🧑 Male", use_container_width=True, key="sample_3d_male"):
                st.session_state.selected_sample_label = "3D Male"
                st.rerun()

        with s4:
            if st.button("👩 Female", use_container_width=True, key="sample_3d_female"):
                st.session_state.selected_sample_label = "3D Female"
                st.rerun()

        current_sample = st.session_state.selected_sample_label
        st.markdown(
            f'<div class="selected-sample-box">Selected Sample: <span class="selected-sample-label">{current_sample}</span></div>',
            unsafe_allow_html=True
        )

        sample_filename = SAMPLE_MAP[current_sample]
        sample_path = os.path.join(SAMPLE_FOLDER, sample_filename)

        if os.path.exists(sample_path):
            selected_image = Image.open(sample_path).convert("RGB")
            image_name = os.path.splitext(sample_filename)[0]
        else:
            st.error(f"Sample image not found: {sample_filename}")

    # -----------------------------
    # UPLOAD MODE
    # -----------------------------
    else:
        uploaded_file = st.file_uploader(
            "Upload an image",
            type=["jpg", "jpeg", "png"]
        )

        mirror_image = st.checkbox("Mirror Image Horizontal", value=True)

        if uploaded_file is not None:
            selected_image = Image.open(uploaded_file).convert("RGB")
            selected_image = ImageOps.exif_transpose(selected_image)
            
            if mirror_image:
                selected_image = ImageOps.mirror(selected_image)
                
            image_name = os.path.splitext(uploaded_file.name)[0]

    st.markdown('</div>', unsafe_allow_html=True)

    # -----------------------------
    # Filter controls
    # -----------------------------
    st.markdown('<div class="right-panel-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Filters</div>', unsafe_allow_html=True)

    f1, f2 = st.columns(2)
    f3, f4 = st.columns(2)
    f5, _ = st.columns([1, 1])

    with f1:
        if st.button("👓 Glasses", use_container_width=True):
            st.session_state.selected_filter = "Glasses"
            st.rerun()

    with f2:
        if st.button("👨 Moustache", use_container_width=True):
            st.session_state.selected_filter = "Moustache"
            st.rerun()

    with f3:
        if st.button("👑 Crown", use_container_width=True):
            st.session_state.selected_filter = "Crown"
            st.rerun()

    with f4:
        if st.button("🤠 Cowboy Hat", use_container_width=True):
            st.session_state.selected_filter = "Cowboy Hat"
            st.rerun()

    with f5:
        if st.button("🎀 Bow Tie", use_container_width=True):
            st.session_state.selected_filter = "Bow Tie"
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# =============================
# LEFT SIDE = image preview
# =============================
with left_col:
    if selected_image is not None:
        image_np = np.array(selected_image)
        image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

        landmarks = detector.get_landmarks(image_bgr, strict=(source == "Upload"))

        if landmarks is None:
            st.warning("No face detected in this image.")
            result_bgr = image_bgr.copy()
        else:
            selected_filter = st.session_state.selected_filter

            if selected_filter == "Glasses":
                result_bgr = engine.apply_glasses(image_bgr, landmarks, os.path.join(FILTERS_DIR, "glasses.png"))

            elif selected_filter == "Moustache":
                result_bgr = engine.apply_moustache(image_bgr, landmarks, os.path.join(FILTERS_DIR, "moustache.png"))

            elif selected_filter == "Crown":
                result_bgr = engine.apply_crown(image_bgr, landmarks, os.path.join(FILTERS_DIR, "crown.png"))

            elif selected_filter == "Cowboy Hat":
                result_bgr = engine.apply_cowboy_hat(image_bgr, landmarks, os.path.join(FILTERS_DIR, "cowboy_hat.png"))

            elif selected_filter == "Bow Tie":
                result_bgr = engine.apply_bow_tie(image_bgr, landmarks, os.path.join(FILTERS_DIR, "bow_tie.png"))

            else:
                result_bgr = image_bgr.copy()

        result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)

        st.markdown('<div class="preview-card">', unsafe_allow_html=True)
        st.image(result_rgb, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(
            f'<div class="current-filter">Current Filter: <b>{st.session_state.selected_filter}</b></div>',
            unsafe_allow_html=True
        )

        safe_filter_name = st.session_state.selected_filter.lower().replace(" ", "_")
        output_path = os.path.join(
            OUTPUT_FOLDER,
            f"{image_name}_{safe_filter_name}.png"
        )

        Image.fromarray(result_rgb).save(output_path)

        download_col1, download_col2, download_col3 = st.columns([1, 1.4, 1])
        with download_col2:
            with open(output_path, "rb") as f:
                st.download_button(
                    label="⬇ Download Image",
                    data=f,
                    file_name=os.path.basename(output_path),
                    mime="image/png",
                    use_container_width=True
                )

    else:
        st.markdown('<div class="preview-card">', unsafe_allow_html=True)
        st.info("Choose a sample or upload an image to begin.")
        st.markdown('</div>', unsafe_allow_html=True)