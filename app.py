import argparse
import os
import time
from pathlib import Path
from flask import Flask, render_template, request, send_from_directory, Response, abort, jsonify
from werkzeug.utils import secure_filename
import cv2
from ultralytics import YOLO
from config.paths_config import *
import base64
import numpy as np
from io import BytesIO
from PIL import Image

# ---- Config ----
UPLOAD_DIR = Path(__file__).parent / "uploads"
DETECT_DIR = Path("runs") / "detect"
ALLOWED_EXT = {"jpg", "jpeg", "png", "mp4"}
OUTPUT_VIDEO = Path("output.mp4")

UPLOAD_DIR.mkdir(exist_ok=True, parents=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB

model = YOLO(MODEL_PATH)


def allowed(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


def latest_detection_file():
    if not DETECT_DIR.exists():
        return None
    subfolders = [p for p in DETECT_DIR.iterdir() if p.is_dir()]
    if not subfolders:
        return None
    latest = max(subfolders, key=lambda p: p.stat().st_ctime)
    files = list(latest.glob("*"))
    return max(files, key=lambda p: p.stat().st_ctime) if files else None


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")

    # POST - handle upload
    if "file" not in request.files:
        abort(400, "No file part")
    f = request.files["file"]
    if f.filename == "":
        abort(400, "Empty filename")
    if not allowed(f.filename):
        abort(400, "Unsupported file type")

    filename = secure_filename(f.filename)
    filepath = UPLOAD_DIR / filename
    f.save(str(filepath))

    ext = filename.rsplit(".", 1)[1].lower()

    if ext in {"jpg", "jpeg", "png"}:
        # Run detection on image
        model.predict(
            source=str(filepath),
            save=True,
            exist_ok=True
        )
        return result()

    if ext == "mp4":
        process_video(filepath)
        return Response(stream_video_frames(str(OUTPUT_VIDEO)),
                        mimetype='multipart/x-mixed-replace; boundary=frame')

    abort(400, "Unhandled file type")


@app.route("/result")
def result():
    det_file = latest_detection_file()
    if not det_file:
        abort(404, "No detections yet")
    return send_from_directory(det_file.parent, det_file.name)


@app.route("/predict_webcam", methods=["POST"])
def predict_webcam():
    data = request.get_json()
    if not data or "image" not in data:
        return jsonify({"error": "No image"}), 400

    # Decode base64 image
    img_data = data["image"].split(",")[1]
    img_bytes = base64.b64decode(img_data)
    img = Image.open(BytesIO(img_bytes)).convert("RGB")
    frame = np.array(img)
    # Convert RGB to BGR
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    # Run YOLO prediction
    results = model(frame)
    annotated = results[0].plot()

    # Encode annotated image to base64
    _, buf = cv2.imencode(".jpg", annotated)
    pred_b64 = base64.b64encode(buf).decode("utf-8")
    return jsonify({"predicted": "data:image/jpeg;base64," + pred_b64})


def process_video(video_path: Path):
    # Remove previous output if present
    if OUTPUT_VIDEO.exists():
        try:
            OUTPUT_VIDEO.unlink()
        except OSError:
            pass

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError("Cannot open video")

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(str(OUTPUT_VIDEO), fourcc, fps, (w, h))

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        results = model(frame)
        annotated = results[0].plot()
        out.write(annotated)

    cap.release()
    out.release()


def stream_video_frames(video_path: str):
    cap = cv2.VideoCapture(video_path)
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            ok, buf = cv2.imencode(".jpg", frame)
            if not ok:
                continue
            yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" +
                   buf.tobytes() + b"\r\n")
            time.sleep(0.03)
    finally:
        cap.release()
        # Delete the video after streaming completes
        try:
            if OUTPUT_VIDEO.exists():
                OUTPUT_VIDEO.unlink()
        except OSError:
            pass


@app.route("/video_feed")
def video_feed():
    if not OUTPUT_VIDEO.exists():
        abort(404, "No processed video")
    return Response(stream_video_frames(str(OUTPUT_VIDEO)),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/live_feed")
def live_feed():
    return Response(stream_webcam(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def stream_webcam():
    cap = cv2.VideoCapture(0)
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        ok, buf = cv2.imencode(".jpg", frame)
        if not ok:
            continue
        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buf.tobytes() + b"\r\n")
        time.sleep(0.03)
    cap.release()


def parse_args():
    parser = argparse.ArgumentParser(description="Flask app exposing YOLO model")
    parser.add_argument("--port", default=5000, type=int)
    parser.add_argument("--host", default="0.0.0.0")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    app.run(host=args.host, port=args.port, debug=False)