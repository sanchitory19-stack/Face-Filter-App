import cv2
import numpy as np


def overlay_png(background, overlay, x, y):
    bh, bw = background.shape[:2]
    oh, ow = overlay.shape[:2]

    if x >= bw or y >= bh or x + ow <= 0 or y + oh <= 0:
        return background

    x1 = max(x, 0)
    y1 = max(y, 0)
    x2 = min(x + ow, bw)
    y2 = min(y + oh, bh)

    overlay_x1 = x1 - x
    overlay_y1 = y1 - y
    overlay_x2 = overlay_x1 + (x2 - x1)
    overlay_y2 = overlay_y1 + (y2 - y1)

    overlay_crop = overlay[overlay_y1:overlay_y2, overlay_x1:overlay_x2]

    if overlay_crop.shape[2] < 4:
        return background

    overlay_rgb = overlay_crop[:, :, :3]
    alpha = overlay_crop[:, :, 3] / 255.0

    roi = background[y1:y2, x1:x2]

    for c in range(3):
        roi[:, :, c] = (1 - alpha) * roi[:, :, c] + alpha * overlay_rgb[:, :, c]

    background[y1:y2, x1:x2] = roi
    return background


def rotate_image_with_anchor(image, angle, anchor_point):
    """
    Rotate transparent PNG without cutting it off,
    and return where the chosen anchor point ends up.

    anchor_point = (ax, ay) in ORIGINAL image coordinates
    """
    h, w = image.shape[:2]
    cx, cy = w / 2, h / 2

    M = cv2.getRotationMatrix2D((cx, cy), angle, 1.0)

    cos = abs(M[0, 0])
    sin = abs(M[0, 1])

    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))

    M[0, 2] += (new_w / 2) - cx
    M[1, 2] += (new_h / 2) - cy

    rotated = cv2.warpAffine(
        image,
        M,
        (new_w, new_h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(0, 0, 0, 0)
    )

    pt = np.array([[[anchor_point[0], anchor_point[1]]]], dtype=np.float32)
    mapped = cv2.transform(pt, M)[0][0]

    return rotated, (mapped[0], mapped[1])