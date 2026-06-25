# Bitmoji Filter App

## Overview

This is a Streamlit-based Bitmoji Filter App that applies fun face filters to sample Bitmoji avatars or uploaded images.

The app uses facial landmark detection to place filters correctly on the face.

## Features

- Upload your own image or use built-in Bitmoji samples
- Apply multiple filters:
  - Glasses
  - Moustache
  - Crown
  - Cowboy Hat
  - Bow Tie

- Preview the filtered image instantly
- Download the final output image

## Files in the Project

- `app.py` → main Streamlit app
- `filter_engine.py` → applies the filters on the face
- `landmark_detector.py` → detects facial landmarks
- `utils.py` → helper functions for image overlay and rotation
- `filters/` → contains filter PNG images
- `sample_faces/` → contains sample Bitmoji images

## Python Compatibility

This project is tested on **Python 3.11 / 3.12**.

Recommended version: **Python 3.11** for the most predictable dependency compatibility.

## How to Run

1. Open terminal in the project folder
2. Install dependencies:

   ```bash
   pip install streamlit opencv-python numpy pillow mediapipe
   ```

3. Run the app:

   ```bash
   streamlit run app.py
   ```

## Usage

- Choose **Sample** or **Upload**
- Select a Bitmoji sample or upload your own image
- Click a filter button to apply a filter
- Download the final filtered image if needed

## Author

Shivang Gulati
