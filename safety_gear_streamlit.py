import cv2
import math
import os
import torch
from ultralytics import YOLO
import streamlit as st
from datetime import datetime
import time

# Set current directory and paths
CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(CURRENT_FOLDER, "."))
current_dir = os.getcwd()

video_path = './video/8487018-uhd_2160_3840_30fps.mp4'
model_path = f"{current_dir}/safty_gear_70e.pt"
rtsp_url = "rtsp://admin:admin123@182.0.21.83:554/stream1"

# Load YOLO model
model = YOLO(model_path)
class_names = model.names

# Define class colors for bounding boxes
class_colors = {
    'Glass': (0, 0, 204),
    'Gloves': (204, 0, 204),
    'Goggles': (0, 0, 204),
    'Helmet': (0, 255, 255),
    'No-Helmet': (64, 64, 64),
    'No-Vest': (64, 64, 64),
    'Person': (160, 160, 160),
    'Safety-Boot': (0, 51, 102),
    'Safety-Vest': (102, 255, 255),
    'Vest': (102, 255, 255),
    'helmet': (0, 0, 255),
    'no helmet': (64, 64, 64),
    'no vest': (64, 64, 64),
    'no_helmet': (64, 64, 64),
    'no_vest': (64, 64, 64),
    'protective_suit': (102, 255, 255),
    'vest': (102, 255, 255),
    'worker': (0, 153, 0)
}

st.logo(f"{current_dir}/img/finterlabs logo.png")
st.title("CCTV Dashboard")
st.header("Real-time CCTV Feed")

# logo_path = f"{current_dir}/img/finterlabs logo.png"


# Function to process each video frame
def process_frame(img):
    mps_device = torch.device("mps")
    results = model(img, stream=True, device=mps_device)
    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            conf = math.ceil((box.conf[0] * 100)) / 100
            cls = int(box.cls[0])
            current_class = class_names[cls]
            print(f'class_names  = {current_class}')

            color = class_colors.get(current_class, (255, 0, 0))

            if conf >= 0.75:
                cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
                cv2.putText(img, f'{current_class} {conf}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    return img

# Stream video function using Streamlit
def stream_video():
    # Dropdown to select video source
    source_option = st.sidebar.selectbox("Select Video Source", ("Webcam", "RTSP Stream", "Sample Video"))
    if source_option == "Webcam":
        video_source = 0
    elif source_option == "Sample Video":
        video_source = video_path
    else:
        video_source = st.text_input("Enter Video URL", rtsp_url)

    frame_placeholder = st.empty()
    if 'stop_play' not in st.session_state:
        st.session_state.stop_play = False
    # Button to toggle state
    if st.button("stop/play"):
        st.session_state.stop_play = not st.session_state.stop_play

    cap = None
    
    if source_option == "Webcam" or source_option == "Sample Video":
        cap = cv2.VideoCapture(video_source)
    elif video_source:
        cap = cv2.VideoCapture(video_source)

    if cap is None or not cap.isOpened():
        st.error("Error: Could not open video source.")
        return

    paused = False
    # stop_streaming = False
    if st.session_state.stop_play:
        paused = False
    else:
        paused = True

    while cap.isOpened():
        if not paused:
            success, img = cap.read()
            if not success:
                st.error("Error: Could not read frame.")
                break

            img = process_frame(img)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            frame_placeholder.image(img, channels="RGB")

            # Wait for a short duration to simulate real-time frame processing
            time.sleep(0.1)

    cap.release()

if __name__ == "__main__":
    stream_video()
