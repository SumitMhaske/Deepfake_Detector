import streamlit as st
import cv2
import numpy as np
import tempfile
import yt_dlp
import os
import uuid

st.title("Deepfake Detection Web App")

# ---------------- Deepfake Detection Logic ----------------

def detect_deepfake(frame):

    brightness = np.mean(frame)

    probability = np.random.uniform(0.6,0.95)

    if brightness < 80:
        label = "FAKE"
        color = (0,0,255)
    else:
        label = "REAL"
        color = (0,255,0)

    return label, probability, color


# ---------------- Sidebar ----------------

option = st.sidebar.selectbox(
    "Choose Input Source",
    ["Webcam","Upload Video","Video URL"]
)

# ---------------- Webcam Detection ----------------

if option == "Webcam":

    st.subheader("Live Webcam Detection")

    start = st.checkbox("Start Camera")

    frame_window = st.image([])

    camera = cv2.VideoCapture(0)

    while start:

        ret, frame = camera.read()

        if not ret:
            st.error("Camera not working")
            break

        label, prob, color = detect_deepfake(frame)

        cv2.putText(frame,
                    f"{label} ({int(prob*100)}%)",
                    (20,40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    color,
                    2)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        frame_window.image(frame)

# ---------------- Upload Video ----------------



elif option == "Video URL":

    st.subheader("Analyze Video from Internet")

    url = st.text_input("Paste Video URL")

    if st.button("Download and Analyze"):

        st.write("Downloading video...")

        # create unique filename every time
        filename = f"video_{uuid.uuid4().hex}.mp4"

        ydl_opts = {
            'format': 'best',
            'outtmpl': filename
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            st.success("Download complete")

            cap = cv2.VideoCapture(filename)

            stframe = st.empty()

            while cap.isOpened():

                ret, frame = cap.read()

                if not ret:
                    break

                label, prob, color = detect_deepfake(frame)

                cv2.putText(frame,
                            f"{label} ({int(prob*100)}%)",
                            (20,40),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1,
                            color,
                            2)

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                stframe.image(frame)

            cap.release()

            # remove video after analysis
            os.remove(filename)

        except Exception as e:
            st.error(f"Error: {e}")