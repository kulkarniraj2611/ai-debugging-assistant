# 🔧 AI-Powered Code Debugging Assistant

An intelligent Python debugging assistant built with **Streamlit**, **Groq AI (LLaMA 3.1)**, and **Python AST analysis**.

---

## Features
- 🔍 AI-powered bug detection and explanation
- 🔴🟡🟢 Error severity rating (High / Medium / Low)
- ✅ Auto-generated fixed code
- 📊 Code complexity analyzer (lines, functions, loops, classes)
- 📜 Debug session history
- ⬇️ Download fixed code

## Tech Stack
- **Python** — core language
- **Streamlit** — UI framework
- **Groq API (LLaMA 3.1)** — AI model
- **Python AST** — static code analysis

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Create `.env` file
```
GROQ_API_KEY=your_groq_api_key_here
```
Get a free key from: https://console.groq.com

### 3. Run the app
```bash
streamlit run apps/debugging_assistant/app.py
```

## Project Structure
```
debugging_assistant/
├── apps/
│   └── debugging_assistant/
│       └── app.py          ← Main Streamlit UI
├── config/
│   ├── config.yaml         ← Model configuration
│   └── model_config.py     ← Config loader
├── utils/
│   ├── llm_client.py       ← Groq API client
│   ├── debugging_helper.py ← Prompt builder + AST analyzer
│   └── prompts/
│       └── debugging_prompt.json ← AI prompt template
├── .env                    ← API key (not in GitHub)
└── requirements.txt
```
