import { useEffect, useMemo, useRef, useState } from "react";
import { detectFaceLandmarks, initFaceLandmarker } from "./faceDetection";
import { renderFilteredImage } from "./filterEngine";
import "./App.css";

const sampleImages = [
  {
    key: "2d_male",
    label: "2D Male",
    file: "/sample_faces/2d_bitmoji_male.jpg",
  },
  {
    key: "2d_female",
    label: "2D Female",
    file: "/sample_faces/2d_bitmoji_female.jpg",
  },
  {
    key: "3d_male",
    label: "3D Male",
    file: "/sample_faces/3d_bitmoji_male.jpg",
  },
  {
    key: "3d_female",
    label: "3D Female",
    file: "/sample_faces/3d_bitmoji_female.jpg",
  },
];

const filters = [
  { name: "Glasses", file: "/filters/glasses.png" },
  { name: "Moustache", file: "/filters/moustache.png" },
  { name: "Crown", file: "/filters/crown.png" },
  { name: "Cowboy Hat", file: "/filters/cowboy_hat.png" },
  { name: "Bow Tie", file: "/filters/bow_tie.png" },
  { name: "Mood", file: ["/filters/happy.png", "/filters/sad.png"] },
];

const MAX_CANVAS_WIDTH = 820;
const MAX_CANVAS_HEIGHT = 620;

function App() {
  const canvasRef = useRef(null);

  const [selectedSample, setSelectedSample] = useState("2d_male");
  const [sourceType, setSourceType] = useState("sample");
  const [uploadedFile, setUploadedFile] = useState(null);
  const [uploadedPreview, setUploadedPreview] = useState(null);
  const [selectedFilter, setSelectedFilter] = useState("Glasses");
  const [modelReady, setModelReady] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const activeImageSrc = useMemo(() => {
    if (sourceType === "upload" && uploadedPreview) return uploadedPreview;
    const sample = sampleImages.find((item) => item.key === selectedSample);
    return sample ? sample.file : null;
  }, [sourceType, uploadedPreview, selectedSample]);

  const activeFilterSrc = useMemo(() => {
    const item = filters.find((filter) => filter.name === selectedFilter);
    return item ? item.file : null;
  }, [selectedFilter]);

  useEffect(() => {
    let cancelled = false;

    initFaceLandmarker()
      .then(() => {
        if (!cancelled) setModelReady(true);
      })
      .catch((err) => {
        console.error(err);
        if (!cancelled) {
          setError("Could not load the face tracking model.");
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const handleSampleSelect = (sample) => {
    setSourceType("sample");
    setUploadedFile(null);
    setUploadedPreview(null);
    setSelectedSample(sample.key);
    setError("");
  };

  const handleUpload = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setSourceType("upload");
    setUploadedFile(file);
    setUploadedPreview(URL.createObjectURL(file));
    setError("");
  };

  const drawToPreviewCanvas = (sourceCanvas) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const scale = Math.min(
      MAX_CANVAS_WIDTH / sourceCanvas.width,
      MAX_CANVAS_HEIGHT / sourceCanvas.height,
      1
    );

    canvas.width = Math.round(sourceCanvas.width * scale);
    canvas.height = Math.round(sourceCanvas.height * scale);

    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(sourceCanvas, 0, 0, canvas.width, canvas.height);
  };

  useEffect(() => {
    if (!modelReady || !activeImageSrc || !activeFilterSrc) return;

    let cancelled = false;

    const applyFilter = async () => {
      setLoading(true);
      setError("");

      try {
        const srcs = Array.isArray(activeFilterSrc) ? activeFilterSrc : [activeFilterSrc];
        const [baseImage, ...filterImages] = await Promise.all([
          loadImage(activeImageSrc),
          ...srcs.map(loadImage),
        ]);

        if (cancelled) return;

        const landmarks = await detectFaceLandmarks(baseImage);

        if (cancelled) return;

        if (!landmarks) {
          setError("No face detected in this image.");
          drawToPreviewCanvas(toCanvas(baseImage));
          return;
        }

        const resultCanvas = renderFilteredImage(
          baseImage,
          filterImages.length === 1 ? filterImages[0] : filterImages,
          selectedFilter,
          landmarks
        );

        if (cancelled) return;

        drawToPreviewCanvas(resultCanvas);
      } catch (err) {
        console.error(err);
        if (!cancelled) {
          setError("Could not apply filter to this image.");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    };

    applyFilter();

    return () => {
      cancelled = true;
    };
  }, [
    modelReady,
    activeImageSrc,
    activeFilterSrc,
    selectedFilter,
    sourceType,
  ]);

  useEffect(() => {
    return () => {
      if (uploadedPreview) URL.revokeObjectURL(uploadedPreview);
    };
  }, [uploadedPreview]);

  const handleDownload = () => {
    if (!canvasRef.current) return;

    const link = document.createElement("a");
    link.download = "bitmoji_filtered.png";
    link.href = canvasRef.current.toDataURL("image/png");
    link.click();
  };

  return (
    <div className="page">
      <div className="app-card">
        <div className="left-panel">
          <div className="brand">
            <h1>Bitmoji Filter App</h1>
            <p>Browser face tracking with MediaPipe — no Python required</p>
          </div>

          <div className="section">
            <h3>Choose a Sample</h3>
            <div className="sample-grid">
              {sampleImages.map((sample) => (
                <button
                  key={sample.key}
                  className={`sample-card ${
                    sourceType === "sample" && selectedSample === sample.key
                      ? "active"
                      : ""
                  }`}
                  onClick={() => handleSampleSelect(sample)}
                >
                  <img src={sample.file} alt={sample.label} />
                  <span>{sample.label}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="section">
            <h3>Or Upload an Image</h3>
            <label className="upload-box">
              <input type="file" accept="image/*" onChange={handleUpload} />
              <span>{uploadedFile ? uploadedFile.name : "Choose Image"}</span>
            </label>
          </div>

          <div className="section">
            <h3>Filters</h3>
            <div className="filter-grid">
              {filters.map((filter) => (
                <button
                  key={filter.name}
                  className={`filter-btn ${
                    selectedFilter === filter.name ? "active" : ""
                  }`}
                  onClick={() => setSelectedFilter(filter.name)}
                >
                  {filter.name}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="right-panel">
          <div className="preview-header">
            <h2>Preview</h2>
            <p>
              Current Filter: <strong>{selectedFilter}</strong>
            </p>
          </div>

          <div className="preview-box">
            {activeImageSrc ? (
              <>
                {(!modelReady || loading) && (
                  <div className="status-text">
                    {!modelReady
                      ? "Loading face tracking model..."
                      : "Applying filter..."}
                  </div>
                )}
                <canvas
                  ref={canvasRef}
                  className="preview-canvas"
                  style={{ display: !modelReady || loading ? "none" : "block" }}
                />
              </>
            ) : (
              <div className="status-text">
                Choose a sample or upload an image
              </div>
            )}
          </div>

          {error && <div className="error-box">{error}</div>}

          <button className="download-btn" onClick={handleDownload}>
            Download Image
          </button>
        </div>
      </div>
    </div>
  );
}

function loadImage(src) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = src;
  });
}

function toCanvas(image) {
  const canvas = document.createElement("canvas");
  canvas.width = image.naturalWidth || image.width;
  canvas.height = image.naturalHeight || image.height;
  canvas.getContext("2d").drawImage(image, 0, 0);
  return canvas;
}

export default App;
