import streamlit as st
import cv2
import ollama
import time
from neo4j import GraphDatabase
import tempfile

# --- CONFIGURATION ---
# We use a session state to hold the "Brain" connections so we don't reconnect every frame
if 'neo4j_driver' not in st.session_state:
    st.session_state.neo4j_driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password123"))

# --- FUNCTIONS ---
def get_protocol(hazard):
    """Queries the Graph DB for the correct safety protocol."""
    query = """
    MATCH (h:Hazard {name: $hazard})-[:REQUIRES_ACTION]->(p:Protocol)
    RETURN p.action AS action, p.code AS code
    """
    try:
        with st.session_state.neo4j_driver.session() as session:
            result = session.run(query, hazard=hazard).single()
            if result:
                return result['action'], result['code']
            return "LOG_INCIDENT", "GRAY-0"
    except Exception:
        return "DB_ERROR", "ERR-500"

def analyze_frame(frame_path):
    """Sends frame to LLaVA."""
    response = ollama.chat(model='llava', messages=[
        {
            'role': 'user',
            'content': 'Look for hazards. If fire, reply "DETECTED: Fire". If spill, reply "DETECTED: Spill". If safe, reply "Status: Safe".',
            'images': [frame_path]
        }
    ])
    return response['message']['content'].strip()

# --- UI LAYOUT ---
st.set_page_config(page_title="Aegis Overwatch HUD", layout="wide")

# Custom CSS for the "Drone" look
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #00FF00; }
    .hazard-box { border: 2px solid red; padding: 10px; border-radius: 5px; background-color: rgba(255,0,0,0.1); }
    .safe-box { border: 2px solid green; padding: 10px; border-radius: 5px; background-color: rgba(0,255,0,0.1); }
    </style>
""", unsafe_allow_html=True)

st.title("🚁 Aegis Overwatch: Autonomous Feed")

# Sidebar for Controls
with st.sidebar:
    st.header("Flight Controls")
    video_path = "../assets/hazard_feed.mp4" # Hardcoded for demo, or add file uploader
    start_btn = st.button("🔴 LAUNCH DRONE", type="primary")
    stop_btn = st.button("LAND DRONE")

    st.divider()
    st.subheader("Telemetry")
    status_indicator = st.empty()
    protocol_display = st.empty()

# Main Video Area
video_placeholder = st.empty()
logs_placeholder = st.empty()

if start_btn:
    cap = cv2.VideoCapture(video_path)
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret or stop_btn:
            break

        # Display Video Stream (Convert BGR to RGB)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        video_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)

        # AI Analysis every 30 frames (approx every 1-2 seconds)
        if frame_count % 30 == 0:
            # Save frame for Ollama
            cv2.imwrite("temp_hud_frame.jpg", frame)

            # 1. VISION
            ai_output = analyze_frame("temp_hud_frame.jpg")

            # 2. LOGIC & UI UPDATE
            if "DETECTED:" in ai_output:
                hazard = ai_output.split("DETECTED:")[1].strip().replace(".", "")
                action, code = get_protocol(hazard)

                status_indicator.error(f"⚠️ HAZARD: {hazard}")
                protocol_display.markdown(f"**PROTOCOL:** `{action}`\n\n**CODE:** `{code}`")

                logs_placeholder.markdown(f"<div class='hazard-box'>[ALERT] {hazard} identified. Executing {code}.</div>", unsafe_allow_html=True)
            else:
                status_indicator.success("✅ SYSTEM SAFE")
                protocol_display.info("Patrolling...")
                logs_placeholder.markdown("<div class='safe-box'>[INFO] Area secure. No anomalies.</div>", unsafe_allow_html=True)

        frame_count += 1
        # Small sleep to simulate real-time playback speed if needed
        # time.sleep(0.01) 

    cap.release()