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
| **Tool use** | 4 real tools: NVIDIA Vision (image diagnosis), NVIDIA Embeddings + cosine retrieval (RAG), a live weather API, and a market price API. |
| **Multi-agent coordination** | 3 specialist agents (Diagnosis, Advisory, Market) report to 1 orchestrator agent, which synthesises their outputs into a single coherent answer. |
| **Memory** | A persistent, file-backed memory store remembers the farmer's crop, location, and recent history across turns and across app restarts. |
| **Multimodal** | Accepts photo input and reasons over it natively using NVIDIA's vision-language model. |
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
                         │ (Llama 3.3 70B via    │      (per-farmer profile,
                         │  NVIDIA NIM tool       │       crop, history)
                         │  calling, plans &      │
                         │  routes dynamically)   │
                         └──┬───────┬───────┬────┘
                            │       │       │
              ┌─────────────┘       │       └─────────────┐
              ▼                     ▼                      ▼
    ┌──────────────────┐  ┌──────────────────┐   ┌──────────────────┐
    │ Diagnosis Agent    │  │ Advisory Agent    │   │ Market Agent      │
    │ (Llama 3.2 90B     │  │ (RAG retrieval +  │   │ (Weather API +    │
    │  Vision via NIM)   │  │  Llama 3.3 70B)   │   │  Mandi price API) │
    └──────────────────┘  └──────────────────┘   └──────────────────┘
              │                     │                      │
              ▼                     ▼                      ▼
       leaf photo            local knowledge        Open-Meteo +
       → crop + disease      base (.txt docs)        mandi data
         + confidence         → embedded once,
                               searched live
```

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
│   ├── orchestrator.py          # Planning brain (NVIDIA NIM tool calling)
│   ├── diagnosis_agent.py       # Wraps the vision tool
│   ├── advisory_agent.py        # RAG-based advice synthesis
│   └── market_agent.py          # Weather + price synthesis
├── tools/
│   ├── vision_tool.py           # NVIDIA Vision leaf diagnosis
│   ├── retrieval_tool.py        # Embedding + cosine-similarity RAG
│   ├── weather_tool.py          # Open-Meteo live weather (no key needed)
│   └── market_tool.py           # Mandi price lookup (live data.gov.in + baseline)
├── utils/
│   ├── memory.py                # Persistent farmer profile/history
│   └── logger.py                # Agent reasoning trace for the UI
├── scripts/
│   └── build_vector_store.py    # Run once to embed the knowledge base
├── data/
│   ├── knowledge_base/          # 5 agri-extension guides (.txt)
│   └── sample_images/           # Sample leaf photos for the demo
└── docs/
    ├── SETUP_LINUX.md
    └── DEMO_SCRIPT.md
```

---

## 🚀 Quickstart (Linux)

See **[docs/SETUP_LINUX.md](docs/SETUP_LINUX.md)** for the full guide. Short version:

```bash
git clone https://github.com/<your-username>/agrimitra.git
cd agrimitra
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env — add your free NVIDIA NIM key from https://build.nvidia.com/
python scripts/build_vector_store.py
streamlit run app.py
```

---

## 🎥 Demo

See **[docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md)** for a ready-to-record
2-minute demo script covering all three agents + the reasoning trace.

---

## 🛠️ Tech stack

- **NVIDIA NIM** — OpenAI-compatible API (free tier)
  - `meta/llama-3.3-70b-instruct` — orchestrator reasoning, tool calling, advisory synthesis
  - `nvidia/llama-3.2-90b-vision-instruct` — multimodal leaf diagnosis
  - `nvidia/llama-3.2-nv-embedqa-1b-v2` — RAG embeddings
- **OpenAI Python SDK** — used as NVIDIA NIM client (`base_url` override)
- **Streamlit** — UI
- **Open-Meteo** — free, no-key weather API
- **data.gov.in Agmarknet API** — live mandi prices (with baseline fallback)
- **Python 3.10+**

---

## 📄 License

MIT — see [LICENSE](LICENSE).

## 🙋 About

Built by Gowri, B.Tech CST student at Viswam Engineering College, for
the Google × Kaggle AI Agents Intensive capstone, with a focus on the
agricultural context of the Madanapalle region.
