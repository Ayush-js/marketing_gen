# =============================================
#   ui/app.py
#   Streamlit Web Interface
#   Marketing Content Generator
# =============================================

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from core.llm_engine import LLMEngine
from core.image_engine import ImageEngine
from vectordb.store import ContentVectorStore
from prompts.templates import TONE_DESCRIPTIONS, PLATFORM_OPTIONS
from utils.exporter import export_to_txt, export_to_docx

st.set_page_config(
    page_title="Marketing Content Generator",
    page_icon="M",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
    --bg-app:        #0D0D0D;
    --bg-sidebar:    #1A1A1A;
    --bg-elevated:   #141414;
    --bg-card:       #2C2C2C;
    --bg-input:      #1A1A1A;
    --border-subtle: #333333;
    --border-hover:  #404040;
    --text-primary:  #F5F5F5;
    --text-secondary:#888888;
    --text-muted:    #888888;
    --accent-warm:   #A0522D;
    --accent-glow:   rgba(139, 69, 19, 0.35);
}

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background: var(--bg-app);
    color: var(--text-primary);
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border-subtle);
}
section[data-testid="stSidebar"] * {
    color: #E0E0E0 !important;
}
section[data-testid="stSidebar"] .section-title {
    color: var(--text-muted) !important;
}
section[data-testid="stSidebar"] .history-meta {
    color: var(--text-muted) !important;
}
section[data-testid="stSidebar"] .metric-value {
    color: var(--text-primary) !important;
}
section[data-testid="stSidebar"] .metric-label {
    color: var(--text-muted) !important;
}
section[data-testid="stSidebar"] .history-topic {
    color: var(--text-primary) !important;
}
section[data-testid="stSidebar"] p {
    color: var(--text-muted) !important;
}

/* ── Main panel ── */
section[data-testid="stMain"] {
    background:
        radial-gradient(
            ellipse 85% 60% at 12% 8%,
            rgba(160, 82, 45, 0.42) 0%,
            rgba(100, 50, 25, 0.18) 42%,
            transparent 68%
        ),
        radial-gradient(
            ellipse 65% 55% at 92% 88%,
            rgba(35, 22, 45, 0.45) 0%,
            transparent 55%
        ),
        linear-gradient(
            155deg,
            #0D0D0D 0%,
            #0a0908 35%,
            #0D0D0D 72%,
            #08070a 100%
        ) !important;
}

/* ── Typography ── */
.main-header {
    font-family: 'Inter', sans-serif;
    font-size: 2.8rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.02em;
    line-height: 1.15;
}
.sub-header {
    font-family: 'Inter', sans-serif;
    font-size: 1rem;
    color: var(--text-secondary);
    font-weight: 400;
    letter-spacing: 0.02em;
    margin-top: 8px;
}

