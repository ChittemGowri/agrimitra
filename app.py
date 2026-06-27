"""
app.py — AgriMitra Streamlit front end.
Run with: streamlit run app.py
"""
 
import uuid
import os
import streamlit as st
from pathlib import Path
 
# ── Inject Streamlit secrets into env BEFORE importing config ──────────
# This ensures NVIDIA_API_KEY is available when config.py reads os.getenv()
for _k, _v in st.secrets.items():
    if isinstance(_v, str):
        os.environ.setdefault(_k, _v)
 
from config import APP_NAME, NVIDIA_API_KEY, SUPPORTED_LANGUAGES, TRACKED_CROPS
from utils.logger import AgentTrace
from agents.orchestrator import handle_farmer_query
 
st.set_page_config(
    page_title=f"{APP_NAME} | AI Farm Advisory Agent",
    page_icon="🌾",
    layout="wide",
)
 
# ── Colorful, vibrant theme ────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
 
:root {
    --green-dark:   #1a6b2f;
    --green-mid:    #2d9e4f;
    --green-light:  #5ccc7a;
    --orange:       #ff6b35;
    --yellow:       #ffd23f;
    --sky:          #4ecdc4;
    --purple:       #a855f7;
    --bg:           #f0fdf4;
    --card:         #ffffff;
    --text-dark:    #1a2e1a;
}
 
html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}
 
.stApp {
    background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 50%, #f0f9ff 100%);
}
 
/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a6b2f 0%, #145226 40%, #0f3d1e 100%) !important;
    border-right: 3px solid #2d9e4f;
}
section[data-testid="stSidebar"] * {
    color: #ffffff !important;
}
section[data-testid="stSidebar"] .stSelectbox label {
    color: #a7f3d0 !important;
    font-weight: 600;
}
 
/* ── Header banner ── */
.main-header {
    background: linear-gradient(135deg, #1a6b2f, #2d9e4f, #4ecdc4);
    border-radius: 16px;
    padding: 1.5rem 2rem;
    margin-bottom: 1.5rem;
    color: white;
    box-shadow: 0 4px 20px rgba(45,158,79,0.3);
}
.main-header h1 {
    color: white !important;
    font-size: 2.2rem;
    font-weight: 700;
    margin: 0;
}
.main-header p {
    color: #d1fae5 !important;
    margin: 0.3rem 0 0 0;
    font-size: 1rem;
}
 
/* ── Section cards ── */
.section-card {
    background: white;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    border-top: 4px solid #2d9e4f;
}
 
/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #1a6b2f, #2d9e4f) !important;
    color: white !important;
    border-radius: 10px !important;
    border: none !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    padding: 0.6rem 1.5rem !important;
    box-shadow: 0 4px 12px rgba(45,158,79,0.35) !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #ff6b35, #ffd23f) !important;
    color: #1a2e1a !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 18px rgba(255,107,53,0.4) !important;
}
 
