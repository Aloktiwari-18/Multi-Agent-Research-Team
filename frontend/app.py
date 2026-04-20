"""Streamlit dashboard for the Multi-Agent AI Research Team."""

from __future__ import annotations

import json
from fpdf import FPDF
import requests
import streamlit as st
from fpdf import FPDF

# ── Page config ──────────────────────────────────────────────

st.set_page_config(
    page_title="Research Team · AI Agents",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Professional Dark Theme ──────────────────────────────────

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        --bg-primary: #ffffff;
        --bg-secondary: #f9fafb;
        --bg-tertiary: #f3f4f6;
        --bg-elevated: #ffffff;
        --border-subtle: #e5e7eb;
        --border-medium: #d1d5db;
        --text-primary: #111827;
        --text-secondary: #4b5563;
        --text-tertiary: #6b7280;
        --accent: #2563eb;
        --accent-muted: rgba(37, 99, 235, 0.1);
        --green: #16a34a;
        --green-muted: rgba(22, 163, 74, 0.1);
        --amber: #d97706;
        --amber-muted: rgba(217, 119, 6, 0.1);
        --red: #dc2626;
        --red-muted: rgba(220, 38, 38, 0.1);
    }

    /* ── Global ─────────────────────────────────── */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        -webkit-font-smoothing: antialiased;
    }
    .stApp {
        background: var(--bg-primary);
    }
    .block-container {
        padding-top: 2rem;
        max-width: 1100px;
    }

    /* ── Sidebar ────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: var(--bg-secondary);
        border-right: 1px solid var(--border-subtle);
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
        padding-top: 1.5rem;
    }
    section[data-testid="stSidebar"] * {
        color: var(--text-primary) !important;
    }
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p {
        color: var(--text-primary) !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
    }
    section[data-testid="stSidebar"] .sidebar-section-label {
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        margin: 1.25rem 0 0.5rem 0 !important;
    }
    section[data-testid="stSidebar"] .stTextInput input {
        background: var(--bg-tertiary) !important;
        border: 1px solid var(--border-subtle) !important;
        color: var(--text-primary) !important;
        border-radius: 6px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.82rem !important;
    }
    section[data-testid="stSidebar"] .stTextInput input:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 1px var(--accent) !important;
    }
    section[data-testid="stSidebar"] .stSelectbox > div > div {
        background: var(--bg-tertiary) !important;
        border: 1px solid var(--border-subtle) !important;
        color: var(--text-primary) !important;
        border-radius: 6px !important;
    }

    /* ── Header ─────────────────────────────────── */
    .app-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.25rem;
    }
    .app-header-icon {
        width: 36px;
        height: 36px;
        background: var(--accent-muted);
        border: 1px solid rgba(59, 130, 246, 0.25);
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        flex-shrink: 0;
    }
    .app-header h1 {
        font-size: 1.35rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 0;
        letter-spacing: -0.02em;
    }
    .app-subtitle {
        color: var(--text-tertiary);
        font-size: 0.85rem;
        margin: 0 0 1.75rem 0;
        font-weight: 400;
    }

    /* ── Query input ────────────────────────────── */
    .stTextArea textarea {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
        font-size: 0.92rem !important;
        padding: 0.85rem 1rem !important;
        line-height: 1.5 !important;
        resize: none !important;
    }
    .stTextArea textarea:focus {
        border-color: var(--border-medium) !important;
        box-shadow: none !important;
    }
    .stTextArea textarea::placeholder {
        color: var(--text-tertiary) !important;
    }

    /* ── Primary button ─────────────────────────── */
    .stButton > button[kind="primary"],
    button[data-testid="stBaseButton-primary"] {
        background: var(--text-primary) !important;
        color: var(--bg-primary) !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        letter-spacing: -0.01em !important;
        padding: 0.5rem 1.25rem !important;
        transition: opacity 0.15s ease !important;
    }
    .stButton > button[kind="primary"]:hover,
    button[data-testid="stBaseButton-primary"]:hover {
        opacity: 0.85 !important;
        background: var(--text-primary) !important;
        color: var(--bg-primary) !important;
    }

    /* ── Agent log entries ──────────────────────── */
    .agent-log {
        display: flex;
        align-items: flex-start;
        gap: 0.6rem;
        padding: 0.6rem 0;
        border-bottom: 1px solid var(--border-subtle);
        font-size: 0.88rem;
        color: var(--text-secondary);
        line-height: 1.55;
    }
    .agent-log:last-child {
        border-bottom: none;
    }
    .agent-log-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: var(--accent);
        margin-top: 0.45rem;
        flex-shrink: 0;
    }
    .agent-log-dot.supervisor { background: var(--accent); }
    .agent-log-dot.researcher { background: var(--amber); }
    .agent-log-dot.writer { background: var(--green); }
    .agent-log-dot.fact_checker { background: var(--red); }
    .agent-log-dot.status { background: var(--text-tertiary); }
    .agent-log-dot.done { background: var(--green); }

    /* ── Status container ──────────────────────── */
    details[data-testid="stExpander"] {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 8px !important;
    }
    details[data-testid="stExpander"] summary {
        color: var(--text-primary) !important;
    }
    [data-testid="stStatusWidget"] {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 8px !important;
    }

    /* ── Report section ─────────────────────────── */
    .report-divider {
        border: none;
        border-top: 1px solid var(--border-subtle);
        margin: 2rem 0;
    }
    .report-title {
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--text-tertiary);
        margin-bottom: 1.25rem;
    }

    /* ── Download button ────────────────────────── */
    .stDownloadButton > button {
        background: var(--bg-tertiary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        transition: background 0.15s ease !important;
    }
    .stDownloadButton > button:hover {
        background: var(--bg-elevated) !important;
        border-color: var(--border-medium) !important;
    }

    /* ── Toggle ─────────────────────────────────── */
    .stToggle label span {
        color: var(--text-primary) !important;
        font-size: 0.85rem !important;
    }

    /* ── Markdown in report ─────────────────────── */
    .stMarkdown p, .stMarkdown li {
        color: var(--text-secondary);
        line-height: 1.7;
    }
    .stMarkdown h1 {
        color: var(--text-primary);
        font-size: 1.4rem;
        font-weight: 600;
        border-bottom: 1px solid var(--border-subtle);
        padding-bottom: 0.6rem;
        margin-top: 1.5rem;
    }
    .stMarkdown h2 {
        color: var(--text-primary);
        font-size: 1.1rem;
        font-weight: 600;
        margin-top: 1.5rem;
    }
    .stMarkdown h3 {
        color: var(--text-primary);
        font-size: 0.95rem;
        font-weight: 600;
    }
    .stMarkdown a {
        color: var(--accent);
        text-decoration: none;
    }
    .stMarkdown a:hover {
        text-decoration: underline;
    }
    .stMarkdown table {
        border-collapse: collapse;
        width: 100%;
        font-size: 0.88rem;
    }
    .stMarkdown th {
        background: var(--bg-tertiary);
        color: var(--text-secondary);
        font-weight: 600;
        text-align: left;
        padding: 0.55rem 0.75rem;
        border-bottom: 1px solid var(--border-medium);
    }
    .stMarkdown td {
        padding: 0.55rem 0.75rem;
        border-bottom: 1px solid var(--border-subtle);
        color: var(--text-secondary);
    }
    .stMarkdown strong {
        color: var(--text-primary);
        font-weight: 600;
    }

    /* ── Sidebar brand ──────────────────────────── */
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0 0 1rem 0;
        margin-bottom: 1rem;
        border-bottom: 1px solid var(--border-subtle);
    }
    .sidebar-brand-icon {
        width: 28px;
        height: 28px;
        background: var(--accent-muted);
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.85rem;
    }
    .sidebar-brand span {
        font-size: 0.88rem;
        font-weight: 600;
        color: var(--text-primary);
    }
    .sidebar-section-label {
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--text-tertiary);
        margin: 1.25rem 0 0.5rem 0;
    }
    .sidebar-footer {
        font-size: 0.75rem;
        color: var(--text-tertiary);
        margin-top: 1.5rem;
        padding-top: 1rem;
        border-top: 1px solid var(--border-subtle);
    }

    /* ── Warning/info boxes ─────────────────────── */
    .stAlert {
        background: var(--bg-tertiary) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: 6px !important;
        color: var(--text-secondary) !important;
    }

    /* ── Hide Streamlit chrome ──────────────────── */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar ──────────────────────────────────────────────────

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-brand-icon">◆</div>
            <span>Research Team</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sidebar-section-label">Mode</div>', unsafe_allow_html=True)
    demo_mode = st.toggle(
        "Demo mode — no API keys needed",
        value=True,
        help="Runs a simulated pipeline with sample data and realistic delays",
    )

    st.markdown('<div class="sidebar-section-label">API Keys</div>', unsafe_allow_html=True)
    groq_key = st.text_input(
        "Groq",
        type="password",
        placeholder="gsk_...",
        disabled=demo_mode,
    )
    tavily_key = st.text_input(
        "Tavily",
        type="password",
        placeholder="tvly-...",
        disabled=demo_mode,
    )
    langsmith_key = st.text_input(
        "LangSmith (optional)",
        type="password",
        placeholder="lsv2-...",
        disabled=demo_mode,
    )

    st.markdown('<div class="sidebar-section-label">Model</div>', unsafe_allow_html=True)
    model_choice = st.selectbox(
        "LLM",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"],
        index=0,
        label_visibility="collapsed",
        disabled=demo_mode,
    )

    st.markdown('<div class="sidebar-section-label">Backend</div>', unsafe_allow_html=True)
    backend_url = st.text_input(
        "URL",
        value="https://multi-agent-research-team.onrender.com",
        label_visibility="collapsed",
    )

    st.markdown(
        '<div class="sidebar-footer">LangGraph · FastAPI · Streamlit</div>',
        unsafe_allow_html=True,
    )

