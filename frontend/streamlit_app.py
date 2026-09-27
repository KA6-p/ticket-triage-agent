import os
import requests
import streamlit as st


# ============================================================
# Configuration
# ============================================================

API = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Ticket Triage Agent",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded",
)

PRIORITY_COLORS = {
    "critical": "#D6455D",
    "high": "#DB8A32",
    "medium": "#3E6FD9",
    "low": "#8A93A6",
}

PRIORITY_DOTS = {
    "critical": "🔴",
    "high": "🟠",
    "medium": "🔵",
    "low": "⚪",
}


# ============================================================
# API helper
# ============================================================

def api(path, method="get", **kwargs):
    response = requests.request(method, API + path, timeout=120, **kwargs)
    response.raise_for_status()
    return response.json()


# ============================================================
# Styling
# ============================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

    :root {
        --ink: #14181F;
        --ink-soft: #3A4150;
        --slate: #6B7280;
        --line: #E3E6EB;
        --canvas: #FAFBFC;
        --surface: #FFFFFF;
        --success: #1F8A5F;
        --critical: #D6455D;
        --high: #DB8A32;
        --medium: #3E6FD9;
        --low: #8A93A6;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, sans-serif;
        color: var(--ink);
    }

    .stApp {
        background: var(--canvas);
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1180px;
    }

    code, .mono {
        font-family: 'IBM Plex Mono', monospace !important;
    }

    /* Streamlit auto-switches to a dark theme based on the visitor's
       OS setting. These rules force every native Streamlit text
       element back to our palette so the app looks the same for
       everyone, light mode or dark mode. */
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"] {
        background: var(--canvas) !important;
    }

    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stMarkdownContainer"] span,
    [data-testid="stMarkdownContainer"] strong,
    label p, label span {
        color: var(--ink) !important;
    }

    [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p {
        color: var(--slate) !important;
    }

    .stTextInput input,
    .stTextArea textarea {
        background: var(--surface) !important;
        color: var(--ink) !important;
        border: 1px solid var(--line) !important;
        border-radius: 5px !important;
    }
    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {
        color: var(--slate) !important;
        opacity: 1 !important;
    }
    .stTextInput label p,
    .stTextArea label p,
    .stSelectbox label p {
        color: var(--ink-soft) !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
    }

    [data-baseweb="select"] > div {
        background: var(--surface) !important;
        border: 1px solid var(--line) !important;
    }
    [data-baseweb="select"] * {
        color: var(--ink) !important;
    }
    [data-baseweb="popover"] li {
        color: var(--ink) !important;
    }

    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary p,
    [data-testid="stExpander"] summary span {
        color: var(--ink) !important;
    }

    /* ---- Header ---- */
    .app-title {
        font-size: 1.6rem;
        font-weight: 700;
        letter-spacing: -0.01em;
        margin-bottom: 0.15rem;
        color: var(--ink) !important;
    }
    .app-caption {
        color: var(--slate) !important;
        font-size: 0.92rem;
        margin-bottom: 1.6rem;
        max-width: 640px;
        line-height: 1.5;
    }

    /* ---- Section labels ---- */
    .section-label {
        font-size: 0.95rem;
        font-weight: 600;
        color: var(--ink) !important;
        margin: 0 0 0.7rem 0;
    }

    /* ---- KPI cards ---- */
    .kpi-row {
        display: flex;
        gap: 0.75rem;
        margin-bottom: 1.6rem;
    }
    .kpi-card {
        flex: 1;
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 6px;
        padding: 0.9rem 1.1rem;
    }
    .kpi-value {
        font-size: 1.7rem;
        font-weight: 700;
        line-height: 1.1;
        font-family: 'IBM Plex Mono', monospace;
        color: var(--ink) !important;
    }
    .kpi-label {
        color: var(--slate) !important;
        font-size: 0.82rem;
        margin-top: 0.25rem;
    }

    /* ---- Bars (category / priority) ---- */
    .bar-row {
        margin-bottom: 0.65rem;
    }
    .bar-head {
        display: flex;
        justify-content: space-between;
        font-size: 0.85rem;
        margin-bottom: 0.25rem;
    }
    .bar-name {
        color: var(--ink-soft) !important;
        font-weight: 500;
    }
    .bar-count {
        font-family: 'IBM Plex Mono', monospace;
        color: var(--slate) !important;
    }
    .bar-track {
        width: 100%;
        height: 6px;
        background: var(--line);
        border-radius: 3px;
        overflow: hidden;
    }
    .bar-fill {
        height: 100%;
        border-radius: 3px;
    }

    /* ---- Alerts ---- */
    .alert {
        border-left: 3px solid var(--line);
        background: var(--surface);
        border-radius: 4px;
        padding: 0.65rem 0.9rem;
        font-size: 0.9rem;
        line-height: 1.45;
        color: var(--ink) !important;
    }
    .alert-critical { border-left-color: var(--critical); }
    .alert-success  { border-left-color: var(--success); }
    .alert-muted    { border-left-color: var(--line); color: var(--slate) !important; }

    /* ---- Ticket meta strip ---- */
    .stat-row {
        display: flex;
        gap: 1.6rem;
        padding: 0.7rem 0;
        border-top: 1px solid var(--line);
        border-bottom: 1px solid var(--line);
        margin-bottom: 1rem;
    }
    .stat-item .stat-label {
        font-size: 0.75rem;
        color: var(--slate) !important;
        text-transform: none;
        margin-bottom: 0.1rem;
    }
    .stat-item .stat-value {
        font-size: 0.95rem;
        font-weight: 600;
        font-family: 'IBM Plex Mono', monospace;
        color: var(--ink) !important;
    }

    .field-label {
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--slate) !important;
        margin: 0.9rem 0 0.3rem 0;
    }

    /* ---- Sidebar ---- */
    section[data-testid="stSidebar"] {
        background: var(--surface);
        border-right: 1px solid var(--line);
    }
    .sys-item {
        display: flex;
        justify-content: space-between;
        font-size: 0.82rem;
        padding: 0.3rem 0;
        border-bottom: 1px solid var(--line);
    }
    .sys-key { color: var(--slate) !important; }
    .sys-val { font-family: 'IBM Plex Mono', monospace; color: var(--ink-soft) !important; }

    /* ---- Buttons ---- */
    .stButton > button {
        background: var(--ink);
        color: white !important;
        border: none;
        border-radius: 5px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .stButton > button p,
    .stButton > button div,
    .stButton > button span {
        color: white !important;
    }
    .stButton > button:hover,
    .stButton > button:hover p,
    .stButton > button:hover div,
    .stButton > button:hover span {
        color: white !important;
    }
    .stButton > button:hover {
        background: var(--ink-soft);
    }

    /* ---- Expander (ticket card) ---- */
    [data-testid="stExpander"] {
        border: 1px solid var(--line);
        border-radius: 6px;
        background: var(--surface);
        margin-bottom: 0.5rem;
    }

    [data-testid="stExpander"] summary {
        font-family: 'Inter', sans-serif;
    }

    hr { border-color: var(--line); }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Small render helpers
# ============================================================

def render_kpis(items):
    cards = "".join(
        f'<div class="kpi-card"><div class="kpi-value">{value}</div>'
        f'<div class="kpi-label">{label}</div></div>'
        for label, value in items
    )
    st.markdown(f'<div class="kpi-row">{cards}</div>', unsafe_allow_html=True)


def render_bar(name, count, total, color):
    pct = 0 if total == 0 else round(100 * count / total)
    st.markdown(
        f"""
        <div class="bar-row">
            <div class="bar-head">
                <span class="bar-name">{name}</span>
                <span class="bar-count">{count}</span>
            </div>
            <div class="bar-track">
                <div class="bar-fill" style="width:{pct}%; background:{color};"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_alert(text, kind="muted"):
    st.markdown(f'<div class="alert alert-{kind}">{text}</div>', unsafe_allow_html=True)


def render_stats(items):
    cells = "".join(
        f'<div class="stat-item"><div class="stat-label">{label}</div>'
        f'<div class="stat-value">{value}</div></div>'
        for label, value in items
    )
    st.markdown(f'<div class="stat-row">{cells}</div>', unsafe_allow_html=True)


# ============================================================
# Header
# ============================================================

st.markdown('<div class="app-title">🎫 Ticket Triage Agent</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-caption">LLM classification, deterministic guardrails, semantic '
    "duplicate detection, and human-in-the-loop review, in one queue.</div>",
    unsafe_allow_html=True,
)


# ============================================================
# Sidebar
# ============================================================

with st.sidebar:
    st.markdown('<div class="section-label">Submit a ticket</div>', unsafe_allow_html=True)

    subject = st.text_input("Subject", placeholder="e.g. I cannot access my account")
    body = st.text_area(
        "Message", height=160, placeholder="Describe the customer's problem..."
    )

    if st.button("Run triage", type="primary", use_container_width=True):
        if not subject.strip() or not body.strip():
            st.warning("Add a subject and a message before running triage.")
        else:
            try:
                with st.spinner("Classifying, checking for duplicates, drafting a reply..."):
                    data = api(
                        "/tickets",
                        "post",
                        json={"subject": subject, "body": body, "source": "streamlit"},
                    )
                st.success(f"Ticket #{data['id']} triaged.")
                st.rerun()
            except Exception as e:
                st.error(f"Triage failed: {e}")

    st.divider()
    st.markdown('<div class="section-label">System</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="sys-item"><span class="sys-key">Backend</span><span class="sys-val">FastAPI</span></div>
        <div class="sys-item"><span class="sys-key">LLM</span><span class="sys-val">Gemini</span></div>
        <div class="sys-item"><span class="sys-key">Embeddings</span><span class="sys-val">Sentence Transformers</span></div>
        <div class="sys-item"><span class="sys-key">Vector store</span><span class="sys-val">ChromaDB</span></div>
        <div class="sys-item"><span class="sys-key">Database</span><span class="sys-val">SQLite</span></div>

        """,
        unsafe_allow_html=True,
    )


# ============================================================
# Load backend data
# ============================================================

try:
    stats = api("/stats")
    tickets = api("/tickets")
except Exception as e:
    render_alert(
        f"Backend unavailable at <span class='mono'>{API}</span>. "
        f"Start it and reload this page.<br>{e}",
        "critical",
    )
    st.code("python -m uvicorn app.main:app --reload")
    st.stop()


# ============================================================
# KPI cards
# ============================================================

st.markdown('<div class="section-label">Overview</div>', unsafe_allow_html=True)

high_critical = stats["priorities"].get("high", 0) + stats["priorities"].get("critical", 0)
human_review = stats["statuses"].get("needs_human_review", 0)

render_kpis(
    [
        ("Total tickets", stats["total"]),
        ("Duplicates", stats["duplicates"]),
        ("High / critical", high_critical),
        ("Needs human review", human_review),
    ]
)


# ============================================================
# Analytics
# ============================================================

st.markdown('<div class="section-label">Ticket analytics</div>', unsafe_allow_html=True)

analytics_col1, analytics_col2 = st.columns(2)

with analytics_col1:
    st.markdown("**Categories**")
    categories = stats.get("categories", {})
    if categories:
        for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
            render_bar(category.replace("_", " ").title(), count, stats["total"], "#3A4150")
    else:
        render_alert("No category data yet.", "muted")

with analytics_col2:
    st.markdown("**Priorities**")
    priorities = stats.get("priorities", {})
    for priority in ["critical", "high", "medium", "low"]:
        count = priorities.get(priority, 0)
        render_bar(priority.title(), count, stats["total"], PRIORITY_COLORS[priority])

st.divider()


# ============================================================
# Filters
# ============================================================

st.markdown('<div class="section-label">Ticket inbox</div>', unsafe_allow_html=True)

filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

with filter_col1:
    category_options = ["All"] + sorted({(t.get("category") or "other") for t in tickets})
    selected_category = st.selectbox("Category", category_options)

with filter_col2:
    priority_options = ["All", "critical", "high", "medium", "low"]
    selected_priority = st.selectbox("Priority", priority_options)

with filter_col3:
    status_options = ["All"] + sorted({(t.get("status") or "unknown") for t in tickets})
    selected_status = st.selectbox("Status", status_options)

with filter_col4:
    search = st.text_input("Search", placeholder="Search subject or message...")


# ============================================================
# Apply filters
# ============================================================

filtered_tickets = tickets

if selected_category != "All":
    filtered_tickets = [t for t in filtered_tickets if (t.get("category") or "other") == selected_category]

if selected_priority != "All":
    filtered_tickets = [t for t in filtered_tickets if (t.get("priority") or "medium") == selected_priority]

if selected_status != "All":
    filtered_tickets = [t for t in filtered_tickets if (t.get("status") or "unknown") == selected_status]

if search.strip():
    search_text = search.lower()
    filtered_tickets = [
        t
        for t in filtered_tickets
        if search_text in (t.get("subject") or "").lower()
        or search_text in (t.get("body") or "").lower()
    ]

st.caption(f"Showing {len(filtered_tickets)} of {len(tickets)} tickets")


# ============================================================
# Ticket display
# ============================================================

if not filtered_tickets:
    render_alert(
        "No tickets match these filters. Clear a filter or submit a new ticket from the sidebar.",
        "muted",
    )
else:
    for ticket in filtered_tickets:
        priority = ticket.get("priority") or "medium"
        category = ticket.get("category") or "other"
        status = ticket.get("status") or "unknown"
        subject = ticket.get("subject") or "(no subject)"
        dot = PRIORITY_DOTS.get(priority, "⚪")

        title = (
        f"{dot}  #{ticket['id']}  ·  "
        f"{priority.title()}  ·  "
        f"{category.replace('_', ' ').title()}  ·  "
        f"{subject}"
)

        with st.expander(title):
            confidence = ticket.get("confidence")
            confidence_display = f"{confidence:.2f}" if confidence is not None else "N/A"

            render_stats(
                [
                    ("Priority", priority.title()),
                    ("Category", category.replace("_", " ").title()),
                    ("Confidence", confidence_display),
                    ("Status", status.replace("_", " ").title()),
                ]
            )

            st.markdown('<div class="field-label">Customer message</div>', unsafe_allow_html=True)
            st.write(ticket.get("body") or "(no message)")

            st.markdown('<div class="field-label">Triage analysis</div>', unsafe_allow_html=True)
            analysis1, analysis2 = st.columns(2)

            with analysis1:
                sentiment = ticket.get("sentiment") or "unknown"
                suggested_team = ticket.get("suggested_team") or "Unknown"
                st.write(f"**Sentiment:** {sentiment.title()}")
                st.write(f"**Suggested team:** {suggested_team}")

            with analysis2:
                if ticket.get("duplicate_of"):
                    render_alert(f"Likely duplicate of ticket #{ticket['duplicate_of']}", "critical")
                else:
                    render_alert("No likely duplicate detected.", "success")

            st.markdown('<div class="field-label">Draft reply</div>', unsafe_allow_html=True)
            render_alert(ticket.get("draft_reply") or "No draft reply available.", "muted")

            if status == "needs_human_review":
                st.markdown('<div class="field-label">Needs attention</div>', unsafe_allow_html=True)
                render_alert(
                    "This ticket needs human review. Triage confidence was below the "
                    "configured threshold, or the LLM was unavailable when it ran.",
                    "critical",
                )