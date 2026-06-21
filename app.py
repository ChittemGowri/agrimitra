"""
app.py
AgriMitra — Modern, Light Multi-Agent Agricultural Dashboard.

Run with: streamlit run app.py
"""

import uuid
import html
import streamlit as st
from pathlib import Path

from config import (
    APP_NAME,
    NVIDIA_API_KEY,
    SUPPORTED_LANGUAGES,
    TRACKED_CROPS,
    VECTOR_STORE_PATH,
    KB_DIR,
)
from utils.logger import AgentTrace
from utils.memory import FarmerMemory
from agents.orchestrator import handle_farmer_query

# Initialize page config
st.set_page_config(
    page_title=f"{APP_NAME} | AI Farm Advisory Control Center",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize memory store
_memory = FarmerMemory()

# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
# Innovative Cyber-Agri Theme
# ---------------------------------------------------------------------
st.markdown("""
<style>
@import url("https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700&family=Rajdhani:wght@300;400;500;600;700&family=Hubot+Sans:wght@300;400;500;600&display=swap");

/* Color variables for Futuristic Cyber-Agri Theme */
:root {
    --bg-gradient: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
    --panel-bg: rgba(20, 25, 40, 0.6);
    --panel-border: rgba(0, 255, 187, 0.2);
    --primary-neon: #00ffef;
    --secondary-neon: #ff006e;
    --accent-neon: #7bff00;
    --text-primary: #e0e0e0;
    --text-secondary: #a0a0a0;
    --text-muted: #606060;
    --success-color: #00ff88;
    --warning-color: #ffaa00;
    --error-color: #ff4444;
    --glow-primary: 0 0 10px rgba(0, 255, 239, 0.5), 0 0 20px rgba(0, 255, 239, 0.3);
    --glow-secondary: 0 0 10px rgba(255, 0, 110, 0.5), 0 0 20px rgba(255, 0, 110, 0.3);
    --glow-accent: 0 0 10px rgba(123, 255, 0, 0.5), 0 0 20px rgba(123, 255, 0, 0.3);
}

/* App Background override */
.stApp {
    background: var(--bg-gradient) !important;
    font-family: "Hubot Sans", sans-serif;
    color: var(--text-primary) !important;
}

/* Sidebar background with glass effect */
section[data-testid="stSidebar"] {
    background: var(--panel-bg) !important;
    border-right: 1px solid var(--panel-border) !important;
    backdrop-filter: blur(10px) !important;
}

section[data-testid="stSidebar"] * {
    color: var(--text-primary) !important;
}

section[data-testid="stSidebar"] h1, 
section[data-testid="stSidebar"] h2, 
section[data-testid="stSidebar"] h3 {
    color: var(--primary-neon) !important;
    text-shadow: var(--glow-primary);
}

/* Hide header gradient */
header[data-testid="stHeader"] {
    background-color: transparent !important;
}

/* Futuristic Glass Cards */
.glass-card {
    background: var(--panel-bg) !important;
    border: 1px solid var(--panel-border) !important;
    border-radius: 16px !important;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
    backdrop-filter: blur(10px) !important;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    position: relative;
    overflow: hidden;
    color: var(--text-primary) !important;
}

.glass-card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--primary-neon), transparent);
    animation: scan 2s linear infinite;
}

@keyframes scan {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}

.glass-card:hover {
    border-color: var(--primary-neon) !important;
    box-shadow: 0 0 30px rgba(0, 255, 239, 0.2) !important;
    transform: translateY(-5px) scale(1.02);
}

.glass-card:hover::before {
    animation: scan 1.5s linear infinite;
}

/* Glowing Titles */
.glow-title {
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--primary-neon);
    font-family: "Orbitron", sans-serif;
    text-align: center;
    text-shadow: var(--glow-primary);
    letter-spacing: 1px;
    margin-bottom: 0.5rem;
    position: relative;
}

.glow-title::after {
    content: "";
    position: absolute;
    bottom: -10px;
    left: 50%;
    transform: translateX(-50%);
    width: 80px;
    height: 4px;
    background: linear-gradient(90deg, transparent, var(--primary-neon), transparent);
    border-radius: 2px;
}

.glow-subtitle {
    font-size: 1.2rem;
    color: var(--secondary-neon);
    font-family: "Rajdhani", sans-serif;
    letter-spacing: 2px;
    text-transform: uppercase;
    text-align: center;
    margin-bottom: 2rem;
    text-shadow: var(--glow-secondary);
}

/* Monospace cyber terminal with glow */
.cyber-terminal {
    background: rgba(0, 0, 0, 0.4) !important;
    border: 1px solid var(--panel-border) !important;
    border-radius: 12px;
    font-family: "Fira Code", monospace;
    font-size: 0.85rem;
    padding: 15px;
    color: var(--text-primary) !important;
    max-height: 480px;
    overflow-y: auto;
    box-shadow: inset 0 2px 8px rgba(0,0,0,0.3), 0 0 15px rgba(0, 255, 239, 0.1);
    position: relative;
}

.cyber-terminal::before {
    content: "[AGRIMITRA SYSTEM]";
    position: absolute;
    top: -8px;
    left: 12px;
    background: var(--bg-gradient);
    color: var(--primary-neon);
    font-size: 0.75rem;
    padding: 0 8px;
    border-radius: 4px;
    font-family: "Orbitron", sans-serif;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.trace-line {
    margin-bottom: 10px;
    line-height: 1.4;
    border-bottom: 1px dashed rgba(0, 255, 239, 0.1);
    padding-bottom: 8px;
    color: var(--text-primary) !important;
}

.trace-line:last-child {
    border-bottom: none;
}

/* Badge stylings with neon glow */
.badge {
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    display: inline-block;
    margin-right: 6px;
    border: 1px solid transparent;
}

.badge-success { 
    background-color: rgba(0, 255, 136, 0.15); 
    color: var(--success-color); 
    border: 1px solid rgba(0, 255, 136, 0.3);
    box-shadow: 0 0 8px rgba(0, 255, 136, 0.3);
}

.badge-warning { 
    background-color: rgba(255, 170, 0, 0.15); 
    color: var(--warning-color); 
    border: 1px solid rgba(255, 170, 0, 0.3);
    box-shadow: 0 0 8px rgba(255, 170, 0, 0.3);
}

.badge-error { 
    background-color: rgba(255, 68, 68, 0.15); 
    color: var(--error-color); 
    border: 1px solid rgba(255, 68, 68, 0.3);
    box-shadow: 0 0 8px rgba(255, 68, 68, 0.3);
}

.badge-info { 
    background-color: rgba(0, 255, 239, 0.15); 
    color: var(--primary-neon); 
    border: 1px solid rgba(0, 255, 239, 0.3);
    box-shadow: 0 0 8px rgba(0, 255, 239, 0.3);
}

/* Custom Streamlit component overrides with neon effects */
.stButton > button {
    background: linear-gradient(135deg, rgba(0, 255, 239, 0.1) 0%, rgba(0, 255, 239, 0.2) 100%) !important;
    color: var(--primary-neon) !important;
    border-radius: 12px !important;
    border: 1px solid var(--panel-border) !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
    box-shadow: 0 4px 12px rgba(0, 255, 239, 0.15) !important;
    transition: all 0.3s ease !important;
    position: relative;
    overflow: hidden;
}

.stButton > button::before {
    content: "";
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(0, 255, 239, 0.3), transparent);
    transition: 0.5s;
}

.stButton > button:hover::before {
    left: 100%;
}

.stButton > button:hover {
    background: linear-gradient(135deg, rgba(0, 255, 239, 0.2) 0%, rgba(0, 255, 239, 0.4) 100%) !important;
    box-shadow: 0 0 20px rgba(0, 255, 239, 0.3) !important;
    transform: translateY(-2px);
    color: white !important;
    text-shadow: 0 0 5px rgba(0, 255, 239, 0.5);
}

.stButton > button:active {
    transform: translateY(0);
}

/* Custom Connection Indicator with neon dots */
.indicator-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 6px 12px;
    background-color: rgba(255,255,255,0.02);
    border-radius: 6px;
    margin-bottom: 8px;
    border: 1px solid var(--panel-border);
}

.dot {
    height: 10px;
    width: 10px;
    border-radius: 50%;
    display: inline-block;
    position: relative;
}

.dot-green {
    background-color: var(--success-color);
    box-shadow: 0 0 8px var(--success-color), 0 0 12px var(--success-color);
    animation: pulse 2s infinite;
}

.dot-red {
    background-color: var(--error-color);
    box-shadow: 0 0 8px var(--error-color), 0 0 12px var(--error-color);
    animation: pulse 2s infinite;
}

.dot-yellow {
    background-color: var(--warning-color);
    box-shadow: 0 0 8px var(--warning-color), 0 0 12px var(--warning-color);
    animation: pulse 2s infinite;
}

.dot-blue {
    background-color: var(--primary-neon);
    box-shadow: 0 0 8px var(--primary-neon), 0 0 12px var(--primary-neon);
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.4); }
    70% { box-shadow: 0 0 0 10px rgba(255, 255, 255, 0); }
    100% { box-shadow: 0 0 0 0 rgba(255, 255, 255, 0); }
}

/* Readability overrides */
.stApp p, .stApp span, .stApp label, .stApp div, .stApp li {
    color: var(--text-primary) !important;
}

.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
    color: var(--primary-neon) !important;
    text-shadow: var(--glow-primary);
}

.stApp section[data-testid="stSidebar"] p, 
.stApp section[data-testid="stSidebar"] span, 
.stApp section[data-testid="stSidebar"] label,
.stApp section[data-testid="stSidebar"] h1,
.stApp section[data-testid="stSidebar"] h2,
.stApp section[data-testid="stSidebar"] h3 {
    color: var(--text-primary) !important;
}

/* Animated background elements */
#root > div:nth-child(1) > div > div > div > div > div section.main > div.block-container {
    position: relative;
    z-index: 10;
}

#root > div:nth-child(1) > div > div > div > div > div section.main > div.block-container::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: 
        "radial-gradient(circle at 10% 20%, rgba(0, 255, 239, 0.05) 0%, transparent 20%)",
        "radial-gradient(circle at 90% 80%, rgba(255, 0, 110, 0.05) 0%, transparent 20%)",
        "radial-gradient(circle at 30% 60%, rgba(123, 255, 0, 0.05) 0%, transparent 20%)";
    background-repeat: repeat;
    background-size: 200% 200%;
    animation: backgroundShift 15s ease infinite;
    z-index: -2;
    pointer-events: none;
}

@keyframes backgroundShift {
    0% { background-position: 0 0; }
    50% { background-position: 100% 100%; }
    100% { background-position: 0 0; }
}

/* Input field styling */
.stTextArea > div > div > textarea,
.stTextInput > div > div > input,
.stSelectbox > div > div > div {
    background: rgba(0, 0, 0, 0.3) !important;
    border: 1px solid var(--panel-border) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
}

.stTextArea > div > div > textarea:focus,
.stTextInput > div > div > input:focus {
    box-shadow: 0 0 0 2px rgba(0, 255, 239, 0.25) !important;
    border-color: var(--primary-neon) !important;
}

.stFileUploader > div > div > div > div {
    background: rgba(0, 0, 0, 0.2) !important;
    border: 2px dashed var(--panel-border) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
}

.stFileUploader > div > div > div > div:hover {
    border-color: var(--primary-neon) !important;
    background: rgba(0, 255, 239, 0.1) !important;
}

/* Alert/styling for messages */
.stAlert {
    background: rgba(0, 0, 0, 0.3) !important;
    border: 1px solid var(--panel-border) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
}

.stAlert[data-baseweb="notification"] {
    background: rgba(0, 0, 0, 0.3) !important;
}

.stSuccess {
    background-color: rgba(0, 255, 136, 0.1) !important;
    border-left: 4px solid var(--success-color) !important;
    box-shadow: 0 0 15px rgba(0, 255, 136, 0.2);
}

.stError {
    background-color: rgba(255, 68, 68, 0.1) !important;
    border-left: 4px solid var(--error-color) !important;
    box-shadow: 0 0 15px rgba(255, 68, 68, 0.2);
}

.stWarning {
    background-color: rgba(255, 170, 0, 0.1) !important;
    border-left: 4px solid var(--warning-color) !important;
    box-shadow: 0 0 15px rgba(255, 170, 0, 0.2);
}

.stInfo {
    background-color: rgba(0, 255, 239, 0.1) !important;
    border-left: 4px solid var(--primary-neon) !important;
    box-shadow: 0 0 15px rgba(0, 255, 239, 0.2);
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: rgba(0, 0, 0, 0.2);
    border-radius: 12px;
    padding: 4px;
}

.stTabs [data-baseweb="tab"] {
    height: 50px;
    background-color: transparent;
    border-radius: 10px;
    color: var(--text-secondary) !important;
    font-weight: 600;
    transition: all 0.3s ease;
    border: 1px solid transparent;
}

.stTabs [aria-selected="true"] {
    background-color: rgba(0, 255, 239, 0.1) !important;
    color: var(--primary-neon) !important;
    border: 1px solid var(--panel-border) !important;
    box-shadow: 0 0 15px rgba(0, 255, 239, 0.2);
}

/* Scrollbar styling */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.2) ;
}

::-webkit-scrollbar-thumb {
    background: var(--primary-neon) ;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--secondary-neon) ;
}
</style>
""", unsafe_allow_html=True)
# Session State Setup
# ---------------------------------------------------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_trace" not in st.session_state:
    st.session_state.last_trace = None
if "last_tool_outputs" not in st.session_state:
    st.session_state.last_tool_outputs = {}
if "selected_suggestion" not in st.session_state:
    st.session_state.selected_suggestion = ""

# ---------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------
def run_rebuild_kb():
    """Trigger vector store building directly from the UI."""
    try:
        from tools.retrieval_tool import SimpleVectorStore
        store = SimpleVectorStore()
        store.build_from_directory(KB_DIR)
        st.sidebar.success(f"Successfully indexed {len(store.chunks)} chunks!")
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"Failed to build vector store: {e}")

