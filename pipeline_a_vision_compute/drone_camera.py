import cv2
import time
import ollama
from neo4j import GraphDatabase

# --- CONFIGURATION ---
VIDEO_PATH = "../assets/hazard_feed.mp4"
FRAME_RATE = 2  # Process 1 frame every 2 seconds
NEO4J_URI = "bolt://localhost:7687"
NEO4J_AUTH = ("neo4j", "password123")

# --- DATABASE CONNECTION ---
def get_safety_protocol(hazard_keyword):
    """Asks Neo4j what to do about a specific hazard."""
    driver = GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)
    query = """
    MATCH (h:Hazard {name: $hazard})-[:REQUIRES_ACTION]->(p:Protocol)
    RETURN p.action AS action, p.code AS code
    """
    try:
        with driver.session() as session:
            result = session.run(query, hazard=hazard_keyword).single()
            if result:
                return f"{result['action']} (Code: {result['code']})"
            return "LOG_INCIDENT (Unknown Hazard)"
    except Exception as e:
        return f"DB_ERROR: {e}"
    finally:
        driver.close()

# --- MAIN DRONE LOOP ---
print(f"🚀 LAUNCHING SMART DRONE: {VIDEO_PATH}")
cap = cv2.VideoCapture(VIDEO_PATH)

fps = cap.get(cv2.CAP_PROP_FPS)
frame_interval = int(fps * FRAME_RATE)
frame_count = 0

try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            print(f"\n[Frame {frame_count}] Analyzing...")

            # 1. SEE (Vision)
            cv2.imwrite("current_frame.jpg", frame)
            response = ollama.chat(model='llava', messages=[
                {
                    'role': 'user',
                    'content': 'Look for hazards. If you see fire, reply only "DETECTED: Fire". If you see a spill, reply "DETECTED: Spill". If safe, reply "Status: Safe".',
                    'images': ['./current_frame.jpg']
                }
            ])
            ai_output = response['message']['content'].strip()
            print(f"   👁️  VISION: {ai_output}")

            # 2. THINK (Logic)
            if "DETECTED:" in ai_output:
                # Extract the hazard name (e.g., "Fire")
                hazard = ai_output.split("DETECTED:")[1].strip().replace(".", "")

                # Query the Brain
                protocol = get_safety_protocol(hazard)

                # 3. ACT (Result)
                print(f"   🧠 LOGIC:  Hazard '{hazard}' identified.")
                print(f"   🚨 ACTION: {protocol}")
            else:
                print("   ✅ STATUS: Normal Operation")

        frame_count += 1

except KeyboardInterrupt:
    print("\n🛑 Landing Drone...")

cap.release()