# ── Header ───────────────────────────────────────────────────

st.markdown(
    """
    <div class="app-header">
        <div class="app-header-icon">◆</div>
        <h1>Multi-Agent Research Team</h1>
    </div>
    <p class="app-subtitle">
        Supervisor → Researcher → Writer → Fact-Checker &nbsp;·&nbsp; Claude 3.5 Sonnet &nbsp;·&nbsp; LangGraph
    </p>
    """,
    unsafe_allow_html=True,
)

# ── Query input ──────────────────────────────────────────────

query = st.text_area(
    "query",
    placeholder="Describe what you want researched — e.g. \"Analyze the impact of 2026 interest rate hikes on the renewable energy sector and write a whitepaper with citations.\"",
    height=90,
    label_visibility="collapsed",
)

col_spacer, col_btn = st.columns([4, 1])
with col_btn:
    run_clicked = st.button("Run research →", use_container_width=True, type="primary")


# ── Helpers ──────────────────────────────────────────────────
# ── Helpers ──────────────────────────────────────────────────
from reportlab.platypus import (
    Paragraph, Spacer, Table, TableStyle,
    PageBreak, Frame, PageTemplate, BaseDocTemplate
)
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from io import BytesIO
import re

# ─────────────────────────────────────────────
# CLEAN TEXT (REMOVE EMOJIS)
# ─────────────────────────────────────────────
def clean_text(text):
    return re.sub(r'[^\x00-\x7F]+', '', text)