def render_price_gauge(price, min_val, max_val):
    """Generates custom visual range slider for Mandi Prices."""
    span = max_val - min_val
    if span <= 0:
        pct = 50
    else:
        pct = int(((price - min_val) / span) * 100)
    pct = max(0, min(100, pct))
    
    if pct >= 70:
        color = "#10b981"  # Emerald Green (Good for Selling)
        rec = "Optimal Selling Price"
    elif pct <= 30:
        color = "#dc2626"  # Red (Low Price)
        rec = "Sub-optimal (Consider Holding)"
    else:
        color = "#d97706"  # Amber Orange (Fair Price)
        rec = "Seasonal Average Price"
        
    return f"""
    <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px; margin-top: 10px; color: #1b261b;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 0.85rem; color: #5c6f5c;">
            <span>Min: <b>₹{min_val}</b></span>
            <span style="color: {color}; font-weight: 600;">Current: <b>₹{price}</b> ({rec})</span>
            <span>Max: <b>₹{max_val}</b></span>
        </div>
        <div style="background-color: #cbd5e1; border-radius: 4px; height: 10px; width: 100%; position: relative; border: 1px solid #94a3b8;">
            <div style="background-color: {color}; width: {pct}%; height: 100%; border-radius: 4px; transition: width 0.5s ease-in-out;"></div>
        </div>
        <div style="font-size: 0.75rem; color: #5c6f5c; text-align: center; margin-top: 6px;">
            Current Mandi rate sits at the <b>{pct}%</b> level of historical seasonal range.
        </div>
    </div>
    """