/* ── Trace panel ── */
.trace-panel {
    background: linear-gradient(135deg, #fefce8, #fff7ed);
    border-left: 5px solid #ffd23f;
    border-radius: 10px;
    padding: 1.2rem;
    font-size: 0.85rem;
    box-shadow: 0 2px 10px rgba(255,210,63,0.15);
}
 
/* ── Answer card ── */
.answer-card {
    background: linear-gradient(135deg, #f0fdf4, #ecfdf5);
    border-left: 5px solid #2d9e4f;
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    font-size: 1rem;
    line-height: 1.7;
    box-shadow: 0 2px 10px rgba(45,158,79,0.12);
    margin-bottom: 0.8rem;
}
 
/* ── Farmer bubble ── */
.farmer-bubble {
    background: linear-gradient(135deg, #eff6ff, #dbeafe);
    border-left: 5px solid #4ecdc4;
    border-radius: 10px;
    padding: 0.8rem 1.2rem;
    font-size: 0.95rem;
    margin-bottom: 0.5rem;
    box-shadow: 0 2px 8px rgba(78,205,196,0.12);
}
 
/* ── Subheaders ── */
h2, h3 {
    color: #1a6b2f !important;
    font-weight: 700 !important;
}
 
/* ── Badge chips ── */
.badge {
    display: inline-block;
    padding: 0.2rem 0.7rem;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    margin: 0.2rem;
}
.badge-green  { background: #dcfce7; color: #166534; }
.badge-orange { background: #ffedd5; color: #9a3412; }
.badge-blue   { background: #dbeafe; color: #1e40af; }
.badge-purple { background: #f3e8ff; color: #6b21a8; }
 
/* ── Sidebar status indicator ── */
.status-connected {
    background: linear-gradient(135deg, #059669, #10b981);
    color: white !important;
    padding: 0.6rem 1rem;
    border-radius: 10px;
    font-weight: 700;
    text-align: center;
    box-shadow: 0 2px 8px rgba(5,150,105,0.4);
}
.status-error {
    background: linear-gradient(135deg, #dc2626, #ef4444);
    color: white !important;
    padding: 0.6rem 1rem;
    border-radius: 10px;
    font-weight: 700;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)
 
# ── Session state ──────────────────────────────────────────────────────
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_trace" not in st.session_state:
    st.session_state.last_trace = None
 
# Re-read key live from secrets in case config loaded before secrets were injected
_live_key = st.secrets.get("NVIDIA_API_KEY", NVIDIA_API_KEY)
 
# ── Sidebar ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌾 AgriMitra")
    st.markdown("*Multi-agent AI farm advisor*")
    st.markdown("---")
 
    st.markdown("### 🏆 Built for")
    st.markdown("Google × Kaggle **AI Agents Intensive** Capstone 2026")
    st.markdown("---")
 
    language = st.selectbox("🌐 Response language", SUPPORTED_LANGUAGES, index=0)
    st.markdown("---")
 
    st.markdown("### 🏗️ Architecture")
    st.markdown("""
**Orchestrator** (Llama 3.3 70B + tool calling)
plans and routes to:
 
🔬 **Diagnosis Agent** (Llama 3.2 Vision)
📚 **Advisory Agent** (RAG + Llama 3.3 70B)
📈 **Market Agent** (Weather + Price APIs)
 
All three share **persistent memory**
of the farmer's crop and history.
    """)
    st.markdown("---")
 
    st.markdown("### ⚡ Powered by")
    st.markdown("🟢 **NVIDIA NIM** · OpenAI-compatible API")
    st.markdown("---")
 
    if _live_key:
        st.markdown('<div class="status-connected">✅ NVIDIA NIM Connected</div>',
                    unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-error">⚠️ NVIDIA_API_KEY not set</div>',
                    unsafe_allow_html=True)
        st.markdown("Add it under **Settings → Secrets**:")
        st.code('NVIDIA_API_KEY = "nvapi-..."', language="toml")
 
# ── Main header banner ────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🌾 AgriMitra</h1>
    <p>AI-powered multi-agent farm advisory — built for smallholder farmers near Madanapalle, AP</p>
</div>
""", unsafe_allow_html=True)
 
# ── Badges ────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:1rem;">
  <span class="badge badge-green">🔬 Disease Diagnosis</span>
  <span class="badge badge-orange">📈 Market Prices</span>
  <span class="badge badge-blue">🌤 Live Weather</span>
  <span class="badge badge-purple">📚 RAG Advisory</span>
  <span class="badge badge-green">🧠 Multi-Agent</span>
</div>
""", unsafe_allow_html=True)
 
col_chat, col_trace = st.columns([3, 2])
 
with col_chat:
    st.markdown("### 💬 Ask AgriMitra")
 
    uploaded_image = st.file_uploader(
        "📷 Upload a leaf/plant photo (optional)", type=["jpg", "jpeg", "png"]
    )
    if uploaded_image:
        st.image(uploaded_image, caption="Uploaded image", width=250)
 
    quick_crop = st.selectbox(
        "⚡ Or quickly check a crop's market price", ["—"] + TRACKED_CROPS
    )
 
    user_text = st.text_area(
        "Your question",
        placeholder="e.g. 'What's wrong with this tomato leaf and should I sell my groundnut now?'",
        height=110,
    )
 
    submit = st.button("🌱 Ask AgriMitra", use_container_width=True)
 
    if submit:
        if not _live_key:
            st.error("⚠️ Please set NVIDIA_API_KEY in Streamlit Secrets before running queries.")
        elif not user_text.strip() and not uploaded_image and quick_crop == "—":
            st.warning("Please type a question, upload an image, or pick a crop.")
        else:
            final_query = user_text.strip()
            if quick_crop != "—" and not final_query:
                final_query = f"What's the current market price for {quick_crop} and should I sell now?"
            elif quick_crop != "—":
                final_query += f" (Also check market price for {quick_crop}.)"
 
            image_path = None
            if uploaded_image:
                tmp_dir = Path("/tmp/agrimitra_uploads")
                tmp_dir.mkdir(parents=True, exist_ok=True)
                image_path = tmp_dir / uploaded_image.name
                image_path.write_bytes(uploaded_image.getbuffer())
                image_path = str(image_path)
                if not final_query:
                    final_query = "What disease or issue does this leaf have, and what should I do?"
 
            trace = AgentTrace()
            with st.spinner("🌿 AgriMitra is thinking and consulting its agents..."):
                # Ensure live key is in env for orchestrator
                os.environ["NVIDIA_API_KEY"] = _live_key
                answer = handle_farmer_query(
                    session_id=st.session_state.session_id,
                    user_text=final_query,
                    image_path=image_path,
                    language=language,
                    trace=trace,
                )
 
            st.session_state.chat_history.append(("farmer", final_query))
            st.session_state.chat_history.append(("agrimitra", answer))
            st.session_state.last_trace = trace
 
    if st.session_state.chat_history:
        st.markdown("---")
        st.markdown("### 🗨️ Conversation")
        for role, text in reversed(st.session_state.chat_history[-10:]):
            if role == "farmer":
                st.markdown(
                    f'<div class="farmer-bubble">🧑‍🌾 <b>You:</b> {text}</div>',
                    unsafe_allow_html=True)
            else:
                st.markdown(
                    f'<div class="answer-card">🌾 <b>AgriMitra:</b><br>{text}</div>',
                    unsafe_allow_html=True)
 
with col_trace:
    st.markdown("### 🧠 Agent Reasoning Trace")
    st.caption("Live view of the orchestrator's plan and tool calls")
    if st.session_state.last_trace and st.session_state.last_trace.events:
        st.markdown(
            f'<div class="trace-panel">{st.session_state.last_trace.as_markdown()}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.info("💡 Ask a question to see the agent's live reasoning trace here.")
 
st.markdown("---")
st.caption(
    "AgriMitra • Diagnosis Agent (NVIDIA Llama 3.2 Vision) • "
    "Advisory Agent (RAG + Llama 3.3 70B) • Market Agent (Open-Meteo + Mandi prices) • "
    "Orchestrated via NVIDIA NIM tool calling"
)