/* ── Cards ── */
.result-card, .image-prompt-card {
    background: var(--bg-elevated);
    border: 1px solid var(--border-subtle);
    border-radius: 18px;
    padding: 24px;
    margin: 12px 0;
    font-size: 0.95rem;
    line-height: 1.7;
    white-space: pre-wrap;
    color: var(--text-primary);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45);
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}
.result-card:hover, .image-prompt-card:hover {
    transform: translateY(-2px);
    border-color: var(--border-hover);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.55);
}
.result-card       { border-left: 3px solid #5C4033; }
.image-prompt-card { border-left: 3px solid #4a3a32; }

/* ── Badges ── */
.badge {
    display: inline-block;
    background: #252525;
    border: 1px solid var(--border-subtle);
    border-radius: 10px;
    padding: 4px 10px;
    font-size: 0.75rem;
    font-weight: 600;
    color: #E0E0E0;
    margin: 2px 4px 2px 0;
    letter-spacing: 0.02em;
    font-family: 'Inter', sans-serif;
}

/* ── Metric tiles ── */
.metric-tile {
    background: var(--bg-elevated);
    border: 1px solid var(--border-subtle);
    border-radius: 16px;
    padding: 16px;
    text-align: center;
}
.metric-value {
    font-family: 'Inter', sans-serif;
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-primary);
}
.metric-label {
    font-size: 0.7rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-weight: 600;
    margin-top: 4px;
}

/* ── Divider ── */
.section-divider {
    border: none;
    border-top: 1px solid var(--border-subtle);
    margin: 28px 0;
}

/* ── History items ── */
.history-item {
    background: rgba(20, 20, 20, 0.85);
    border: 1px solid var(--border-subtle);
    border-radius: 12px;
    padding: 14px;
    margin: 8px 0;
    transition: background 0.2s ease, border-color 0.2s ease;
}
.history-item:hover {
    background: rgba(37, 37, 37, 0.95);
    border-color: var(--border-hover);
}
.history-topic {
    font-family: 'Inter', sans-serif;
    font-weight: 600;
    font-size: 0.9rem;
    color: var(--text-primary);
}
.history-meta {
    font-size: 0.75rem;
    color: var(--text-muted);
    margin-top: 6px;
}

/* ── Section titles ── */
.section-title {
    font-family: 'Inter', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    margin-bottom: 16px;
}
section[data-testid="stSidebar"] .section-title {
    color: var(--text-muted) !important;
}
section[data-testid="stMain"] .section-title {
    color: var(--text-secondary) !important;
}

/* ── Widget labels ── */
section[data-testid="stSidebar"] label[data-testid="stWidgetLabel"] p,
section[data-testid="stSidebar"] label[data-testid="stWidgetLabel"] span {
    color: var(--text-muted) !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
}
section[data-testid="stMain"] label[data-testid="stWidgetLabel"] p,
section[data-testid="stMain"] label[data-testid="stWidgetLabel"] span {
    color: var(--text-secondary) !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
}

/* ── Sidebar inputs ── */
section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div,
section[data-testid="stSidebar"] .stTextInput input {
    background-color: var(--bg-input) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
}
section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div:hover {
    border-color: var(--border-hover) !important;
}

/* ── Main inputs ── */
section[data-testid="stMain"] .stSelectbox [data-baseweb="select"] > div,
section[data-testid="stMain"] .stTextInput input,
section[data-testid="stMain"] .stTextArea textarea {
    background: var(--bg-input) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 14px !important;
    color: var(--text-primary) !important;
    font-weight: 400 !important;
}
section[data-testid="stMain"] .stSelectbox [data-baseweb="select"] > div:hover,
section[data-testid="stMain"] .stTextInput input:hover {
    border-color: var(--border-hover) !important;
}
section[data-testid="stMain"] .stSelectbox [data-baseweb="select"] > div:focus-within,
section[data-testid="stMain"] .stTextInput input:focus,
section[data-testid="stMain"] .stTextArea textarea:focus {
    border-color: rgba(160, 82, 45, 0.55) !important;
    box-shadow: 0 0 0 1px rgba(160, 82, 45, 0.2) !important;
}
section[data-testid="stMain"] .stSelectbox [data-baseweb="select"] span,
section[data-testid="stMain"] .stSelectbox div[data-baseweb="select"] * {
    font-weight: 500 !important;
    color: var(--text-primary) !important;
}

/* ── Dropdown menu ── */
div[data-baseweb="popover"] li[role="option"],
div[data-baseweb="menu"] li[role="option"],
ul[role="listbox"] li[role="option"] {
    font-weight: 500 !important;
    color: #E0E0E0 !important;
    transition: background-color 0.12s ease !important;
}
div[data-baseweb="popover"] li[role="option"]:hover,
div[data-baseweb="popover"] li[role="option"][aria-selected="true"],
div[data-baseweb="menu"] li[role="option"]:hover,
ul[role="listbox"] li[role="option"]:hover {
    font-weight: 600 !important;
    background-color: rgba(45, 45, 45, 0.95) !important;
    color: var(--text-primary) !important;
}
div[data-baseweb="popover"] ul,
div[data-baseweb="menu"] ul {
    background: #1A1A1A !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 14px !important;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.65) !important;
    padding: 6px 0 !important;
}

/* ── Checkbox ── */
.stCheckbox label p, .stCheckbox label span {
    font-weight: 500 !important;
    color: var(--text-secondary) !important;
    font-size: 0.875rem !important;
}

/* ── Main buttons ── */
.stButton > button,
.stDownloadButton > button {
    background: #2C2C2C !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 12px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    padding: 10px 24px !important;
    transition: transform 0.2s ease, box-shadow 0.2s ease, background 0.2s ease, border-color 0.2s ease !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35) !important;
}
.stButton > button:hover,
.stDownloadButton > button:hover {
    transform: translateY(-1px) !important;
    background: #333333 !important;
    border-color: rgba(160, 82, 45, 0.45) !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45) !important;
}

