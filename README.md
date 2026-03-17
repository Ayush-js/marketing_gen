# ✦ Marketing Content Generator

A GenAI-powered tool that transforms topics into high-quality marketing content using **Groq LLM**, **ChromaDB Vector Memory**, and a **Streamlit UI**.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red)
![Groq](https://img.shields.io/badge/Groq-LLM-orange)
![ChromaDB](https://img.shields.io/badge/ChromaDB-VectorDB-green)

---

## ✨ Features
- 📋 4 Content Types: Ad Copy, Social Media Posts, Email Campaigns, Product Descriptions
- 🎨 8 Brand Tones: Professional, Friendly, Luxury, Bold & Edgy, and more
- 🧠 Brand Memory: ChromaDB stores all generations for brand consistency
- 🎨 AI Image Prompt Generator: Ready-to-use prompts for Midjourney/DALL·E
- 📄 Export: Download as `.txt` or `.docx`
- 🕐 History Panel: Browse all past generations

---

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/marketing_gen.git
cd marketing_gen
```

### 2. Create virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API key
```bash
cp .env.example .env
```
Open `.env` and add your Groq API key from [console.groq.com](https://console.groq.com)

### 5. Run the app
```bash
streamlit run ui/app.py
```

Open **http://localhost:8501** in your browser.

---

## 📁 Project Structure
```
marketing_gen/
├── core/
│   └── llm_engine.py         # Groq API connection & generation
├── prompts/
│   └── templates.py          # Prompt engineering templates
├── vectordb/
│   └── store.py              # ChromaDB vector store manager
├── ui/
│   └── app.py                # Streamlit web interface
├── utils/
│   └── exporter.py           # .txt and .docx export
├── .env.example              # Environment variables template
└── requirements.txt
```

---

## 🔑 Environment Variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Your Groq API key (required) |
| `GROQ_MODEL` | Model name (default: llama-3.3-70b-versatile) |
| `MAX_TOKENS` | Max output length (default: 1024) |
| `TEMPERATURE` | Creativity 0-1 (default: 0.75) |

---

Built with ❤️ using Python, Groq, ChromaDB, and Streamlit.