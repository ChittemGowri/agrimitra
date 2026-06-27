# AgriMitra — Setup Guide (Linux / Linux Mint)

## Prerequisites
- Python 3.10 or higher
- Git
- A free NVIDIA NIM API key: https://build.nvidia.com/ → Sign in → **Get API Key**

---

## Step-by-step setup

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/agrimitra.git
cd agrimitra

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your API key
cp .env.example .env
nano .env          # paste your NVIDIA_API_KEY value and save (Ctrl+O, Enter, Ctrl+X)

# 5. Build the RAG vector store (run once)
python scripts/build_vector_store.py

# 6. Launch the app
streamlit run app.py
```

Open the URL Streamlit prints — usually `http://localhost:8501`.

---

## Getting a free NVIDIA NIM API key

1. Go to https://build.nvidia.com/
2. Click **Sign In** (create an account if needed — it's free)
3. After signing in, click **Get API Key** in the top-right corner
4. Copy the key (starts with `nvapi-…`)
5. Paste it into your `.env` file as `NVIDIA_API_KEY=nvapi-...`

The free tier includes a generous credit allowance — more than enough
for development, testing, and the demo.

---

## Models used (all on NVIDIA NIM free tier)

| Role | Model |
|---|---|
| Orchestrator + Advisory | `meta/llama-3.3-70b-instruct` |
| Vision / Diagnosis | `nvidia/llama-3.2-90b-vision-instruct` |
| RAG Embeddings | `nvidia/llama-3.2-nv-embedqa-1b-v2` |

All accessed via the OpenAI-compatible endpoint at `https://integrate.api.nvidia.com/v1`.

---

## Troubleshooting

**`ModuleNotFoundError: No module named 'openai'`**
```bash
pip install openai
```

**`NVIDIA_API_KEY not set` error in the app**
Make sure you created `.env` from `.env.example` and it's in the project root.

**Vector store empty / RAG not working**
Run `python scripts/build_vector_store.py` — it only needs to be run once.
The script reads all `.txt` files in `data/knowledge_base/`.

**`Connection error` on market price lookup**
The live data.gov.in API sometimes throttles. The app automatically falls
back to baseline prices — no action needed.