/* ── Sidebar Load buttons — small and subtle ── */
div[data-testid="stSidebar"] .stButton > button {
    background: rgba(255, 255, 255, 0.04) !important;
    color: #888888 !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 8px !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    padding: 4px 12px !important;
    box-shadow: none !important;
    margin-top: 6px !important;
    letter-spacing: 0.04em !important;
}
div[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(160, 82, 45, 0.15) !important;
    color: #C9A080 !important;
    border-color: rgba(160, 82, 45, 0.30) !important;
    transform: none !important;
    filter: none !important;
    box-shadow: none !important;
}

/* ── Tool links ── */
.tool-links {
    color: var(--text-secondary);
    font-size: 0.85rem;
    margin-top: 12px;
    font-weight: 500;
}
.tool-links a {
    color: #C9A080 !important;
    text-decoration: none;
    transition: color 0.2s;
}
.tool-links a:hover {
    color: #E8D4C4 !important;
    text-decoration: underline;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    font-weight: 600 !important;
    color: var(--text-muted) !important;
}
div[data-testid="stExpander"] {
    border: 1px solid var(--border-subtle) !important;
    border-radius: 14px !important;
    background: rgba(20, 20, 20, 0.6) !important;
}

/* ── Alerts ── */
div[data-testid="stAlert"] {
    border-radius: 14px !important;
    border: 1px solid var(--border-subtle) !important;
}
section[data-testid="stMain"] div[data-testid="stMarkdownContainer"] p,
section[data-testid="stMain"] div[data-testid="stMarkdownContainer"] li {
    color: var(--text-primary);
}
div[data-testid="stAlert"] div[data-testid="stMarkdownContainer"] p {
    color: inherit !important;
}
section[data-testid="stMain"] .stCodeBlock,
section[data-testid="stMain"] pre {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: 12px !important;
    color: var(--text-primary) !important;
}

/* ── Spinner ── */
div[data-testid="stSpinner"] {
    color: #E0E0E0 !important;
}
</style>
""", unsafe_allow_html=True)


# ── Session State ─────────────────────────────────────────────
def init_session():
    defaults = {
        "generated_content": None,
        "generation_meta":   None,
        "image_prompt":      None,
        "generated_image":   None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()


# ── Load Services ─────────────────────────────────────────────
@st.cache_resource
def load_services():
    try:
        llm = LLMEngine()
        db  = ContentVectorStore()
        return llm, db, None
    except ValueError as e:
        return None, None, str(e)

@st.cache_resource
def load_image_engine():
    try:
        return ImageEngine(), None
    except ValueError as e:
        return None, str(e)

llm, db, api_error    = load_services()
img_engine, img_error = load_image_engine()


# ═══════════════════════════════════════════
#   SIDEBAR
# ═══════════════════════════════════════════
with st.sidebar:
    st.markdown(
        '<div class="main-header" style="font-size:1.8rem;color:#F5F5F5;'
        'background:none;-webkit-text-fill-color:#F5F5F5;">MCG</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="sub-header" style="color:#888888;">Marketing Content Generator</div>',
        unsafe_allow_html=True
    )
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Content Library</div>', unsafe_allow_html=True)

    if db:
        history = db.get_history(limit=50)
        counts  = {}
        for item in history:
            counts[item["content_type"]] = counts.get(item["content_type"], 0) + 1

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="metric-tile">
                <div class="metric-value">{len(history)}</div>
                <div class="metric-label">Saved</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-tile">
                <div class="metric-value">{len(counts)}</div>
                <div class="metric-label">Types</div>
            </div>""", unsafe_allow_html=True)

        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Recent History</div>', unsafe_allow_html=True)

        filter_type = st.selectbox(
            "Filter",
            ["All", "Ad Copy", "Social Media Posts", "Email Campaign", "Product Description"],
            label_visibility="collapsed",
        )

        display_history = (
            [h for h in history if h["content_type"] == filter_type]
            if filter_type != "All" else history
        )[:8]

        if display_history:
            for i, item in enumerate(display_history):
                st.markdown(f"""
                <div class="history-item">
                    <div class="history-topic">{item['topic'][:28]}{'...' if len(item['topic']) > 28 else ''}</div>
                    <div class="history-meta">
                        <span class="badge">{item['content_type']}</span>
                        <span class="badge">{item['tone']}</span><br>
                        <span style="display:inline-block;margin-top:6px;color:#888888;">{item['timestamp']}</span>
                    </div>
                </div>""", unsafe_allow_html=True)

                if st.button(
                    "Load",
                    key=f"load_{i}_{item['timestamp']}",
                    use_container_width=True,
                ):
                    st.session_state.generated_content = item['full_content']
                    st.session_state.generation_meta   = {
                        "content_type": item['content_type'],
                        "topic":        item['topic'],
                        "tone":         item['tone'],
                        "platform":     item['platform'],
                        "model":        "llama-3.3-70b-versatile",
                        "tokens_used":  0,
                    }
                    st.session_state.image_prompt    = None
                    st.session_state.generated_image = None
                    st.rerun()

        else:
            st.markdown(
                '<p style="color:#888888;font-size:0.85rem;margin-top:8px">'
                'No history yet. Generate your first piece of content.</p>',
                unsafe_allow_html=True
            )

        st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
        with st.expander("Manage Data"):
            if st.button("Clear All History", use_container_width=True):
                deleted = db.delete_all()
                st.success(f"Deleted {deleted} items.")
                st.cache_resource.clear()
                st.rerun()