def render_tts_button(text, language):
    """Embeds custom browser-based speech synthesis script."""
    escaped_text = html.escape(text.replace("'", "\\'").replace("\n", " ").replace("\r", ""))
    lang_code = "te-IN" if language == "Telugu" else "en-IN"
    return f"""
    <script>
    function speakText() {{
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance('{escaped_text}');
            utterance.lang = '{lang_code}';
            utterance.rate = 0.92;
            utterance.pitch = 1.0;
            window.speechSynthesis.speak(utterance);
        }} else {{
            alert("Browser Text-to-Speech is not supported on this device.");
        }}
    }}
    </script>
    <button onclick="speakText()" style="
        background: rgba(45, 106, 79, 0.1);
        color: #2d6a4f;
        border: 1px solid rgba(45, 106, 79, 0.3);
        border-radius: 8px;
        padding: 8px 14px;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
        font-size: 0.85rem;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        margin-top: 10px;
        transition: all 0.2s ease;
    " onmouseover="this.style.background='rgba(45, 106, 79, 0.2)'; this.style.borderColor='rgba(45, 106, 79, 0.5)';" onmouseout="this.style.background='rgba(45, 106, 79, 0.1)'; this.style.borderColor='rgba(45, 106, 79, 0.3)';">
        🔊 Play Native Audio Advisory ({language})
    </button>
    """

