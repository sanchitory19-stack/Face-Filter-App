from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from fastapi.staticfiles import StaticFiles
import cv2
from io import BytesIO
from PIL import Image
import os

from landmark_detector import FaceLandmarkDetector
from filter_engine import FilterEngine


BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
PUBLIC_DIR = os.path.join(PROJECT_ROOT, "frontend", "public")
SAMPLE_FACES_DIR = os.path.join(PUBLIC_DIR, "sample_faces")
FILTERS_DIR = os.path.join(PUBLIC_DIR, "filters")

app = FastAPI()
app.mount("/static", StaticFiles(directory=SAMPLE_FACES_DIR), name="static")

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later we can lock this to localhost:3000 or your deployed frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

detector = FaceLandmarkDetector()
engine = FilterEngine()

FILTER_PATHS = {
    "Glasses": os.path.join(FILTERS_DIR, "glasses.png"),
    "Moustache": os.path.join(FILTERS_DIR, "moustache.png"),
    "Crown": os.path.join(FILTERS_DIR, "crown.png"),
    "Cowboy Hat": os.path.join(FILTERS_DIR, "cowboy_hat.png"),
    "Bow Tie": os.path.join(FILTERS_DIR, "bow_tie.png"),
}

SAMPLE_IMAGES = {
    "2d_male": os.path.join(SAMPLE_FACES_DIR, "2d_bitmoji_male.jpg"),
    "2d_female": os.path.join(SAMPLE_FACES_DIR, "2d_bitmoji_female.jpg"),
    "3d_male": os.path.join(SAMPLE_FACES_DIR, "3d_bitmoji_male.jpg"),
    "3d_female": os.path.join(SAMPLE_FACES_DIR, "3d_bitmoji_female.jpg"),
}


def apply_selected_filter(image_bgr, landmarks, selected_filter):
    if selected_filter == "Glasses":
        return engine.apply_glasses(image_bgr, landmarks, FILTER_PATHS["Glasses"])
    elif selected_filter == "Moustache":
        return engine.apply_moustache(image_bgr, landmarks, FILTER_PATHS["Moustache"])
    elif selected_filter == "Crown":
        return engine.apply_crown(image_bgr, landmarks, FILTER_PATHS["Crown"])
    elif selected_filter == "Cowboy Hat":
        return engine.apply_cowboy_hat(image_bgr, landmarks, FILTER_PATHS["Cowboy Hat"])
    elif selected_filter == "Bow Tie":
        return engine.apply_bow_tie(image_bgr, landmarks, FILTER_PATHS["Bow Tie"])
    return image_bgr


@app.get("/")
def home():
    return {"message": "Bitmoji Filter API is running"}


@app.get("/samples")
def get_samples():
    return SAMPLE_IMAGES


@app.post("/apply-filter")
async def apply_filter(
    filter_name: str = Form(...),
    source_type: str = Form(...),   # "sample" or "upload"
    sample_key: str = Form(None),
    file: UploadFile = File(None)
):
    try:
        # -----------------------------
        # Load image from sample or upload
        # -----------------------------
        if source_type == "sample":
            if not sample_key or sample_key not in SAMPLE_IMAGES:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Invalid sample key"}
                )

            image_path = SAMPLE_IMAGES[sample_key]
            image_bgr = cv2.imread(image_path)

            if image_bgr is None:
                return JSONResponse(
                    status_code=500,
                    content={"error": f"Could not load sample image: {image_path}"}
                )

            strict = False

        elif source_type == "upload":
            if file is None:
                return JSONResponse(
                    status_code=400,
                    content={"error": "No uploaded image provided"}
                )

            image_bytes = await file.read()
            np_arr = np.frombuffer(image_bytes, np.uint8)
            image_bgr = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

            if image_bgr is None:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Invalid uploaded image"}
                )

            strict = True

        else:
            return JSONResponse(
                status_code=400,
                content={"error": "source_type must be 'sample' or 'upload'"}
            )

        # -----------------------------
        # Detect landmarks
        # -----------------------------
        landmarks = detector.get_landmarks(image_bgr, strict=strict)

        if landmarks is None:
            return JSONResponse(
                status_code=400,
                content={"error": "No face detected in image"}
            )

        # -----------------------------
        # Apply selected filter
        # -----------------------------
        result_bgr = apply_selected_filter(image_bgr, landmarks, filter_name)

        # Convert to RGB and then PNG bytes
        result_rgb = cv2.cvtColor(result_bgr, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(result_rgb)

        buffer = BytesIO()
        pil_image.save(buffer, format="PNG")
        buffer.seek(0)

        return StreamingResponse(buffer, media_type="image/png")

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )