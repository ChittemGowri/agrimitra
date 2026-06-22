# 🌾 AgriMitra — Multi-Agent AI Farm Advisory System

> Built for the **Google × Kaggle 5-Day AI Agents Intensive — Capstone Project**

AgriMitra is a multi-agent AI system that helps smallholder farmers near
Madanapalle, Andhra Pradesh diagnose crop diseases from a photo, get
practical treatment advice grounded in real agricultural guides, and
check live weather + market prices before deciding what to do next —
all through one conversational interface.

It is built specifically to demonstrate the core competencies of an
agentic system: **planning, tool use, multi-agent orchestration, and
persistent memory** — not just a single LLM call with a chat UI on top.

---

## 🧠 Why this is a genuine multi-agent system (not just a chatbot)

| Capability | How AgriMitra demonstrates it |
|---|---|
| **Planning** | The Orchestrator dynamically decides *which* agents to call and in *what order*, based on the farmer's actual message — there is no hardcoded if/else flow. |
| **Tool use** | 4 real tools: Gemini Vision (image diagnosis), Gemini Embeddings + cosine retrieval (RAG), a live weather API, and a market price API. |
| **Multi-agent coordination** | 3 specialist agents (Diagnosis, Advisory, Market) report to 1 orchestrator agent, which synthesizes their outputs into a single coherent answer. |
| **Memory** | A persistent, file-backed memory store remembers the farmer's crop, location, and recent history across turns and across app restarts. |
| **Multimodal** | Accepts photo input and reasons over it natively using Gemini's vision capability. |
| **Grounding** | Advice is retrieved from a real local knowledge base (agricultural extension guides) rather than hallucinated from the model's parametric memory. |

---

## 🏗️ Architecture

```
                         ┌─────────────────────┐
                         │   Streamlit UI       │
                         │   (app.py)            │
                         └──────────┬────────────┘
                                    │ farmer query + optional image
                                    ▼
                         ┌─────────────────────┐
                         │   ORCHESTRATOR        │◄──── persistent memory
                         │ (Gemini function       │      (per-farmer profile,
                         │  calling, plans &      │       crop, history)
                         │  routes dynamically)   │
                         └──┬───────┬───────┬────┘
                            │       │       │
              ┌─────────────┘       │       └─────────────┐
              ▼                     ▼                      ▼
    ┌──────────────────┐  ┌──────────────────┐   ┌──────────────────┐
    │ Diagnosis Agent    │  │ Advisory Agent    │   │ Market Agent      │
    │ (Gemini Vision)     │  │ (RAG retrieval +  │   │ (Weather API +    │
    │                     │  │  Gemini synthesis)│   │  Mandi price API) │
    └──────────────────┘  └──────────────────┘   └──────────────────┘
              │                     │                      │
              ▼                     ▼                      ▼
       leaf photo            local knowledge        Open-Meteo +
       → crop + disease      base (.txt docs)        market data
         + confidence         → embedded once,
                               searched live
```

**Flow example:** A farmer uploads a tomato leaf photo and asks "what's
wrong and should I sell my tomatoes now?" → the Orchestrator decides
this needs **two** tool calls: `diagnose_crop_image` (Diagnosis Agent)
and `check_market_and_weather` (Market Agent) → both run → the
Orchestrator synthesizes one combined answer → the conversation is
saved to memory for next time.

---

## 📁 Project structure

```
agrimitra/
├── app.py                       # Streamlit UI (entry point)
├── config.py                    # Central config (models, paths, keys)
├── requirements.txt
├── .env.example                 # Copy to .env and fill in your key
├── .gitignore
├── agents/
│   ├── orchestrator.py          # Planning brain (Gemini function calling)
│   ├── diagnosis_agent.py       # Wraps the vision tool
│   ├── advisory_agent.py        # RAG-based advice synthesis
│   └── market_agent.py          # Weather + price synthesis
├── tools/
│   ├── vision_tool.py           # Gemini Vision leaf diagnosis
│   ├── retrieval_tool.py        # Embedding + cosine-similarity RAG
│   ├── weather_tool.py          # Open-Meteo live weather (no key needed)
│   └── market_tool.py           # Mandi price lookup (simulated baseline,
│                                 #   live data.gov.in hook included)
├── utils/
│   ├── memory.py                # Persistent farmer profile/history
│   └── logger.py                # Agent reasoning trace for the UI
├── scripts/
│   └── build_vector_store.py    # Run once to embed the knowledge base
├── data/
│   ├── knowledge_base/          # 5 agri-extension guides (.txt)
│   └── sample_images/           # Sample leaf photos for the demo
└── docs/
    ├── DEPLOYMENT.md
    ├── DEMO_SCRIPT.md
    └── architecture-diagram.png (optional, see docs/)
```

---

## 🚀 Quickstart (Linux)

See **[docs/SETUP_LINUX.md](docs/SETUP_LINUX.md)** for the full,
copy-pasteable step-by-step guide. Short version:

```bash
git clone https://github.com/<your-username>/agrimitra.git
cd agrimitra
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env and add your free Gemini API key from https://aistudio.google.com/app/apikey
python scripts/build_vector_store.py
streamlit run app.py
```

Then open the URL Streamlit prints (usually `http://localhost:8501`).

---

## 🎥 Demo

See **[docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md)** for a ready-to-record
2-minute demo script covering all three agents + the reasoning trace.

---

## 🛠️ Tech stack

- **Gemini 2.5 Flash** — orchestrator reasoning, function calling, vision diagnosis, advisory synthesis
- **Gemini text-embedding-004** — RAG embeddings
- **Streamlit** — UI
- **Open-Meteo** — free, no-key weather API
- **Python 3.10+**

---

## 📄 License

MIT — see [LICENSE](LICENSE).

## 🙋 About

Built by Gowri, B.Tech CST student at Viswam Engineering College, for
the Google × Kaggle AI Agents Intensive capstone, with a focus on the
agricultural context of the Madanapalle region.