# ─────────────────────────────────────────────
# TABLE PARSER
# ─────────────────────────────────────────────
def parse_table(lines):
    table_data = []
    for line in lines:
        row = [cell.strip() for cell in line.split("|") if cell.strip()]
        if row:
            table_data.append(row)
    return table_data if len(table_data) > 1 else None


# ─────────────────────────────────────────────
# HEADER + FOOTER + WATERMARK
# ─────────────────────────────────────────────
def add_page_design(canvas, doc):
    width, height = letter

    canvas.setFont("Helvetica-Bold", 10)
    canvas.setFillColor(colors.darkblue)
    canvas.drawString(40, height - 30, "AI Research Report")

    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.grey)
    canvas.drawString(40, 20, "Generated by Multi-Agent AI System")

    canvas.drawRightString(width - 40, 20, f"Page {doc.page}")

    canvas.setFont("Helvetica-Bold", 40)
    canvas.setFillColor(colors.lightgrey)
    canvas.saveState()
    canvas.translate(300, 400)
    canvas.rotate(45)
    canvas.drawCentredString(0, 0, "CONFIDENTIAL")
    canvas.restoreState()


# ─────────────────────────────────────────────
# CUSTOM DOC TEMPLATE (TOC SUPPORT)
# ─────────────────────────────────────────────
class MyDocTemplate(BaseDocTemplate):
    def __init__(self, buffer, **kwargs):
        super().__init__(buffer, **kwargs)
        frame = Frame(self.leftMargin, self.bottomMargin, self.width, self.height)
        template = PageTemplate(id='main', frames=frame, onPage=add_page_design)
        self.addPageTemplates([template])

    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            text = flowable.getPlainText()

            if flowable.style.name == "HeadingStyle":
                self.notify('TOCEntry', (0, text, self.page))

            elif flowable.style.name == "SubHeadingStyle":
                self.notify('TOCEntry', (1, text, self.page))


