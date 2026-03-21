# Marketing Content Generator

A GenAI-powered web application that transforms topic inputs into professional marketing content using Groq LLM, ChromaDB vector memory, Hugging Face image generation, and Streamlit.

Live App: https://marketinggen-hdxstvx33cpb868akgjryi.streamlit.app

---

## What It Does

Marketing professionals spend hours manually writing ad copy, social media posts, email campaigns, and product descriptions. This tool solves that by generating structured, platform-ready marketing content in seconds — and now also generates photorealistic marketing images using FLUX.1-schnell.

---

## Features

- 4 content types: Ad Copy, Social Media Posts, Email Campaigns, Product Descriptions
- 8 brand tones: Professional, Friendly, Luxury, Bold and Edgy, Minimalist, Playful, Inspirational, Urgency-Driven
- Brand memory using ChromaDB — stores every generation and retrieves similar past content to maintain brand voice consistency
- AI image prompt generator — creates detailed prompts for Midjourney, DALL-E, and Adobe Firefly
- Real AI image generation using FLUX.1-schnell via Hugging Face Inference API
- Export generated content as .txt or formatted .docx Word document
- Generation history panel with filtering by content type
- Token usage tracking per generation

---

## Content Type Frameworks

| Content Type | Framework | Output |
|---|---|---|
| Ad Copy | AIDA | Headline, Subheadline, Body, CTA, A/B Variant |
| Social Media Posts | Hook-Story-CTA | Hook, Caption, Hashtags, Engagement Question, Reel Concept |
| Email Campaign | PAS | Subject Line, Preview Text, Hook, Body, CTA Button, P.S. |
| Product Description | FAB | SEO Title, Hero Description, Features, Specs, Meta Description, Closer |

---

## Technology Stack

| Technology | Role |
|---|---|
| Python 3.10+ | Core language |
| Groq API (llama-3.3-70b-versatile) | Text generation — fastest LLM inference available |
| Hugging Face API (FLUX.1-schnell) | Photorealistic image generation |
| ChromaDB | Local vector database for brand memory |
| Streamlit | Web UI framework |
| sentence-transformers | Text embeddings for ChromaDB semantic search |
| python-dotenv | Environment variable management |
| python-docx | Word document export |

---

## Project Structure

```
marketing_gen/
├── core/
│   ├── llm_engine.py       # Groq API — text generation and image prompts
│   └── image_engine.py     # Hugging Face API — FLUX.1-schnell image generation
├── prompts/
│   └── templates.py        # Prompt engineering templates, tones, platforms
├── vectordb/
│   └── store.py            # ChromaDB vector store manager
├── ui/
│   └── app.py              # Streamlit web interface
├── utils/
│   └── exporter.py         # .txt and .docx export
├── .env                    # API keys and config (not committed)
├── .env.example            # Safe template
├── requirements.txt
└── README.md
```

---

## Local Setup

### Prerequisites
- Python 3.10 or higher
- Groq API key from console.groq.com
- Hugging Face API key from huggingface.co

### Installation

```bash
# Clone the repository
git clone https://github.com/Ayush-js/marketing_gen.git
cd marketing_gen

# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
CHROMA_DB_PATH=./vectordb/chroma_store
MAX_TOKENS=1024
TEMPERATURE=0.75
HF_API_KEY=your_huggingface_api_key_here
HF_MODEL=black-forest-labs/FLUX.1-schnell
```

### Run

```bash
streamlit run ui/app.py
```

Open http://localhost:8501 in your browser.

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| GROQ_API_KEY | required | Groq API key from console.groq.com |
| GROQ_MODEL | llama-3.3-70b-versatile | Groq model for text generation |
| MAX_TOKENS | 1024 | Maximum output length in tokens |
| TEMPERATURE | 0.75 | Creativity level (0 = precise, 1 = creative) |
| CHROMA_DB_PATH | ./vectordb/chroma_store | Local path for ChromaDB storage |
| HF_API_KEY | required | Hugging Face API key from huggingface.co |
| HF_MODEL | black-forest-labs/FLUX.1-schnell | Image generation model |

---

## How Brand Memory Works

Every generation is saved to ChromaDB as a vector embedding. When a new generation is requested, the system searches for past content with over 30 percent semantic similarity to the current topic and audience. If found, that content is injected into the LLM prompt as brand context — ensuring the new generation matches your existing tone and terminology automatically.

---

## Image Generation

The image generation feature works in two steps:

1. Click Image Prompt — Groq generates a detailed, platform-optimized image prompt based on your content
2. Click Generate Image — the prompt is sent to FLUX.1-schnell via Hugging Face Inference API, producing a 1024x1024 photorealistic marketing visual

The generated image can be downloaded as a PNG. The image prompt can also be copied and pasted into Midjourney, DALL-E, or Adobe Firefly.

---

## Deployment on Streamlit Cloud

1. Push code to GitHub
2. Go to share.streamlit.io and sign in with GitHub
3. Create new app: Repository = this repo, Branch = main, File = ui/app.py
4. Add secrets in Advanced Settings:

```toml
GROQ_API_KEY = "your_groq_key"
GROQ_MODEL = "llama-3.3-70b-versatile"
CHROMA_DB_PATH = "/tmp/chroma_store"
MAX_TOKENS = "1024"
TEMPERATURE = "0.75"
HF_API_KEY = "your_hf_key"
HF_MODEL = "black-forest-labs/FLUX.1-schnell"
```

5. Click Deploy

Note: On Streamlit Cloud free tier, ChromaDB uses /tmp/chroma_store which resets on container restart. Brand memory history does not persist between sessions on the cloud.

Every git push to the main branch triggers an automatic redeploy.

---

## Pushing Updates

```bash
git add .
git commit -m "your update description"
git push
```

---

## Roadmap

- Phase 3: Brand profile manager — save tone and audience presets per brand
- Phase 3: Batch generation — generate multiple variations at once
- Phase 3: Persistent cloud storage using Pinecone or Supabase
- Phase 4: Analytics dashboard — token usage, content type trends
- Phase 4: Multi-language content generation

---

## Group

Group 13D10

Built with Python, Groq AI, ChromaDB, Hugging Face, and Streamlit.