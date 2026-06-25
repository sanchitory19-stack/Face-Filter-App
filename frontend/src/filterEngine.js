function resizeToCanvas(image, width, height) {
  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;
  canvas.getContext("2d").drawImage(image, 0, 0, width, height);
  return canvas;
}

function rotateImageWithAnchor(sourceCanvas, angleDeg, anchorX, anchorY) {
  const width = sourceCanvas.width;
  const height = sourceCanvas.height;
  const radians = (angleDeg * Math.PI) / 180;
  const cos = Math.abs(Math.cos(radians));
  const sin = Math.abs(Math.sin(radians));
  const newWidth = Math.ceil(height * sin + width * cos);
  const newHeight = Math.ceil(height * cos + width * sin);

  const canvas = document.createElement("canvas");
  canvas.width = newWidth;
  canvas.height = newHeight;
  const ctx = canvas.getContext("2d");

  const centerX = width / 2;
  const centerY = height / 2;

  ctx.translate(newWidth / 2, newHeight / 2);
  ctx.rotate(radians);
  ctx.drawImage(sourceCanvas, -centerX, -centerY);

  const dx = anchorX - centerX;
  const dy = anchorY - centerY;
  const mappedX =
    newWidth / 2 + dx * Math.cos(radians) - dy * Math.sin(radians);
  const mappedY =
    newHeight / 2 + dx * Math.sin(radians) + dy * Math.cos(radians);

  return { canvas, anchorX: mappedX, anchorY: mappedY };
}

function overlayCanvas(targetCtx, overlayCanvas, x, y) {
  targetCtx.drawImage(overlayCanvas, Math.round(x), Math.round(y));
}

function placeRotatedFilter(
  targetCtx,
  filterImage,
  width,
  height,
  angle,
  targetX,
  targetY,
  anchorX,
  anchorY
) {
  const resized = resizeToCanvas(filterImage, width, height);
  const { canvas, anchorX: mappedX, anchorY: mappedY } = rotateImageWithAnchor(
    resized,
    angle,
    anchorX,
    anchorY
  );

  overlayCanvas(targetCtx, canvas, targetX - mappedX, targetY - mappedY);
}

function applyGlasses(ctx, landmarks, filterImage) {
  const [leftOuterX, leftOuterY] = landmarks.left_eye_outer;
  const [leftInnerX, leftInnerY] = landmarks.left_eye_inner;
  const [rightInnerX, rightInnerY] = landmarks.right_eye_inner;
  const [rightOuterX, rightOuterY] = landmarks.right_eye_outer;

  const leftEyeX = Math.floor((leftOuterX + leftInnerX) / 2);
  const leftEyeY = Math.floor((leftOuterY + leftInnerY) / 2);
  const rightEyeX = Math.floor((rightInnerX + rightOuterX) / 2);
  const rightEyeY = Math.floor((rightInnerY + rightOuterY) / 2);

  const eyeCenterX = Math.floor((leftEyeX + rightEyeX) / 2);
  const eyeCenterY = Math.floor((leftEyeY + rightEyeY) / 2);
  const eyeDistance = Math.floor(
    Math.hypot(rightEyeX - leftEyeX, rightEyeY - leftEyeY)
  );
  const angle =
    -(Math.atan2(leftEyeY - rightEyeY, rightEyeX - leftEyeX) * 180) / Math.PI;

  const glassesWidth = Math.floor(eyeDistance * 2.25);
  const aspectRatio = filterImage.naturalHeight / filterImage.naturalWidth;
  const glassesHeight = Math.floor(glassesWidth * aspectRatio);

  placeRotatedFilter(
    ctx,
    filterImage,
    glassesWidth,
    glassesHeight,
    angle,
    eyeCenterX,
    eyeCenterY,
    Math.floor(glassesWidth * 0.5),
    Math.floor(glassesHeight * 0.38)
  );
}

function applyMoustache(ctx, landmarks, filterImage) {
  const [x1, y1] = landmarks.left_mouth;
  const [x2, y2] = landmarks.right_mouth;
  const [, ny] = landmarks.nose_tip;

  const mouthWidth = Math.floor(Math.hypot(x2 - x1, y2 - y1));
  const angle = -(Math.atan2(y1 - y2, x2 - x1) * 180) / Math.PI;
  const targetX = Math.floor((x1 + x2) / 2);
  const targetY = Math.floor((ny + Math.floor((y1 + y2) / 2)) / 2) + 5;

  const moustacheWidth = Math.floor(mouthWidth * 1.4);
  const aspectRatio = filterImage.naturalHeight / filterImage.naturalWidth;
  const moustacheHeight = Math.floor(moustacheWidth * aspectRatio);

  placeRotatedFilter(
    ctx,
    filterImage,
    moustacheWidth,
    moustacheHeight,
    angle,
    targetX,
    targetY,
    Math.floor(moustacheWidth / 2),
    Math.floor(moustacheHeight / 2)
  );
}

