import os
import uuid
import streamlit as st
from pathlib import Path

# Import variables from config
import config
from config import APP_NAME, SUPPORTED_LANGUAGES, TRACKED_CROPS
from utils.logger import AgentTrace
from agents.orchestrator import handle_farmer_query

# ---------------------------------------------------------------------
# Robust API Key Resolution for Streamlit Cloud Deployment
# ---------------------------------------------------------------------
if hasattr(config, 'GEMINI_API_KEY') and config.GEMINI_API_KEY:
    GEMINI_API_KEY = config.GEMINI_API_KEY
elif "GEMINI_API_KEY" in st.secrets:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", None)

# Set up page configurations
st.set_page_config(
    page_title=f"{APP_NAME} | AI Farm Advisory Agent",
    page_icon="🌾",
    layout="wide",
)

# ---------------------------------------------------------------------
# Custom theme: an intentional earthy/agri palette instead of default
# Streamlit blue. Deep soil brown, leaf green, turmeric accent, warm
# cream background -- grounded in the actual subject matter.
# ---------------------------------------------------------------------
st.markdown("""
<style>
:root {
    --soil-dark: #2b2118;
    --leaf-green: #3f6b3f;
    --leaf-light: #7ba05b;
    --turmeric: #d99a2b;
    --cream: #f7f2e7;
    --card: #fffaf0;
}
.stApp {
    background-color: var(--cream);
}
section[data-testid="stSidebar"] {
    background-color: var(--soil-dark);
}
section[data-testid="stSidebar"] * {
    color: var(--cream) !important;
}
h1, h2, h3 {
    color: var(--soil-dark) !important;
    font-family: 'Georgia', serif;
}
.stButton > button {
    background-color: var(--leaf-green);
    color: white;
    border-radius: 8px;
    border: none;
    font-weight: 600;
}
.stButton > button:hover {
    background-color: var(--turmeric);
    color: var(--soil-dark);
}
.trace-panel {
    background-color: var(--card);
    border-left: 4px solid var(--turmeric);
    padding: 1rem;
    border-radius: 6px;
    font-size: 0.85rem;
}
.answer-card {
    background-color: var(--card);
    border-left: 4px solid var(--leaf-green);
    padding: 1.2rem;
    border-radius: 8px;
    font-size: 1.05rem;
    line-height: 1.6;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # list of (role, text)
if "last_trace" not in st.session_state:
    st.session_state.last_trace = None

# ---------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🌾 AgriMitra")
    st.markdown("*Multi-agent AI farm advisor*")
    st.markdown("---")
    st.markdown("### Built for")
    st.markdown("Google × Kaggle **AI Agents Intensive** Capstone")
    st.markdown("---")
    language = st.selectbox("Response language", SUPPORTED_LANGUAGES, index=0)
    st.markdown("---")
    st.markdown("### Architecture")
    st.markdown("""
    **Orchestrator** (Gemini function calling)
    plans and routes to:
    - 🔬 Diagnosis Agent (Vision)
    - 📚 Advisory Agent (RAG)
    - 📈 Market Agent (Weather + Price)

    All three share **persistent memory**
    of the farmer's crop and history.
    """)
    st.markdown("---")
    
    if not GEMINI_API_KEY:
        st.error("⚠️ GEMINI_API_KEY not set. Add it to Secrets in Streamlit Cloud Settings.")
    else:
        st.success("✅ Gemini API connected")

# ---------------------------------------------------------------------
# Main layout
# ---------------------------------------------------------------------
st.title("🌾 AgriMitra")
st.caption("AI-powered multi-agent farm advisory — built for smallholder farmers near Madanapalle, AP")

col_chat, col_trace = st.columns([3, 2])

with col_chat:
    st.subheader("Ask AgriMitra")

    uploaded_image = st.file_uploader(
        "Upload a leaf/plant photo (optional)", type=["jpg", "jpeg", "png"]
    )
    if uploaded_image:
        st.image(uploaded_image, caption="Uploaded image", width=250)

    quick_crop = st.selectbox("Or quickly check a crop's market price", ["—"] + TRACKED_CROPS)

    user_text = st.text_area(
        "Your question",
        placeholder="e.g. 'What's wrong with this tomato leaf and should I sell my groundnut now?'",
        height=100,
    )

    submit = st.button("🌱 Ask AgriMitra", use_container_width=True)

    if submit:
        if not GEMINI_API_KEY:
            st.error("Please configure GEMINI_API_KEY in the Streamlit App Advanced Secrets Panel before running queries.")
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
                tmp_dir = Path("data/uploaded_tmp")
                tmp_dir.mkdir(parents=True, exist_ok=True)
                image_path = tmp_dir / uploaded_image.name
                image_path.write_bytes(uploaded_image.getbuffer())
                image_path = str(image_path)
                if not final_query:
                    final_query = "What disease or issue does this leaf have, and what should I do?"

            trace = AgentTrace()
            with st.spinner("AgriMitra is thinking and consulting its agents..."):
                try:
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
                    
                except Exception as e:
                    st.error(f"An error occurred while handling the query down the pipeline: {e}")

    st.markdown("---")
    st.subheader("Conversation")
    for role, text in reversed(st.session_state.chat_history[-10:]):
        if role == "farmer":
            st.markdown(f"**🧑‍🌾 You:** {text}")
        else:
            st.markdown(f'<div class="answer-card">🌾 <b>AgriMitra:</b><br>{text}</div>',
                        unsafe_allow_html=True)
            st.markdown("")

with col_trace:
    st.subheader("🧠 Agent Reasoning Trace")
    st.caption("Live view of the orchestrator's plan and tool calls")
    if st.session_state.last_trace and st.session_state.last_trace.events:
        st.markdown(
            f'<div class="trace-panel">{st.session_state.last_trace.as_markdown()}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.info("Ask a question to see the agent's live reasoning trace here.")

st.markdown("---")
st.caption(
    "AgriMitra combines a Diagnosis Agent (Gemini Vision), an Advisory Agent (RAG over "
    "agricultural extension guides), and a Market Agent (live weather + mandi prices), "
    "coordinated by a planning Orchestrator using Gemini function calling."
)
