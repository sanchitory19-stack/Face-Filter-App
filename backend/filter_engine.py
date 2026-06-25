import cv2
import numpy as np
from utils import overlay_png, rotate_image_with_anchor


class FilterEngine:
    def __init__(self):
        pass

    def apply_glasses(self, image, landmarks, glasses_path):
        if landmarks is None:
            return image

        output = image.copy()

        left_outer = landmarks["left_eye_outer"]
        left_inner = landmarks["left_eye_inner"]
        right_inner = landmarks["right_eye_inner"]
        right_outer = landmarks["right_eye_outer"]

        left_eye_x = (left_outer[0] + left_inner[0]) // 2
        left_eye_y = (left_outer[1] + left_inner[1]) // 2

        right_eye_x = (right_inner[0] + right_outer[0]) // 2
        right_eye_y = (right_inner[1] + right_outer[1]) // 2

        eye_center_x = (left_eye_x + right_eye_x) // 2
        eye_center_y = (left_eye_y + right_eye_y) // 2

        eye_distance = int(np.sqrt((right_eye_x - left_eye_x) ** 2 +
                                   (right_eye_y - left_eye_y) ** 2))

        angle = np.degrees(np.arctan2(left_eye_y - right_eye_y,
                                      right_eye_x - left_eye_x))

        glasses = cv2.imread(glasses_path, cv2.IMREAD_UNCHANGED)
        if glasses is None:
            raise FileNotFoundError(glasses_path)

        glasses_width = int(eye_distance * 2.25)
        aspect_ratio = glasses.shape[0] / glasses.shape[1]
        glasses_height = int(glasses_width * aspect_ratio)
        glasses = cv2.resize(glasses, (glasses_width, glasses_height))

        bridge_anchor = (
            int(glasses.shape[1] * 0.50),
            int(glasses.shape[0] * 0.38)
        )

        rotated, (ax, ay) = rotate_image_with_anchor(glasses, angle, bridge_anchor)

        top_left_x = int(eye_center_x - ax)
        top_left_y = int(eye_center_y - ay)

        return overlay_png(output, rotated, top_left_x, top_left_y)

    def apply_moustache(self, image, landmarks, moustache_path):
        if landmarks is None:
            return image

        left_mouth = landmarks["left_mouth"]
        right_mouth = landmarks["right_mouth"]
        nose = landmarks["nose_tip"]

        x1, y1 = left_mouth
        x2, y2 = right_mouth
        nx, ny = nose

        mouth_width = int(np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))
        angle = np.degrees(np.arctan2(y1 - y2, x2 - x1))

        moustache = cv2.imread(moustache_path, cv2.IMREAD_UNCHANGED)
        if moustache is None:
            raise FileNotFoundError(moustache_path)

        moustache_width = int(mouth_width * 1.4)
        aspect_ratio = moustache.shape[0] / moustache.shape[1]
        moustache_height = int(moustache_width * aspect_ratio)
        moustache = cv2.resize(moustache, (moustache_width, moustache_height))

        target_x = (x1 + x2) // 2
        target_y = (ny + (y1 + y2) // 2) // 2 + 5

        anchor = (moustache.shape[1] // 2, moustache.shape[0] // 2)

        rotated, (ax, ay) = rotate_image_with_anchor(moustache, angle, anchor)

        top_left_x = int(target_x - ax)
        top_left_y = int(target_y - ay)

        return overlay_png(image.copy(), rotated, top_left_x, top_left_y)

    def apply_crown(self, image, landmarks, crown_path):
        if landmarks is None:
            return image

        left_face = landmarks["left_face"]
        right_face = landmarks["right_face"]
        forehead = landmarks["forehead"]

        x1, y1 = left_face
        x2, y2 = right_face
        fx, fy = forehead

        face_width = int(np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))
        angle = np.degrees(np.arctan2(y1 - y2, x2 - x1))

        crown = cv2.imread(crown_path, cv2.IMREAD_UNCHANGED)
        if crown is None:
            raise FileNotFoundError(crown_path)

        crown_width = int(face_width * 1.2)
        aspect_ratio = crown.shape[0] / crown.shape[1]
        crown_height = int(crown_width * aspect_ratio)
        crown = cv2.resize(crown, (crown_width, crown_height))

        target_x = fx
        target_y = fy + 8

        anchor = (crown.shape[1] // 2, crown.shape[0])

        rotated, (ax, ay) = rotate_image_with_anchor(crown, angle, anchor)

        top_left_x = int(target_x - ax)
        top_left_y = int(target_y - ay)

        return overlay_png(image.copy(), rotated, top_left_x, top_left_y)

    def apply_cowboy_hat(self, image, landmarks, cowboy_hat_path):
        if landmarks is None:
            return image

        left_face = landmarks["left_face"]
        right_face = landmarks["right_face"]
        forehead = landmarks["forehead"]

        x1, y1 = left_face
        x2, y2 = right_face
        fx, fy = forehead

        face_width = int(np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))
        angle = np.degrees(np.arctan2(y1 - y2, x2 - x1))

        hat = cv2.imread(cowboy_hat_path, cv2.IMREAD_UNCHANGED)
        if hat is None:
            raise FileNotFoundError(cowboy_hat_path)

        hat_width = int(face_width * 1.5)
        aspect_ratio = hat.shape[0] / hat.shape[1]
        hat_height = int(hat_width * aspect_ratio)
        hat = cv2.resize(hat, (hat_width, hat_height))

        target_x = fx
        target_y = fy + 48

        anchor = (hat.shape[1] // 2, hat.shape[0])

        rotated, (ax, ay) = rotate_image_with_anchor(hat, angle, anchor)

        top_left_x = int(target_x - ax)
        top_left_y = int(target_y - ay)

        return overlay_png(image.copy(), rotated, top_left_x, top_left_y)

    def apply_bow_tie(self, image, landmarks, bow_tie_path):
        if landmarks is None:
            return image

        left_mouth = landmarks["left_mouth"]
        right_mouth = landmarks["right_mouth"]
        chin = landmarks["chin"]

        x1, y1 = left_mouth
        x2, y2 = right_mouth
        cx, cy = chin

        tie_width = int(np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2) * 2.0)
        angle = np.degrees(np.arctan2(y1 - y2, x2 - x1))

        tie = cv2.imread(bow_tie_path, cv2.IMREAD_UNCHANGED)
        if tie is None:
            raise FileNotFoundError(bow_tie_path)

        aspect_ratio = tie.shape[0] / tie.shape[1]
        tie_height = int(tie_width * aspect_ratio)
        tie = cv2.resize(tie, (tie_width, tie_height))

        target_x = cx
        target_y = cy + int(tie_height * 0.4)

        anchor = (tie.shape[1] // 2, tie.shape[0] // 2)

        rotated, (ax, ay) = rotate_image_with_anchor(tie, angle, anchor)

        top_left_x = int(target_x - ax)
        top_left_y = int(target_y - ay)

        return overlay_png(image.copy(), rotated, top_left_x, top_left_y)