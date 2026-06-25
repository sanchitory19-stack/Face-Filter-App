import cv2
import mediapipe as mp


# MediaPipe Face Mesh landmark indices used by FilterEngine
LANDMARK_INDICES = {
    "left_eye_outer": 33,
    "left_eye_inner": 133,
    "right_eye_inner": 362,
    "right_eye_outer": 263,
    "nose_tip": 1,
    "left_mouth": 61,
    "right_mouth": 291,
    "chin": 152,
    "forehead": 10,
    "left_face": 234,
    "right_face": 454,
}


class FaceLandmarkDetector:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_face_detection = mp.solutions.face_detection

        # Face mesh for landmarks
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )

        # Face detector for strict validation
        self.face_detector = self.mp_face_detection.FaceDetection(
            model_selection=1,
            min_detection_confidence=0.75
        )

    def get_landmarks(self, image, strict=True):
        """
        strict=True  -> use face detection gate first (good for uploaded real photos)
        strict=False -> skip face detection gate (better for Bitmoji/cartoon samples)
        """
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # -----------------------------
        # STRICT MODE: require a proper face detection first
        # -----------------------------
        if strict:
            detection_results = self.face_detector.process(rgb_image)

            if not detection_results.detections:
                return None

            detection = detection_results.detections[0]
            score = detection.score[0]

            if score < 0.75:
                return None

        # -----------------------------
        # Then run face mesh
        # -----------------------------
        mesh_results = self.face_mesh.process(rgb_image)

        if not mesh_results.multi_face_landmarks:
            return None

        face_landmarks = mesh_results.multi_face_landmarks[0]
        h, w, _ = image.shape

        points = []
        for landmark in face_landmarks.landmark:
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            points.append((x, y))

        return {
            name: points[index]
            for name, index in LANDMARK_INDICES.items()
            if index < len(points)
        }