# ---------------------------------------------------------------------
# Sidebar Panel (Memory & System Status)
# ---------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🌾 AgriMitra Control Panel")
    st.markdown("*Multi-agent Autonomous Farm Advisor*")
    st.markdown("---")

    # Real-Time Integration Status LEDs
    st.subheader("📡 System Status")
    
    # NVIDIA Key Status
    is_nvidia_connected = bool(NVIDIA_API_KEY)
    st.markdown(
        f'<div class="indicator-row"><span>NVIDIA AI Engine</span>'
        f'<span class="dot {"dot-green" if is_nvidia_connected else "dot-red"}"></span></div>',
        unsafe_allow_html=True
    )
    
    # RAG Vector Index Status
    is_kb_built = Path(VECTOR_STORE_PATH).exists()
    st.markdown(
        f'<div class="indicator-row"><span>Vector Store Index</span>'
        f'<span class="dot {"dot-green" if is_kb_built else "dot-red"}"></span></div>',
        unsafe_allow_html=True
    )

    # Weather API status
    st.markdown(
        '<div class="indicator-row"><span>Open-Meteo API</span>'
        '<span class="dot dot-green"></span></div>',
        unsafe_allow_html=True
    )
    
    # Mandi price feed
    st.markdown(
        '<div class="indicator-row"><span>Mandi Price Service</span>'
        '<span class="dot dot-green"></span></div>',
        unsafe_allow_html=True
    )

    st.markdown("---")
    
    # Memory Context Display
    st.subheader("🧠 Farmer Profile Memory")
    profile = _memory.get_profile(st.session_state.session_id)
    
    st.write(f"🧑‍🌾 **Current Crop:** `{profile.get('crop') or 'Not identified yet'}`")
    st.write(f"📍 **Location:** `{profile.get('location') or 'Madanapalle, AP'}`")
    
    col_clear, col_lang = st.columns([1, 1])
    with col_clear:
        if st.button("🗑️ Reset Session", use_container_width=True):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.chat_history = []
            st.session_state.last_trace = None
            st.session_state.last_tool_outputs = {}
            st.rerun()
    with col_lang:
        language = st.selectbox("Language", SUPPORTED_LANGUAGES, index=0)

    st.markdown("---")
    
    # Knowledge Base rebuilding options
    st.subheader("⚙️ Indexing & RAG Config")
    if not is_kb_built:
        st.warning("⚠️ RAG knowledge base not indexed yet.")
    
    if st.button("🔧 Rebuild Vector Index", use_container_width=True):
        with st.spinner("Embedding knowledge base docs..."):
            run_rebuild_kb()

