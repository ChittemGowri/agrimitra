# Deployment Guide - Streamlit Community Cloud (Free)

This is the fastest way to get a live, public URL for AgriMitra so
judges can try it without cloning anything.

---

## 1. Prerequisites

- Your project is already pushed to GitHub (see GITHUB_PUSH_GUIDE.md)
- You have a Gemini API key from https://aistudio.google.com/app/apikey

---

## 2. Deploy

1. Go to https://share.streamlit.io
2. Sign in with your GitHub account
3. Click "New app"
4. Choose:
   - Repository: <your-username>/agrimitra
   - Branch: main
   - Main file path: app.py
5. Click "Advanced settings" BEFORE deploying, and add your secrets:

```
GEMINI_API_KEY = "your_real_key_here"
DATA_GOV_API_KEY = ""
OPENWEATHER_API_KEY = ""
```

6. Click "Deploy"

Streamlit Cloud will install requirements.txt automatically and start
the app. First deploy takes 2-5 minutes.

---

## 3. Build the vector store on the cloud

The deployed app needs data/vector_store.json to exist for the
Advisory Agent's RAG retrieval to work. You have two options:

**Option A (recommended): commit the vector store file**

Run this locally once, then commit the generated file instead of
gitignoring it:

```bash
python scripts/build_vector_store.py
# remove the gitignore line for vector_store.json, OR force-add it:
git add -f data/vector_store.json
git commit -m "Add pre-built vector store for deployment"
git push
```

**Option B: build it at startup**

Add this near the top of app.py (after the imports) so it builds
automatically if missing -- slower first load, but always fresh:

```python
from pathlib import Path
from config import VECTOR_STORE_PATH, KB_DIR
from tools.retrieval_tool import SimpleVectorStore

if not Path(VECTOR_STORE_PATH).exists():
    with st.spinner("First-time setup: building knowledge base index..."):
        SimpleVectorStore().build_from_directory(KB_DIR)
```

Option A is simpler and faster for a capstone demo -- use that unless
you're actively editing the knowledge base often.

---

## 4. Verify the live app

Open the URL Streamlit Cloud gives you (looks like
`https://agrimitra-<random>.streamlit.app`). Test:

- A text-only farming question
- An image upload from data/sample_images/
- A combined question (image + market price)

Check the sidebar shows "Gemini API connected" in green.

---

## 5. Put the live link in your README and submission

Add this near the top of README.md:

```markdown
**Live demo:** https://your-app-url.streamlit.app
```

A working live link is one of the single highest-value things you can
add for judges -- it lets them try the agent themselves in 10 seconds
instead of reading code.

---

## 6. Free tier limits to be aware of

- Streamlit Community Cloud apps sleep after inactivity and take ~30
  seconds to wake up on the next visit -- mention this in your demo
  video so judges aren't confused by a slow first load.
- Gemini free tier has rate limits (requests per minute). For a judged
  demo with a handful of test queries this is not a concern, but avoid
  hammering it with rapid repeated requests right before judging.
