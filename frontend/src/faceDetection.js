import { FaceLandmarker, FilesetResolver } from "@mediapipe/tasks-vision";

const LANDMARK_INDICES = {
  left_eye_outer: 33,
  left_eye_inner: 133,
  right_eye_inner: 362,
  right_eye_outer: 263,
  nose_tip: 1,
  left_mouth: 61,
  right_mouth: 291,
  chin: 152,
  forehead: 10,
  left_face: 234,
  right_face: 454,
  top_lip: 13,
  bottom_lip: 14,
};

const WASM_PATH =
  "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision/wasm";
const MODEL_PATH =
  "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task";

let initPromise = null;

export function initFaceLandmarker() {
  if (!initPromise) {
    initPromise = (async () => {
      const vision = await FilesetResolver.forVisionTasks(WASM_PATH);
      return FaceLandmarker.createFromOptions(vision, {
        baseOptions: { modelAssetPath: MODEL_PATH },
        runningMode: "IMAGE",
        numFaces: 1,
      });
    })();
  }

  return initPromise;
}

function toNamedLandmarks(faceLandmarks, width, height) {
  const landmarks = {};

  for (const [name, index] of Object.entries(LANDMARK_INDICES)) {
    const point = faceLandmarks[index];
    landmarks[name] = [
      Math.round(point.x * width),
      Math.round(point.y * height),
    ];
  }

  return landmarks;
}

export async function detectFaceLandmarks(image) {
  const landmarker = await initFaceLandmarker();
  const width = image.naturalWidth || image.width;
  const height = image.naturalHeight || image.height;
  const result = landmarker.detect(image);

  if (!result.faceLandmarks?.length) {
    return null;
  }

  return toNamedLandmarks(result.faceLandmarks[0], width, height);
}