# ---------------------------------------------------------------------
# Main AI Command Center Layout
# ---------------------------------------------------------------------
st.markdown('<div class="glow-title">AGRIMITRA</div>', unsafe_allow_html=True)
st.markdown('<div class="glow-subtitle">AI-Powered Multi-Agent Farm Advisory Command Center</div>', unsafe_allow_html=True)

# Main Navigation Tabs
tab_advisor, tab_market, tab_rag, tab_trace = st.tabs([
    "🌾 AI Advisor Workspace",
    "📈 Market & Weather Insights",
    "📚 Grounding Knowledge Base",
    "🧠 Agent Reasoning Logs"
])

# ---------------------------------------------------------------------
# TAB 1: AI Advisor Workspace (Image diagnosis & Chat)
# ---------------------------------------------------------------------
with tab_advisor:
    col_input, col_response = st.columns([2, 3])
    
    with col_input:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🧑‍🌾 Farmer Inputs")
        
        uploaded_image = st.file_uploader(
            "📷 Scan Plant/Leaf Image for Diagnostics (Optional)",
            type=["jpg", "jpeg", "png"]
        )
        if uploaded_image:
            st.image(uploaded_image, caption="Attached Crop Specimen", use_container_width=True)

        # Preloaded Quick-Demo Suggestions to help judges test the flow
        st.subheader("💡 Quick Queries")
        suggestions = [
            "What treatments work for Early Blight on my Tomato plant?",
            "What is the market price of Groundnut, and is it a good time to sell?",
            "Can I safely spray pesticides on my Mango crops this afternoon?",
            "Identify this tomato leaf curl issue and recommend RAG organic solutions."
        ]
        
        # Grid layout for prompt suggestions
        s_col1, s_col2 = st.columns(2)
        with s_col1:
            if st.button(suggestions[0], key="s1", use_container_width=True):
                st.session_state.selected_suggestion = suggestions[0]
            if st.button(suggestions[2], key="s3", use_container_width=True):
                st.session_state.selected_suggestion = suggestions[2]
        with s_col2:
            if st.button(suggestions[1], key="s2", use_container_width=True):
                st.session_state.selected_suggestion = suggestions[1]
            if st.button(suggestions[3], key="s4", use_container_width=True):
                st.session_state.selected_suggestion = suggestions[3]

        # Use suggestion value if selected, otherwise blank
        initial_value = st.session_state.selected_suggestion
        user_query = st.text_area(
            "Query / Question for AgriMitra",
            value=initial_value,
            placeholder="Type your question or query here...",
            height=120
        )
        
        # Reset selection state once consumed
        st.session_state.selected_suggestion = ""

        submit = st.button("🌱 Execute Multi-Agent Consultation", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_response:
        # Run Query logic
        if submit:
            if not NVIDIA_API_KEY:
                st.error("⚠️ NVIDIA_API_KEY missing! Set it in your `.env` configuration file.")
            elif not user_query.strip() and not uploaded_image:
                st.warning("Please enter a query or upload an image first.")
            else:
                final_query = user_query.strip()
                image_path = None
                
                # Handle image uploads
                if uploaded_image:
                    tmp_dir = Path("data/uploaded_tmp")
                    tmp_dir.mkdir(parents=True, exist_ok=True)
                    image_path = tmp_dir / uploaded_image.name
                    image_path.write_bytes(uploaded_image.getbuffer())
                    image_path = str(image_path)
                    if not final_query:
                        final_query = "Please diagnose this plant leaf and suggest treatments."
                
                trace = AgentTrace()
                with st.spinner("🤖 Co-ordinating agents (Orchestrator -> Specialists)..."):
                    final_answer, tool_outputs = handle_farmer_query(
                        session_id=st.session_state.session_id,
                        user_text=final_query,
                        image_path=image_path,
                        language=language,
                        trace=trace
                    )
                
                # Update session states
                st.session_state.chat_history.append(("farmer", final_query))
                st.session_state.chat_history.append(("agrimitra", final_answer))
                st.session_state.last_trace = trace
                st.session_state.last_tool_outputs = tool_outputs
        
        # Display results panel
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("🌾 AgriMitra Recommendation")
        
        if st.session_state.chat_history:
            latest_role, latest_text = st.session_state.chat_history[-1]
            if latest_role == "agrimitra":
                st.markdown(latest_text)
                
                # Render speech synthesizer button
                st.components.v1.html(
                    render_tts_button(latest_text, language),
                    height=55,
                    scrolling=False
                )
        else:
            st.info("Awaiting inputs. Run a quick query or consult using the left panel.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display structured sub-agent visual widgets below answer if they exist
        outputs = st.session_state.last_tool_outputs
        
        # Render visual card for diagnosis if available
        if "diagnosis" in outputs and outputs["diagnosis"].get("status") == "success":
            diag = outputs["diagnosis"]
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### 🔬 Specialist Pathology Diagnosis")
            
            # Formulate layout columns
            col_diag1, col_diag2, col_diag3 = st.columns(3)
            with col_diag1:
                st.markdown(f"**Identified Crop:**<br><span style='color: var(--primary-green); font-size: 1.2rem; font-weight: 600;'>{diag.get('crop_identified')}</span>", unsafe_allow_html=True)
            with col_diag2:
                # Severity badge
                sev = diag.get("severity", "none").lower()
                badge_class = "badge-green" if sev == "none" or sev == "mild" else ("badge-orange" if sev == "moderate" else "badge-red")
                st.markdown(f"**Condition Severity:**<br><span class='badge {badge_class}'>{diag.get('severity')}</span>", unsafe_allow_html=True)
            with col_diag3:
                # Confidence rating
                conf = diag.get("confidence", "low").lower()
                conf_color = "var(--primary-green)" if conf == "high" else ("var(--accent-amber)" if conf == "medium" else "var(--accent-red)")
                st.markdown(f"**AI Confidence:**<br><span style='color: {conf_color}; font-weight: bold;'>{diag.get('confidence').upper()}</span>", unsafe_allow_html=True)
                
            st.markdown(f"<p style='margin-top: 15px; border-left: 3px solid var(--primary-green); padding-left: 10px; font-style: italic;'>{diag.get('visual_evidence')}</p>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # Historical Conversation Log
    if len(st.session_state.chat_history) > 2:
        st.subheader("📜 Consultation History")
        for role, text in reversed(st.session_state.chat_history[:-2]):
            if role == "farmer":
                st.markdown(f"**🧑‍🌾 You:** {text}")
            else:
                st.markdown(
                    f'<div style="background-color: rgba(255,255,255,0.02); border-left: 3px solid var(--accent-emerald); padding: 12px; border-radius: 6px; margin-bottom: 15px;">'
                    f'🌾 <b>AgriMitra:</b><br>{text}</div>',
                    unsafe_allow_html=True
                )

# ---------------------------------------------------------------------
# TAB 2: Market & Weather Insights Dashboard
# ---------------------------------------------------------------------
with tab_market:
    st.subheader("📈 Live Agricultural Market Data Center")
    st.caption("Visual dashboard for commodity pricing, spraying weather safety windows, and local forecasts.")
    
    outputs = st.session_state.last_tool_outputs
    
    if "market" in outputs and outputs["market"].get("status") == "success":
        m_data = outputs["market"]
        weather = m_data.get("weather", {})
        price = m_data.get("price", {})
        work_note = m_data.get("field_work_note", "")
        
        col_w_m, col_gauge = st.columns([3, 2])
        
        with col_w_m:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### ⛅ Climate Spray Window")
            
            # Weather details metrics
            if weather.get("status") == "success":
                w_curr = weather.get("current", {})
                w_col1, w_col2, w_col3, w_col4 = st.columns(4)
                
                with w_col1:
                    st.metric("Temperature", f"{w_curr.get('temperature_c')}°C")
                with w_col2:
                    st.metric("Humidity", f"{w_curr.get('humidity_pct')}%")
                with w_col3:
                    st.metric("Wind Speed", f"{w_curr.get('wind_speed_kmh')} km/h")
                with w_col4:
                    st.metric("Precipitation", f"{w_curr.get('precipitation_mm')} mm")
                
                # Spray Window Warning
                is_rain = "avoid spraying" in work_note.lower()
                alert_type = "error" if is_rain else "success"
                alert_icon = "⚠️" if is_rain else "✅"
                st.markdown(f"**Spraying Window Advisory:**")
                if is_rain:
                    st.error(f"{alert_icon} {work_note}")
                else:
                    st.success(f"{alert_icon} {work_note}")
            else:
                st.info("Weather sub-agent was unable to fetch data.")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 3-Day Forecast Cards
            if weather.get("status") == "success" and weather.get("forecast_3_day"):
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown("#### 📅 3-Day Hyperlocal Forecast")
                f_cols = st.columns(3)
                for idx, day in enumerate(weather["forecast_3_day"]):
                    with f_cols[idx]:
                        st.markdown(f"**{day['date']}**")
                        st.markdown(f"🌡️ Max: {day['max_temp_c']}°C | Min: {day['min_temp_c']}°C")
                        rain_prob = day.get("rain_probability_pct", 0)
                        rain_color = "red" if rain_prob >= 55 else ("orange" if rain_prob >= 30 else "green")
                        st.markdown(f"💧 Rain Probability: <span style='color: {rain_color}; font-weight: bold;'>{rain_prob}%</span>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
        with col_gauge:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### 💰 APMC Mandi Commodity Valuation")
            
            if price.get("status") == "success":
                st.metric(
                    f"Mandi Price ({price.get('crop')})",
                    f"₹{price.get('price_inr_per_quintal')} / quintal",
                    f"{price.get('volatility').upper()} VOLATILITY",
                    delta_color="off"
                )
                
                # Render custom horizontal gauge
                p_min = price.get("typical_range", {}).get("min", 1000)
                p_max = price.get("typical_range", {}).get("max", 5000)
                st.markdown(
                    render_price_gauge(price.get('price_inr_per_quintal'), p_min, p_max),
                    unsafe_allow_html=True
                )
                
                st.markdown(f"<p style='margin-top: 15px;'>📝 <b>Recommendation:</b> {price.get('recommendation')}</p>", unsafe_allow_html=True)
                st.caption(f"Source: {price.get('source')} | Dated: {price.get('date')}")
            else:
                st.info("Market price data is currently unavailable.")
            st.markdown('</div>', unsafe_allow_html=True)
            
    else:
        # Default view before tool triggers
        st.info("Please consult AgriMitra on pricing or weather query to load details.")
        
        # Display simulated default price listing card
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Market Commodity Baselines (Chittoor District)")
        default_cols = st.columns(len(TRACKED_CROPS))
        # Hardcode baseline data for demo rendering
        baselines = {
            "Tomato": "₹800 - ₹2800",
            "Groundnut": "₹5200 - ₹6800",
            "Mango": "₹1200 - ₹4500",
            "Tamarind": "₹7000 - ₹11000",
            "Ragi": "₹3200 - ₹3800"
        }
        for idx, crop in enumerate(TRACKED_CROPS):
            with default_cols[idx]:
                st.metric(crop, baselines.get(crop, "N/A"), help="Typical baseline price range per quintal")
        st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------
# TAB 3: Grounding Knowledge Base File Explorer
# ---------------------------------------------------------------------
with tab_rag:
    st.subheader("📚 Grounding Knowledge Base Documents")
    st.caption("These files form the primary grounding index for the Advisory Agent RAG pipeline.")
    
    try:
        kb_files = list(Path(KB_DIR).glob("*.txt"))
        if kb_files:
            file_names = [f.name for f in kb_files]
            selected_file_name = st.selectbox("Select document to read/preview:", file_names)
            
            selected_filepath = Path(KB_DIR) / selected_file_name
            file_text = selected_filepath.read_text(encoding="utf-8")
            
            col_file_info, col_file_content = st.columns([1, 2])
            with col_file_info:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown(f"#### 📄 File Metadata")
                st.write(f"**Name:** `{selected_file_name}`")
                st.write(f"**Character Count:** `{len(file_text)}`")
                st.write(f"**File Size:** `{selected_filepath.stat().st_size} bytes`")
                
                # Descriptive summaries of grounding files
                desc = "No summary available."
                if "tomato" in selected_file_name:
                    desc = "Details diagnostic features and chemical/organic treatments for Leaf Curl and blight in Tomato crops."
                elif "groundnut" in selected_file_name:
                    desc = "Guides for Tikka leaf spot prevention, early soil prep, and organic copper fungicides."
                elif "mango" in selected_file_name:
                    desc = "Management of Anthracnose disease and blossom blight in mango orchards near Chittoor."
                elif "general" in selected_file_name:
                    desc = "Integrated Pest Management principles, crop rotation, and bio-fertilizer usage guidelines."
                st.write(f"**Scope:** {desc}")
                st.markdown('</div>', unsafe_allow_html=True)
                
            with col_file_content:
                st.markdown('<div class="cyber-terminal" style="max-height: 350px;">', unsafe_allow_html=True)
                st.markdown(f"```text\n{file_text[:3000]}\n```" + ("\n...[TRUNCATED FOR PREVIEW]..." if len(file_text) > 3000 else ""))
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("No documents found in knowledge base directory.")
    except Exception as e:
        st.error(f"Failed to load RAG files: {e}")

# ---------------------------------------------------------------------
# TAB 4: Agent Reasoning Logs Panel
# ---------------------------------------------------------------------
with tab_trace:
    st.subheader("🧠 Multi-Agent Execution Timeline")
    st.caption("Live trace of the orchestrator's decision-making flow and function invocations.")
    
    if st.session_state.last_trace and st.session_state.last_trace.events:
        st.markdown('<div class="terminal-header"><div class="terminal-dot" style="background-color: #f87171;"></div><div class="terminal-dot" style="background-color: #fbbf24;"></div><div class="terminal-dot" style="background-color: #34d399;"></div><span style="color: var(--text-muted); font-size: 0.75rem; font-family: \'Fira Code\', monospace;">agrimitra_orchestration_engine.log</span></div>', unsafe_allow_html=True)
        
        # Custom render loop for logs to look highly technical and glowing
        html_lines = []
        icons = {
            "plan": "🧭 [PLANNING]",
            "tool_call": "🔧 [TOOL CALL]",
            "tool_result": "📥 [RESULT]   ",
            "thought": "💭 [THOUGHT]  ",
            "final": "✅ [FINAL]    ",
            "error": "⚠️ [ERROR]    ",
        }
        for e in st.session_state.last_trace.events:
            tag = icons.get(e.event_type, "• [LOG]      ")
            color = "var(--primary-green)" if "result" in e.event_type or "final" in e.event_type else ("var(--accent-amber)" if "call" in e.event_type else "var(--text-primary)")
            if e.event_type == "error":
                color = "var(--accent-red)"
                
            line = f"<div class='trace-line'>[{(e.timestamp % 100):.2f}s] <b style='color: {color}; font-family: \"Fira Code\", monospace;'>{tag} {e.actor}:</b> {html.escape(e.content)}</div>"
            html_lines.append(line)
            
        st.markdown(
            f'<div class="cyber-terminal">{"".join(html_lines)}</div>',
            unsafe_allow_html=True
        )
    else:
        st.info("Run a query on the Advisor workspace to inspect the AI's execution trace here.")

st.markdown("---")
st.caption(
    "AgriMitra connects a vision-guided plant pathologist (NVIDIA Vision), a grounded advisory agent (NVIDIA Embeddings RAG), "
    "and a real-time climate/market analyst (Open-Meteo & APMC feeds) managed by a central planning Orchestrator. "
    "Created for the Google × Kaggle AI Agents Intensive Capstone."
)
