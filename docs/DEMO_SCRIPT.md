# AgriMitra — 2-Minute Demo Script

Use this script when recording your capstone demo video.

---

## Setup before recording
1. App is running: `streamlit run app.py`
2. Browser open at `http://localhost:8501`
3. Have a sample tomato leaf image ready (use any from `data/sample_images/`)

---

## Demo flow (2 minutes)

### 0:00 — Introduction (15 sec)
"This is AgriMitra — a multi-agent AI system built for smallholder farmers
near Madanapalle, Andhra Pradesh. It combines three specialist agents
coordinated by a planning orchestrator, all running on NVIDIA NIM."

Point to the sidebar architecture panel.

### 0:15 — Disease diagnosis (30 sec)
Upload the tomato leaf image.
Type: "What's wrong with this tomato leaf?"
Click Ask AgriMitra.

"Watch the right panel — the Orchestrator decides it needs the Diagnosis
Agent, calls the Vision model, and you can see every reasoning step live."

### 0:45 — Market + weather query (30 sec)
Type: "Should I sell my groundnut this week?"
Click Ask AgriMitra.

"Now the Orchestrator routes to the Market Agent — it fetches live weather
from Open-Meteo and mandi prices, then synthesises a sell/hold recommendation."

### 1:15 — Combined query (30 sec)
Type: "My tomato crop has spots and I want to know the tomato price."
Click Ask AgriMitra.

"Here the Orchestrator plans TWO tool calls in one turn — Diagnosis AND
Market — and combines both results into one coherent answer."

### 1:45 — Memory (15 sec)
Type: "What was wrong with my crop again?"
Show that AgriMitra remembers the diagnosis from earlier in the session.

"The persistent memory means farmers don't have to repeat themselves
every time they come back."

---

## Key talking points
- NVIDIA NIM OpenAI-compatible API: one SDK, three models
- Tool calling = real dynamic planning, not hardcoded if/else
- RAG grounds advice in real AP agricultural extension documents
- Open-Meteo + data.gov.in = genuinely live data
- Runs on a laptop — no GPU required
