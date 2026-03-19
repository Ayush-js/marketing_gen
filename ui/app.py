# =============================================
#   ui/app.py
#   Streamlit Web Interface
#   Marketing Content Generator
# =============================================

import sys
import os

# Allow imports from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from core.llm_engine import LLMEngine
from core.image_engine import ImageEngine
from vectordb.store import ContentVectorStore
from prompts.templates import TONE_DESCRIPTIONS, PLATFORM_OPTIONS
from utils.exporter import export_to_txt, export_to_docx

# ── Page Config ───────────────────────────────────────────────
st.set_page_config(
    page_title="Marketing Content Generator",
    page_icon="M",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;700;800&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp { background: #030712; color: #f3f4f6; }

section[data-testid="stSidebar"] {
    background: #0f172a !important;
    border-right: 1px solid #1e293b;
}

.main-header {
    font-family: 'Outfit', sans-serif;
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(135deg, #38bdf8, #818cf8, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
    line-height: 1.15;
}

.sub-header {
    font-family: 'Outfit', sans-serif;
    font-size: 1rem;
    color: #9ca3af;
    font-weight: 400;
    letter-spacing: 0.02em;
    margin-top: 8px;
}

.result-card, .image-prompt-card {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 12px;
    padding: 24px;
    margin: 12px 0;
    font-size: 0.95rem;
    line-height: 1.7;
    white-space: pre-wrap;
    color: #e5e7eb;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.result-card:hover, .image-prompt-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -2px rgba(0,0,0,0.05);
}
.result-card { border-left: 4px solid #818cf8; }
.image-prompt-card { border-left: 4px solid #c084fc; }

.badge {
    display: inline-block;
    background: rgba(56,189,248,0.1);
    border: 1px solid rgba(56,189,248,0.2);
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 0.75rem;
    font-weight: 600;
    color: #38bdf8;
    margin: 2px 4px 2px 0;
    letter-spacing: 0.02em;
    font-family: 'Outfit', sans-serif;
}

.metric-tile {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 12px;
    padding: 16px;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.metric-value {
    font-family: 'Outfit', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: #f3f4f6;
}
.metric-label {
    font-size: 0.75rem;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 600;
    margin-top: 4px;
}

.section-divider {
    border: none;
    border-top: 1px solid #1f2937;
    margin: 28px 0;
}

.history-item {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 8px;
    padding: 14px;
    margin: 8px 0;
    transition: background 0.2s ease;
}
.history-item:hover { background: #1e293b; }
.history-topic {
    font-family: 'Outfit', sans-serif;
    font-weight: 600;
    font-size: 0.9rem;
    color: #f3f4f6;
}
.history-meta {
    font-size: 0.75rem;
    color: #9ca3af;
    margin-top: 6px;
}

.stButton > button {
    background: linear-gradient(135deg, #4f46e5, #3b82f6) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important;
    padding: 10px 24px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 6px -1px rgba(59,130,246,0.2) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 8px -1px rgba(59,130,246,0.3) !important;
    filter: brightness(1.1) !important;
}

.section-title {
    font-family: 'Outfit', sans-serif;
    font-size: 0.85rem;
    font-weight: 700;
    color: #9ca3af;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    margin-bottom: 16px;
}

.tool-links {
    color: #9ca3af;
    font-size: 0.85rem;
    margin-top: 12px;
    font-weight: 500;
}
.tool-links a {
    color: #38bdf8 !important;
    text-decoration: none;
    transition: color 0.2s;
}
.tool-links a:hover {
    color: #818cf8 !important;
    text-decoration: underline;
}

.image-container {
    border: 1px solid #1f2937;
    border-radius: 12px;
    overflow: hidden;
    margin: 16px 0;
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

llm, db, api_error       = load_services()
img_engine, img_error    = load_image_engine()


# ═══════════════════════════════════════════
#   SIDEBAR
# ═══════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="main-header" style="font-size:1.8rem">MCG</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Marketing Content Generator</div>', unsafe_allow_html=True)
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
            for item in display_history:
                st.markdown(f"""
                <div class="history-item">
                    <div class="history-topic">{item['topic'][:28]}{'...' if len(item['topic']) > 28 else ''}</div>
                    <div class="history-meta">
                        <span class="badge">{item['content_type']}</span>
                        <span class="badge">{item['tone']}</span><br>
                        <span style="display:inline-block;margin-top:6px;">{item['timestamp']}</span>
                    </div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown(
                '<p style="color:#6b7280;font-size:0.85rem;margin-top:8px">'
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
st.markdown('<div class="main-header">Marketing Content<br>Generator</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Transform ideas into high-converting marketing content — powered by Groq AI</div>',
    unsafe_allow_html=True
)
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

# ── API Key Warning ───────────────────────────────────────────
if api_error:
    st.error(f"""
    **API Key Not Configured**\n\n{api_error}

    **Fix:** Open `.env` → replace `your_groq_api_key_here` with your key from [console.groq.com](https://console.groq.com) → restart the app.
    """)
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
        placeholder="e.g. Remote workers aged 25–40",
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

# Tone preview
st.markdown(
    f'<span class="badge">{tone}</span> '
    f'<span style="color:#9ca3af;font-size:0.85rem;font-weight:500;">{TONE_DESCRIPTIONS[tone]}</span>',
    unsafe_allow_html=True,
)

st.markdown("<br>", unsafe_allow_html=True)

# ── Generate Button ───────────────────────────────────────────
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
        # Reset all previous results
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

    # ── Action Buttons ────────────────────────────────────────
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
            '<p style="color:#9ca3af;font-size:0.85rem;margin-top:4px;">'
            'Step 1: Generate an image prompt. '
            'Step 2: Create the actual image using Stable Diffusion XL.</p>',
            unsafe_allow_html=True,
        )
    with img_col2:
        generate_img_prompt = st.button(
            "Image Prompt", use_container_width=True
        )
    with img_col3:
        generate_image_btn = st.button(
            "Generate Image", use_container_width=True,
            disabled=not st.session_state.get("image_prompt"),
        )

    # ── Step 1: Generate image prompt ────────────────────────
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

    # ── Show image prompt ─────────────────────────────────────
    if st.session_state.get("image_prompt"):
        st.markdown(
            f'<div class="image-prompt-card">{st.session_state["image_prompt"]}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="tool-links">Or paste into: '
            '<a href="https://www.midjourney.com" target="_blank">Midjourney</a> · '
            '<a href="https://chat.openai.com" target="_blank">DALL·E</a> · '
            '<a href="https://firefly.adobe.com" target="_blank">Adobe Firefly</a>'
            '</div>',
            unsafe_allow_html=True,
        )

    # ── Step 2: Generate actual image ────────────────────────
    if generate_image_btn and st.session_state.get("image_prompt"):
        if img_error:
            st.error(f"Image engine not available: {img_error}")
        else:
            with st.spinner("Generating image... this takes 20-40 seconds on first run"):
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

    # ── Display generated image ───────────────────────────────
    if st.session_state.get("generated_image"):
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">Generated Image</div>', unsafe_allow_html=True)
        st.image(
            st.session_state.generated_image,
            caption=f"{meta['topic']} | {meta['platform']} | {meta['tone']}",
            use_column_width=True,
        )
        st.download_button(
            label="⬇️ Download Image (.png)",
            data=st.session_state.generated_image,
            file_name=f"{meta['topic'][:20].replace(' ','_')}_image.png",
            mime="image/png",
        )

    # ── Brand Memory Viewer ───────────────────────────────────
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    with st.expander("Brand Memory — Retrieved Context"):
        if db and use_memory:
            ctx = db.find_similar(content_type, topic, audience)
            if ctx:
                st.markdown(f"```\n{ctx}\n```")
            else:
                st.info("No similar past content found. This was a fresh generation.")