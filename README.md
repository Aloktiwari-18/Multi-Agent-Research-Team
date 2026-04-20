# Multi-Agent AI Research Team 🧠

A full-stack, production-ready AI orchestration project that demonstrates autonomous agents reasoning, critiquing, and self-correcting to produce high-quality research reports.

This project moves beyond simple "input-output" prompting. It uses **LangGraph** to orchestrate a team of agents (Supervisor, Researcher, Writer, Fact-Checker) in a cyclic graph workflow.

![App Screenshot](./assets/demo1.png)
![App Screenshot](./assets/demo2.png)
![App Screenshot](./assets/demo3.png)

---

## 🚀 Features

* **Multi-Agent Orchestration**: Powered by LangGraph for cyclical workflows (e.g. Writer ↔ Fact-Checker revision loop).
* **FastAPI Backend**: Robust API with Server-Sent Events (SSE) streaming for real-time UI updates.
* **Streamlit Frontend**: Modern dashboard with dark/light theme support.
* **Built-in Demo Mode**: Run the entire pipeline without API keys for quick demos.
* **PDF Export**: Generates a clean, professional research whitepaper (with TOC, tables, styling).
* **Groq-Powered LLM**: Ultra-fast inference using Groq’s optimized LLMs.

---

## 🧠 The Agent Team

1. **Supervisor**

   * Breaks user query into structured research tasks

2. **Researcher**

   * Uses Tavily AI for real-time web search
   * Collects and formats source-backed data

3. **Writer**

   * Generates a structured, professional Markdown report
   * Incorporates feedback from Fact-Checker

4. **Fact-Checker**

   * Validates claims against sources
   * Forces revision loop if confidence < 70%

---

## 🛠️ Tech Stack

* **Orchestration**: `langgraph`, `langchain`
* **LLM Engine**: Groq (`langchain-groq`)
* **Recommended Models**:

  * `llama-3.1-8b-instant` ⚡ (fast)
  * `llama-3.3-70b-versatile` 🧠 (high quality)
* **Search Engine**: Tavily AI (`tavily-python`)
* **Backend**: `fastapi`, `uvicorn`, `sse-starlette`
* **Frontend**: `streamlit`, `sseclient-py`
* **PDF Generation**: `reportlab`

---

## ⚡ Quickstart (Demo Mode)

Run the project instantly without API keys.

### 1. Clone the repository

```bash
git clone https://github.com/manpatell/Multi-Agent-Research-Team.git
cd Multi-Agent-Research-Team
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start Backend

```bash
uvicorn backend.main:app --reload --port 8000
```

### 4. Start Frontend

```bash
streamlit run frontend/app.py
```

### 5. Run Demo

* Open: http://localhost:8501
* Enable **Demo Mode**
* Enter any query
* Click **Run Research**

---

## 🔑 Running with Real API Keys (Groq)

### 1. Create `.env` file

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

### 2. Or enter keys in Streamlit sidebar

### 3. Turn OFF Demo Mode

---

## 🧱 Architecture

```
User Query → FastAPI (SSE Stream) → LangGraph StateGraph
                                     ↓
                              (1) Supervisor
                                     ↓
                              (2) Researcher (Tavily)
                                     ↓
             ┌────────────── (3) Writer
             ↑                      ↓
      (Revision Loop)        (4) Fact-Checker
             ↑                      ↓
             └─────────────── If confidence < 70
                                     ↓
                              Final Report
```

---

## ⚡ Performance

* ⚡ Groq inference = extremely fast responses
* 🔁 Multi-agent loop ensures high-quality output
* 📄 PDF export for professional usage

---

## 📄 License

MIT License
