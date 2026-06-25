# Face Filter App

A browser-based face filter web app that applies fun overlays like glasses, moustache, crown, cowboy hat, and bow tie onto faces using facial landmark detection.

This project began as a Python/OpenCV prototype and was later adapted into a **client-side React application** so the filters can run directly in the browser with a more modern UI and easier deployment.

---

## Features

* Upload your own image or try built-in sample faces
* Apply multiple face filters:

  * Glasses
  * Moustache
  * Crown
  * Cowboy Hat
  * Bow Tie
* Landmark-based filter placement for better alignment with the face
* Instant preview of the filtered image
* Download the final output image
* Browser-based frontend for a smoother user experience

---

## Tech Stack

### Frontend

* React
* Vite
* JavaScript / CSS

### Face Processing / Prototype Logic

* Python
* OpenCV
* NumPy
* MediaPipe

---

## Project Structure

```bash
Face-Filter-App/
│
├── frontend/              # Main client-side React application
│   ├── public/
│   │   ├── filters/       # PNG overlays used as filters
│   │   └── sample_faces/  # Built-in sample images
│   └── src/               # React app source code
│
├── backend/               # Earlier Python prototype / filter logic
│   ├── main.py
│   ├── filter_engine.py
│   ├── landmark_detector.py
│   └── utils.py
│
├── README.md
└── .gitignore
```

---

## How It Works

The app detects key facial landmarks (such as eye corners, mouth corners, chin, and forehead reference points) and uses them to:

1. Estimate the position of facial features
2. Resize filters according to face proportions
3. Rotate overlays to match head tilt
4. Place each filter naturally on the image

This allows filters like glasses, hats, or moustaches to adapt to the face rather than appearing as static stickers.

---

## Running the Project

### Frontend (Main Version)

Open a terminal inside the `frontend` folder and run:

```bash
npm install
npm run dev
```

Then open the local development URL shown in the terminal.

---

### Backend Prototype (Optional / Legacy)

If you want to explore the earlier Python version inside `backend/`, install the required dependencies and run it separately.

Typical dependencies include:

* opencv-python
* numpy
* mediapipe
* pillow
* streamlit (if using the older Streamlit version)

---

## Notes

* The **frontend** folder contains the current browser-based version of the project.
* The **backend** folder contains the earlier Python implementation and filter-placement logic used during development and experimentation.
* This project was built as part of hands-on learning and experimentation with computer vision, UI development, and face landmark–based image processing.

---

## Future Improvements

* Add more filters and accessories
* Support multiple faces in one image
* Improve landmark accuracy for stylized/cartoon faces
* Add webcam / live camera mode
* Add filter stacking (multiple filters at once)
* Improve mobile responsiveness

---

## Author

**Shivang Gulati**
