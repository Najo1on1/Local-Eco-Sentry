# 🚁 Efficiency Route: Aegis Overwatch

**Autonomous Drone Safety Pipeline with Edge Vision & Graph Intelligence**

This repo demonstrates a sophisticated "Cognitive Drone" architecture designed for high-stakes industrial monitoring. By combining **Edge AI** (Ollama/LLaVA) with **Graph Relations** (Neo4j), the system transforms raw video pixels into codified emergency responses without requiring human intervention.

## 🏗️ System Architecture

The project is divided into three distinct pipelines that handle the transition from raw visual data to actionable safety protocols.

1. **Pipeline A: Vision Compute** – Utilizes OpenCV to capture frames from drone feeds and processes them using the **LLaVA** model via **Ollama**.
2. **Pipeline B: Safety Logic** – A **Neo4j Graph Database** that acts as the "Cognitive Brain," mapping specific hazards to industrial safety protocols.
3. **Pipeline C: Drone HUD** – A **Streamlit** dashboard that provides a real-time Heads-Up Display (HUD) for telemetry and incident logging.

## 🧠 The "See-Think-Act" Loop

The system operates on a continuous feedback loop to ensure zero-latency response times:

* **See:** OpenCV extracts frames from `hazard_feed.mp4` and saves them for analysis.
* **Think:** The LLaVA model identifies environmental anomalies (e.g., Fire, Spills).
* **Act:** The system queries Neo4j for the mandated safety action (e.g., `TRIGGER_EVACUATION`) and updates the HUD.

## 📂 Project Structure

```text
efficiency_route_Ollama/
├── assets/                        # Raw video feeds (Hazard/Safe)
├── images/                        # System diagrams and documentation
├── pipeline_a_vision_compute/     # OpenCV & Ollama integration scripts
├── pipeline_b_safety_logic/       # Neo4j Docker config & rule ingestion
└── pipeline_c_drone_hud/          # Streamlit dashboard & UI assets

```

## 🔄 Operational Sequence

The system follows a strict execution path for every frame processed:

1. **Ingestion**: `drone_camera.py` captures frames from the asset library.
2. **Inference**: The vision-language model (LLaVA) performs zero-shot detection on the frame.
3. **Graph Query**: The detected hazard is used to traverse the Neo4j graph to find the appropriate protocol.
4. **UI Feedback**: The `dashboard.py` HUD triggers a visual alarm and logs the action.

## 🚀 Quick Start

1. **Start the Database:**
```bash
docker-compose -f pipeline_b_safety_logic/docker-compose.yaml up -d
python pipeline_b_safety_logic/init_rules.py

```


2. **Launch the HUD:**
```bash
streamlit run pipeline_c_drone_hud/dashboard.py

```