# ─────────────────────────────────────────────
# MAIN PDF FUNCTION
# ─────────────────────────────────────────────
def _generate_pdf(markdown_text: str) -> bytes:
    buffer = BytesIO()

    doc = MyDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=60,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    # STYLES
    title_style = ParagraphStyle(
        name="TitleStyle",
        parent=styles["Heading1"],
        fontSize=24,
        textColor=colors.darkblue,
        alignment=1,
        spaceAfter=20,
    )

    heading_style = ParagraphStyle(
        name="HeadingStyle",
        parent=styles["Heading2"],
        fontSize=16,
        textColor=colors.blue,
        spaceAfter=10,
    )

    sub_heading_style = ParagraphStyle(
        name="SubHeadingStyle",
        parent=styles["Heading3"],
        fontSize=13,
        textColor=colors.darkblue,
        spaceAfter=8,
    )

    body_style = ParagraphStyle(
        name="BodyStyle",
        parent=styles["BodyText"],
        fontSize=11.5,
        leading=18,
        spaceAfter=6,
    )

    content = []

    # COVER PAGE
    content.append(Spacer(1, 30))
    content.append(Paragraph("AI Research Report", title_style))
    content.append(Spacer(1, 20))
    content.append(Paragraph("Generated by Multi-Agent AI System", body_style))
    content.append(PageBreak())

    # TABLE OF CONTENTS
    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle(name='TOCHeading1', fontSize=12, leftIndent=20),
        ParagraphStyle(name='TOCHeading2', fontSize=10, leftIndent=40),
    ]

    content.append(Paragraph("Table of Contents", title_style))
    content.append(Spacer(1, 12))
    content.append(toc)
    content.append(PageBreak())

    # MAIN CONTENT
    lines = markdown_text.split("\n")
    i = 0

    while i < len(lines):
        line = clean_text(lines[i])

        if not line.strip():
            content.append(Spacer(1, 8))
            i += 1
            continue

        if line.startswith("## "):
            content.append(Paragraph(line[3:], heading_style))
            i += 1
            continue

        elif line.startswith("### "):
            content.append(Paragraph(line[4:], sub_heading_style))
            i += 1
            continue

        elif line.startswith("# "):
            content.append(Paragraph(line[2:], title_style))
            i += 1
            continue

        # TABLE DETECTION
        if "|" in line:
            table_lines = []
            while i < len(lines) and "|" in lines[i]:
                table_lines.append(clean_text(lines[i]))
                i += 1

            table_data = parse_table(table_lines)
            if table_data:
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ]))
                content.append(table)
                content.append(Spacer(1, 10))
            continue

        elif line.startswith("- "):
            content.append(Paragraph("• " + line[2:], body_style))

        else:
            content.append(Paragraph(line, body_style))

        content.append(Spacer(1, 6))
        i += 1

    doc.build(content)

    pdf = buffer.getvalue()
    buffer.close()
    return pdf

