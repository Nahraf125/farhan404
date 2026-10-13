import streamlit as st
from ultralytics import YOLO
import cv2
import tempfile
from PIL import Image
import numpy as np
import os
import subprocess
import imageio_ffmpeg



# Page configuration
st.set_page_config(
    page_title="Fire & Smoke Detection System",
    page_icon="🔥",
    layout="wide"
)

# Title and description
st.title("🔥 Real-Time Fire & Smoke Detection System")
st.write("A YOLOv8-powered web application to detect fire and smoke in images and videos.")

# Load YOLO model with explicit local path
@st.cache_resource
def load_model():
    # Adjust your absolute path here if needed
    model_path = 'best.pt'
    model = YOLO(model_path)
    return model

try:
    model = load_model()
except Exception as e:
    st.error(f"Error loading model: {e}")

# Sidebar for options
st.sidebar.title("Configuration")
app_mode = st.sidebar.selectbox("Choose the Mode", ["About Project", "Image Detection", "Video Detection"])

CONFIDENCE = 0.05   # fixed threshold, user change nahi kar sakta
st.sidebar.markdown(f"**Confidence Threshold:** `{CONFIDENCE}` (fixed)")

if app_mode == "About Project":
    st.markdown("""
    ### About this App:
    - **Model:** YOLOv8 Small (`yolov8s`)
    - **Classes:** Fire, Smoke
    - **Purpose:** Early detection of fire hazards to prevent accidents.
    """)

elif app_mode == "Image Detection":
    st.subheader("Upload an Image for Detection")
    uploaded_image = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    
    if uploaded_image is not None:
        image = Image.open(uploaded_image)
        st.image(image, caption='Uploaded Image', use_container_width=True)
        
        if st.button("Detect Fire & Smoke"):
            with st.spinner("Analyzing image..."):
                # Run prediction
                results = model(image, conf=CONFIDENCE)
                res_plotted = results[0].plot()
                res_rgb = cv2.cvtColor(res_plotted, cv2.COLOR_BGR2RGB)
                
                st.subheader("Detection Result")
                st.image(res_rgb, caption='Processed Image', use_container_width=True)

elif app_mode == "Video Detection":
    st.subheader("Upload a Video for Detection")
    uploaded_video = st.file_uploader("Choose a video...", type=["mp4", "avi", "mov"])

    if uploaded_video is not None:
        tmpdir = tempfile.mkdtemp()
        in_path = os.path.join(tmpdir, "input.mp4")
        raw_path = os.path.join(tmpdir, "raw.mp4")
        out_path = os.path.join(tmpdir, "output.mp4")

        with open(in_path, "wb") as f:       # with se file poori tarah save aur close hoti hai
            f.write(uploaded_video.read())

        if st.button("Process Video"):
            cap = cv2.VideoCapture(in_path)
            fps = cap.get(cv2.CAP_PROP_FPS) or 25
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            writer = cv2.VideoWriter(raw_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
            bar = st.progress(0)
            i = 0

            while cap.isOpened():
                ok, frame = cap.read()
                if not ok:
                    break
                res = model.predict(frame, conf=CONFIDENCE, imgsz=640, verbose=False)
                writer.write(res[0].plot())      # plot() BGR deta hai, writer ko BGR hi chahiye
                i += 1
                if total > 0:
                    bar.progress(min(i / total, 1.0))

            cap.release()
            writer.release()

            # H.264 mein convert, taake browser mein chale
            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
            subprocess.run(
                [ffmpeg, "-y", "-i", raw_path, "-vcodec", "libx264",
                 "-pix_fmt", "yuv420p", out_path],
                check=True,
            )

            st.success("Video Processing Complete!")
            st.video(out_path)
