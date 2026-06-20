# 🐧 Step-by-Step Setup Guide — Linux

This guide assumes a fresh Ubuntu/Debian-based machine (or WSL). Every
command is copy-pasteable in order.

---

## 1. Prerequisites

```bash
# Check Python version (need 3.10+)
python3 --version

# If you don't have Python 3.10+, install it:
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git
```

---

## 2. Get a free Gemini API key

1. Go to **https://aistudio.google.com/app/apikey**
2. Sign in with your Google account
3. Click **"Create API key"**
4. Copy the key — you'll paste it into `.env` in step 5

(Free tier is enough for building and demoing this project.)

---

## 3. Clone the repository

If you've already pushed this project to your own GitHub (see
`docs/GITHUB_PUSH_GUIDE.md`), clone it:

```bash
git clone https://github.com/<your-username>/agrimitra.git
cd agrimitra
```

If you're starting from the files Claude generated locally, just `cd`
into that folder instead.

---

## 4. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Your terminal prompt should now start with `(.venv)`. Every command
below assumes this is active — if you open a new terminal, re-run
`source .venv/bin/activate` first.

---

## 5. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs Streamlit, the Gemini SDK (`google-genai`), Pillow,
requests, and python-dotenv.

---

## 6. Configure your API key

```bash
cp .env.example .env
nano .env        # or: vim .env / code .env
```

Replace `your_gemini_api_key_here` with the real key from step 2, then
save and exit (`Ctrl+O`, `Enter`, `Ctrl+X` in nano).

---

## 7. Build the knowledge base index (one-time step)

This embeds the agricultural guides in `data/knowledge_base/` so the
Advisory Agent can retrieve from them. Run it once now, and again any
time you edit/add `.txt` files in that folder:

```bash
python scripts/build_vector_store.py
```

You should see:
```
Found 5 knowledge base file(s) in .../data/knowledge_base
Embedding and building vector store... (this calls the Gemini API)
Done. Indexed XX chunks.
Saved to: .../data/vector_store.json
```

---

## 8. Run the app

```bash
streamlit run app.py
```

Streamlit will print a local URL, typically:

```
Local URL: http://localhost:8501
```

Open that in your browser. If you're on a remote server/VM, use the
**Network URL** Streamlit also prints, or set up port forwarding:

```bash
ssh -L 8501:localhost:8501 user@your-remote-host
```

---

## 9. Try it out

- Upload a leaf photo from `data/sample_images/` (or any plant photo)
  and ask: *"What's wrong with this leaf?"*
- Ask a text-only question: *"How do I treat early blight on tomato?"*
- Try a combined query: *"Is it safe to spray this week, and what's
  groundnut selling for right now?"*
- Watch the **Agent Reasoning Trace** panel on the right — this shows
  exactly which agent(s) the Orchestrator decided to call and why.

---

## 10. Common issues

| Problem | Fix |
|---|---|
| `GEMINI_API_KEY not set` warning in sidebar | Check `.env` has the key with no quotes, no extra spaces |
| `ModuleNotFoundError` | Make sure `.venv` is activated (`source .venv/bin/activate`) |
| Knowledge base errors / "not built yet" | Run `python scripts/build_vector_store.py` |
| Port 8501 already in use | `streamlit run app.py --server.port 8502` |
| Weather lookup fails | Check internet access to `api.open-meteo.com` (no key needed, but does need outbound internet) |

---

## 11. Stopping the app

Press `Ctrl+C` in the terminal running Streamlit. To deactivate the
virtual environment afterward:

```bash
deactivate
```

Next time, you only need steps 4 (activate), and 8 (run) — skip
reinstalling unless `requirements.txt` changed.