def _agent_dot_class(agent: str) -> str:
    """Map agent name to a dot colour class."""
    mapping = {
        "supervisor": "supervisor",
        "researcher": "researcher",
        "writer": "writer",
        "fact_checker": "fact_checker",
    }
    return mapping.get(agent, "status")


def _stream_research(query: str, url: str, is_demo: bool = False) -> None:
    """Call the FastAPI SSE endpoint and render agent events live."""
    payload = {
        "query": query,
        "groq_api_key": groq_key or None,
        "tavily_api_key": tavily_key or None,
        "langchain_api_key": langsmith_key or None,
        "llm_model": model_choice,
        "demo_mode": is_demo,
    }

    log_container = st.container()

    try:
        with requests.post(
            f"{url}/api/research",
            json=payload,
            stream=True,
            timeout=300,
        ) as resp:
            resp.raise_for_status()
            final_report = ""
            current_event = ""
            current_agent = "status"

            for raw_line in resp.iter_lines(decode_unicode=True):
                if not raw_line:
                    continue

                if raw_line.startswith("event: "):
                    current_event = raw_line[7:].strip()
                    continue

                if raw_line.startswith("data: "):
                    data_str = raw_line[6:]
                    try:
                        data = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue

                    if current_event in ("status", "agent_log"):
                        msg = data.get("message", "")
                        agent = data.get("agent", current_event)
                        dot_cls = _agent_dot_class(agent)
                        if msg:
                            with log_container:
                                st.markdown(
                                    f'<div class="agent-log">'
                                    f'<div class="agent-log-dot {dot_cls}"></div>'
                                    f'<div>{msg}</div>'
                                    f'</div>',
                                    unsafe_allow_html=True,
                                )

                    elif current_event == "final_report":
                        final_report = data.get("report", "")

                    elif current_event == "error":
                        st.error(data.get("message", "Unknown error"))

                    elif current_event == "done":
                        with log_container:
                            st.markdown(
                                f'<div class="agent-log">'
                                f'<div class="agent-log-dot done"></div>'
                                f'<div>{data.get("message", "Done")}</div>'
                                f'</div>',
                                unsafe_allow_html=True,
                            )

            # ── Final report ─────────────────────────────────
            if final_report:
                st.markdown("## 📄 Final Report")
                st.markdown(final_report)

                pdf_bytes = _generate_pdf(final_report)

                st.download_button(
                    "⬇️ Download PDF",
                    data=pdf_bytes,
                    file_name="research_report.pdf",
                    mime="application/pdf",
                )
            else:
                st.warning("Pipeline finished but no final report was produced.")

    except requests.ConnectionError:
        st.error(
            f"Could not connect to the backend at **{url}**. "
            "Start it with: `uvicorn backend.main:app --port 8000`"
        )
    except Exception as e:
        st.error(f"Error: {e}")


# ── Run ──────────────────────────────────────────────────────

if run_clicked:
    if not query.strip():
        st.warning("Enter a research query above.")
    elif not demo_mode and not groq_key:
        st.warning("Provide your Groq API key or enable demo mode.")
    elif not demo_mode and not tavily_key:
        st.warning("Provide your Tavily API key or enable demo mode.")
    else:
        with st.status("Agents working…", expanded=True) as status:
            _stream_research(query.strip(), backend_url.rstrip("/"), is_demo=demo_mode)
            status.update(label="Complete", state="complete", expanded=True)