# ═══════════════════════════════════════════
#   MAIN PANEL
# ═══════════════════════════════════════════
st.markdown(
    '<div class="main-header">Marketing Content<br>Generator</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="sub-header">Transform ideas into high-converting marketing content — powered by Groq AI</div>',
    unsafe_allow_html=True
)
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

if api_error:
    st.error(f"**API Key Not Configured**\n\n{api_error}")
    st.stop()

# ── Input Form ────────────────────────────────────────────────
st.markdown('<div class="section-title">Configure Your Content</div>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1], gap="large")
with col1:
    content_type = st.selectbox(
        "Content Type",
        ["Ad Copy", "Social Media Posts", "Email Campaign", "Product Description"],
    )
    topic = st.text_input(
        "Product / Topic",
        placeholder="e.g. Noise-cancelling wireless headphones",
    )
    audience = st.text_input(
        "Target Audience",
        placeholder="e.g. Remote workers aged 25-40",
    )
with col2:
    tone = st.selectbox(
        "Brand Tone",
        list(TONE_DESCRIPTIONS.keys()),
    )
    platform = st.selectbox(
        "Platform / Channel",
        PLATFORM_OPTIONS.get(content_type, []),
    )
    usp = st.text_input(
        "Key Message / USP",
        placeholder="e.g. 40-hour battery, folds flat, premium sound",
    )

st.markdown(
    f'<span class="badge">{tone}</span> '
    f'<span style="color:#888888;font-size:0.85rem;font-weight:500;">{TONE_DESCRIPTIONS[tone]}</span>',
    unsafe_allow_html=True,
)
st.markdown("<br>", unsafe_allow_html=True)

gen_col, _, opt_col = st.columns([2, 1, 2])
with gen_col:
    generate_clicked = st.button("Generate Content", use_container_width=True)
with opt_col:
    use_memory = st.checkbox(
        "Use brand memory (Vector DB)",
        value=True,
        help="Retrieves similar past content to maintain brand consistency",
    )

# ── Generation Logic ──────────────────────────────────────────
if generate_clicked:
    if not topic.strip():
        st.error("Please enter a Product / Topic.")
    elif not audience.strip():
        st.error("Please enter a Target Audience.")
    elif not usp.strip():
        st.error("Please enter a Key Message / USP.")
    else:
        st.session_state.image_prompt    = None
        st.session_state.generated_image = None

        with st.spinner("Crafting your content..."):
            try:
                similar_context = ""
                if use_memory and db:
                    similar_context = db.find_similar(content_type, topic, audience)

                result = llm.generate_content(
                    content_type    = content_type,
                    topic           = topic,
                    audience        = audience,
                    tone            = tone,
                    platform        = platform,
                    usp             = usp,
                    similar_context = similar_context,
                )

                if db:
                    db.save_content(
                        content_type      = content_type,
                        topic             = topic,
                        audience          = audience,
                        tone              = tone,
                        platform          = platform,
                        generated_content = result["content"],
                    )

                st.session_state.generated_content = result["content"]
                st.session_state.generation_meta   = result

            except Exception as e:
                st.error(f"Generation failed: {str(e)}")

# ── Output Panel ──────────────────────────────────────────────
if st.session_state.generated_content:
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Generated Content</div>', unsafe_allow_html=True)

    meta = st.session_state.generation_meta

    st.markdown(
        f'<span class="badge">{meta["content_type"]}</span>'
        f'<span class="badge">{meta["topic"]}</span>'
        f'<span class="badge">{meta["tone"]}</span>'
        f'<span class="badge">{meta["platform"]}</span>'
        f'<span class="badge">{meta["tokens_used"]} tokens</span>'
        f'<span class="badge">{meta["model"]}</span>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        f'<div class="result-card">{st.session_state.generated_content}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    b1, b2, b3, b4 = st.columns(4)
    with b1:
        st.download_button(
            label="Download .txt",
            data=export_to_txt(
                meta["content_type"], meta["topic"],
                meta["tone"], meta["platform"],
                st.session_state.generated_content,
            ),
            file_name=f"{meta['topic'][:20].replace(' ','_')}.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with b2:
        st.download_button(
            label="Download .docx",
            data=export_to_docx(
                meta["content_type"], meta["topic"],
                meta["tone"], meta["platform"],
                st.session_state.generated_content,
            ),
            file_name=f"{meta['topic'][:20].replace(' ','_')}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
        )
    with b3:
        if st.button("Regenerate", use_container_width=True):
            st.session_state.generated_content = None
            st.session_state.generation_meta   = None
            st.session_state.image_prompt      = None
            st.session_state.generated_image   = None
            st.rerun()
    with b4:
        if st.button("New Content", use_container_width=True):
            st.session_state.generated_content = None
            st.session_state.generation_meta   = None
            st.session_state.image_prompt      = None
            st.session_state.generated_image   = None
            st.rerun()

    # ── Image Section ─────────────────────────────────────────
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">AI Image Generator</div>', unsafe_allow_html=True)

    img_col1, img_col2, img_col3 = st.columns([3, 1, 1])
    with img_col1:
        st.markdown(
            '<p style="color:#888888;font-size:0.85rem;margin-top:4px;">'
            'Step 1: Generate an image prompt. '
            'Step 2: Create the actual image using FLUX.1-schnell.</p>',
            unsafe_allow_html=True,
        )
    with img_col2:
        generate_img_prompt = st.button("Image Prompt", use_container_width=True)
    with img_col3:
        generate_image_btn = st.button(
            "Generate Image",
            use_container_width=True,
            disabled=not st.session_state.get("image_prompt"),
        )

    if generate_img_prompt:
        with st.spinner("Crafting image prompt..."):
            try:
                img_prompt = llm.generate_image_prompt(
                    content_type = meta["content_type"],
                    topic        = meta["topic"],
                    audience     = audience,
                    tone         = meta["tone"],
                    platform     = meta["platform"],
                )
                st.session_state.image_prompt    = img_prompt
                st.session_state.generated_image = None
            except Exception as e:
                st.error(f"Image prompt failed: {str(e)}")

    if st.session_state.get("image_prompt"):
        st.markdown(
            f'<div class="image-prompt-card">{st.session_state["image_prompt"]}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="tool-links">Or paste into: '
            '<a href="https://www.midjourney.com" target="_blank">Midjourney</a> · '
            '<a href="https://chat.openai.com" target="_blank">DALL-E</a> · '
            '<a href="https://firefly.adobe.com" target="_blank">Adobe Firefly</a>'
            '</div>',
            unsafe_allow_html=True,
        )

    if generate_image_btn and st.session_state.get("image_prompt"):
        if img_error:
            st.error(f"Image engine not available: {img_error}")
        else:
            with st.spinner("Generating image... this takes 20-40 seconds"):
                try:
                    final_prompt = img_engine.build_marketing_prompt(
                        topic        = meta["topic"],
                        audience     = audience,
                        tone         = meta["tone"],
                        platform     = meta["platform"],
                        content_type = meta["content_type"],
                        image_prompt = st.session_state["image_prompt"],
                    )
                    image_bytes = img_engine.generate_image(final_prompt)
                    st.session_state.generated_image = image_bytes
                except RuntimeError as e:
                    st.warning(str(e))
                except Exception as e:
                    st.error(f"Image generation failed: {str(e)}")

    if st.session_state.get("generated_image"):
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">Generated Image</div>', unsafe_allow_html=True)
        st.image(
            st.session_state.generated_image,
            caption=f"{meta['topic']} | {meta['platform']} | {meta['tone']}",
            use_column_width=True,
        )
        st.download_button(
            label="Download Image (.png)",
            data=st.session_state.generated_image,
            file_name=f"{meta['topic'][:20].replace(' ','_')}_image.png",
            mime="image/png",
        )

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    with st.expander("Brand Memory — Retrieved Context"):
        if db and use_memory:
            ctx = db.find_similar(content_type, topic, audience)
            if ctx:
                st.markdown(f"```\n{ctx}\n```")
            else:
                st.info("No similar past content found. This was a fresh generation.")