function applyCrown(ctx, landmarks, filterImage) {
  const [x1, y1] = landmarks.left_face;
  const [x2, y2] = landmarks.right_face;
  const [fx, fy] = landmarks.forehead;

  const faceWidth = Math.floor(Math.hypot(x2 - x1, y2 - y1));
  const angle = -(Math.atan2(y1 - y2, x2 - x1) * 180) / Math.PI;
  const crownWidth = Math.floor(faceWidth * 1.2);
  const aspectRatio = filterImage.naturalHeight / filterImage.naturalWidth;
  const crownHeight = Math.floor(crownWidth * aspectRatio);

  placeRotatedFilter(
    ctx,
    filterImage,
    crownWidth,
    crownHeight,
    angle,
    fx,
    fy + 8,
    Math.floor(crownWidth / 2),
    crownHeight
  );
}

function applyCowboyHat(ctx, landmarks, filterImage) {
  const [x1, y1] = landmarks.left_face;
  const [x2, y2] = landmarks.right_face;
  const [fx, fy] = landmarks.forehead;

  const faceWidth = Math.floor(Math.hypot(x2 - x1, y2 - y1));
  const angle = -(Math.atan2(y1 - y2, x2 - x1) * 180) / Math.PI;
  const hatWidth = Math.floor(faceWidth * 1.5);
  const aspectRatio = filterImage.naturalHeight / filterImage.naturalWidth;
  const hatHeight = Math.floor(hatWidth * aspectRatio);

  placeRotatedFilter(
    ctx,
    filterImage,
    hatWidth,
    hatHeight,
    angle,
    fx,
    fy + 48,
    Math.floor(hatWidth / 2),
    hatHeight
  );
}

function applyBowTie(ctx, landmarks, filterImage) {
  const [x1, y1] = landmarks.left_mouth;
  const [x2, y2] = landmarks.right_mouth;
  const [cx, cy] = landmarks.chin;

  const tieWidth = Math.floor(Math.hypot(x2 - x1, y2 - y1) * 2);
  const angle = -(Math.atan2(y1 - y2, x2 - x1) * 180) / Math.PI;
  const aspectRatio = filterImage.naturalHeight / filterImage.naturalWidth;
  const tieHeight = Math.floor(tieWidth * aspectRatio);

  placeRotatedFilter(
    ctx,
    filterImage,
    tieWidth,
    tieHeight,
    angle,
    cx,
    cy + Math.floor(tieHeight * 0.4),
    Math.floor(tieWidth / 2),
    Math.floor(tieHeight / 2)
  );
}

function applyMood(ctx, landmarks, filterImages) {
  const [, leftMouthY] = landmarks.left_mouth;
  const [, rightMouthY] = landmarks.right_mouth;
  const [, topLipY] = landmarks.top_lip;
  const [, bottomLipY] = landmarks.bottom_lip;

  const cornerY = (leftMouthY + rightMouthY) / 2;
  const lipY = (topLipY + bottomLipY) / 2;

  // If corners are higher than lip center, it's a smile (Y goes down, so smaller Y is higher)
  const isHappy = cornerY < lipY;
  const filterImage = isHappy ? filterImages[0] : filterImages[1];

  const [lx, ly] = landmarks.left_face;
  const [rx, ry] = landmarks.right_face;

  const faceWidth = Math.floor(Math.hypot(rx - lx, ry - ly));
  
  const emojiWidth = Math.floor(faceWidth * 0.4);
  const aspectRatio = filterImage.naturalHeight / filterImage.naturalWidth;
  const emojiHeight = Math.floor(emojiWidth * aspectRatio);

  const targetX = rx + Math.floor(emojiWidth * 0.7);
  const targetY = ry - Math.floor(faceWidth * 0.2);

  // Negative angle in Canvas API is counter-clockwise (left tilt)
  const angle = -15;

  placeRotatedFilter(
    ctx,
    filterImage,
    emojiWidth,
    emojiHeight,
    angle,
    targetX,
    targetY,
    Math.floor(emojiWidth / 2),
    Math.floor(emojiHeight / 2)
  );
}

const FILTER_APPLIERS = {
  Glasses: applyGlasses,
  Moustache: applyMoustache,
  Crown: applyCrown,
  "Cowboy Hat": applyCowboyHat,
  "Bow Tie": applyBowTie,
  Mood: applyMood,
};

export function renderFilteredImage(baseImage, filterImage, filterName, landmarks) {
  const canvas = document.createElement("canvas");
  canvas.width = baseImage.naturalWidth || baseImage.width;
  canvas.height = baseImage.naturalHeight || baseImage.height;

  const ctx = canvas.getContext("2d");
  ctx.drawImage(baseImage, 0, 0, canvas.width, canvas.height);

  const applyFilter = FILTER_APPLIERS[filterName];
  if (applyFilter && landmarks) {
    applyFilter(ctx, landmarks, filterImage);
  }

  return canvas;
}
