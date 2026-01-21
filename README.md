# NIFTY 50 RAG Application (Django)

A **personal market co-pilot** for structured NIFTY 50 analysis built using  
**Retrieval-Augmented Generation (RAG)**, private trading journals, and rule-based prompts.

This application is designed to **enforce process discipline, capture learning, and reduce discretionary mistakes** — not to generate blind buy/sell signals.

---

## 🎯 Purpose

The app helps answer questions like:
- What is today’s NIFTY 50 outlook based on my rules and past experience?
- Have I seen this type of market behavior before?
- What mistakes do I usually make on slow or breakdown days?
- How should I frame today’s market bias and risk?

It combines:
- Your **private trading knowledge**
- A **locked professional analysis prompt**
- A **retrieval layer (FAISS)**
- An **LLM (GPT-4.1-mini)**

---

## 🧠 Core Philosophy

- Bias is a hypothesis. Price is the truth.
- Rules are **constraints**, not suggestions.
- Memory beats indicators.
- Consistency beats prediction.
- Process > outcome.

---

## 🏗️ High-Level Architecture

Browser (/ask/)  
→ Django View  
→ RAG Service Layer  
→ FAISS Vector Store (Rules + Playbooks)  
→ Journal & Metadata Context  
→ Locked Prompt (A–F Structure)  
→ OpenAI LLM (GPT-4.1-mini)  
→ Structured NIFTY 50 Outlook

---

## 📁 Project Structure

nifty_rag_django/  
├── manage.py  
├── Pipfile  
├── .env  
│  
├── nifty_rag/                # Django project  
│  
├── ragapp/                   # Core RAG logic  
│   ├── services.py           # RAG orchestration  
│   ├── prompts.py            # Locked prompts & constraints  
│   ├── views.py  
│   ├── urls.py  
│   └── templates/  
│  
├── trading_knowledge/  
│   ├── journals/             # Daily journals (.md)  
│   ├── playbooks/            # Strategy playbooks (.md)  
│   ├── rules/                # Extracted rules (.md)  
│   ├── metadata/             # journal_metadata_YYYY.json  
│   └── summaries/            # (future use)  
│  
└── faiss_index/              # Auto-generated vector index

---

## 🧩 How the Application Works

### Locked Daily Prompt
The application always runs a predefined **A–F NIFTY 50 analysis prompt**.
User input is treated only as **extra instruction**, never replacing the core structure.

### Retrieval-Augmented Generation
- Stable retrieval from FAISS for rules/playbooks
- Metadata-aware journal retrieval for similar past market days

### LLM Reasoning
- Model: GPT-4.1-mini
- Low temperature for discipline
- Explicit no-hallucination instruction

---

## 🚀 Getting Started (Local)

1. Install dependencies
pipenv install  
pipenv shell  

2. Create .env with OpenAI key and DB credentials

3. Build index
python manage.py build_index  

4. Run server
python manage.py migrate  
python manage.py runserver  

Visit http://127.0.0.1:8000/ask/

---

## ❌ What This App Is NOT

- Not a trading bot
- Not a signal generator
- Not real-time execution
- Not financial advice

---

## 📌 Summary

A memory-backed, rule-driven NIFTY 50 analysis system that enforces process,
captures experience, and prevents repeating mistakes — while keeping the trader in control.
