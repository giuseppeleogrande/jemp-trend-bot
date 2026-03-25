import streamlit as st
import json
import os
import hmac
import uuid
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

try:
    from github import Github
except ImportError:
    Github = None

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="JEMP Copilot",
    page_icon="🟡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── ChatGPT-style premium dark UI with mobile responsiveness ───
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
    --bg-primary:   #212121;
    --bg-secondary: #171717;
    --bg-surface:   #2f2f2f;
    --bg-hover:     #3a3a3a;
    --border:       #333333;
    --border-light: #444444;
    --text-primary: #e8e8e8;
    --text-secondary: #9a9a9a;
    --text-muted:   #6b6b6b;
    --accent:       #f2b705;
    --accent-hover: #e0a800;
    --green:        #10a37f;
    --radius-sm:    8px;
    --radius-md:    12px;
    --radius-lg:    16px;
    --radius-xl:    24px;
    --transition:   all 0.2s cubic-bezier(.4,0,.2,1);
}

* {
    font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif !important;
    box-sizing: border-box;
}

/* ═══════════════════════════════ MAIN APP ═══════════════════════════════ */
.stApp {
    background: var(--bg-primary) !important;
    color: var(--text-primary) !important;
}

/* Center main content like ChatGPT */
.stMainBlockContainer {
    max-width: 820px !important;
    margin: 0 auto !important;
    padding: 1rem 1.5rem !important;
}

/* ═══════════════════════════════ SCROLLBAR ═══════════════════════════════ */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #444; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #555; }

/* ═══════════════════════════════ SIDEBAR ═══════════════════════════════ */
section[data-testid="stSidebar"] {
    background: var(--bg-secondary) !important;
    border-right: 1px solid var(--border) !important;
    width: 280px !important;
}
section[data-testid="stSidebar"] > div {
    background: transparent !important;
    padding-top: 0 !important;
}

.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 20px 16px 12px;
}
.sidebar-brand img {
    height: 28px;
    width: auto;
}
.sidebar-brand-text {
    font-size: 0.85rem;
    color: var(--text-secondary);
    font-weight: 400;
    letter-spacing: 0.02em;
}

.sidebar-section {
    font-size: 0.65rem;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    padding: 20px 8px 6px;
    margin: 0;
}

/* Sidebar buttons */
section[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    color: var(--text-primary) !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-size: 0.85rem !important;
    font-weight: 400 !important;
    padding: 8px 12px !important;
    text-align: left !important;
    transition: var(--transition) !important;
    height: auto !important;
    min-height: 38px !important;
    justify-content: flex-start !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: var(--bg-surface) !important;
}
section[data-testid="stSidebar"] .stButton > button:focus {
    box-shadow: none !important;
    outline: none !important;
}

/* Thread row: hide delete button until hover */
.thread-row {
    display: flex;
    align-items: center;
    gap: 2px;
    border-radius: var(--radius-sm);
    transition: var(--transition);
}
.thread-row:hover { background: rgba(255,255,255,0.03); }
.thread-row .del-btn { opacity: 0; transition: opacity 0.15s ease; }
.thread-row:hover .del-btn { opacity: 1; }

/* ═══════════════════════════════ HEADINGS ═══════════════════════════════ */
h1, h2, h3, h4, h5 {
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    letter-spacing: -0.01em !important;
}
h1 { font-size: 1.35rem !important; }
h2 { font-size: 1.2rem !important; }
h3 { font-size: 1.05rem !important; }

/* ═══════════════════════════════ BUTTONS ═══════════════════════════════ */
.stButton > button {
    background: var(--bg-surface) !important;
    color: var(--text-primary) !important;
    font-weight: 500 !important;
    border-radius: var(--radius-sm) !important;
    border: 1px solid var(--border) !important;
    box-shadow: none !important;
    transition: var(--transition) !important;
    font-size: 0.85rem !important;
    padding: 6px 16px !important;
}
.stButton > button:hover {
    background: var(--bg-hover) !important;
    border-color: var(--border-light) !important;
    box-shadow: none !important;
    transform: none !important;
}
.stButton > button:focus {
    box-shadow: none !important;
    outline: none !important;
}

/* Primary accent button */
.accent-btn > button {
    background: var(--accent) !important;
    color: #1a1a1a !important;
    border: none !important;
    font-weight: 600 !important;
    border-radius: var(--radius-sm) !important;
}
.accent-btn > button:hover {
    background: var(--accent-hover) !important;
    color: #1a1a1a !important;
}

/* ═══════════════════════════════ CHAT MESSAGES ═══════════════════════════ */
div[data-testid="stChatMessage"] {
    border: none !important;
    border-radius: 0 !important;
    padding: 20px 0 !important;
    margin-bottom: 0 !important;
    max-width: 100% !important;
    border-bottom: 1px solid rgba(255,255,255,0.04) !important;
}
div[data-testid="stChatMessage"]:last-of-type {
    border-bottom: none !important;
}
/* User messages */
div[data-testid="stChatMessage"][data-role="user"] {
    background: transparent !important;
}
/* Assistant messages */
div[data-testid="stChatMessage"][data-role="assistant"] {
    background: rgba(255,255,255,0.02) !important;
}

/* Chat message text */
div[data-testid="stChatMessage"] p {
    font-size: 0.92rem !important;
    line-height: 1.7 !important;
}

/* ═══════════════════════════════ CHAT INPUT ═══════════════════════════════ */
div[data-testid="stChatInput"] {
    background: var(--bg-primary) !important;
    border-top: none !important;
    padding: 8px 0 16px !important;
}
div[data-testid="stChatInput"] textarea {
    background: var(--bg-surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    border-radius: var(--radius-xl) !important;
    font-size: 0.92rem !important;
    padding: 12px 20px !important;
    min-height: 48px !important;
    transition: border-color 0.2s ease !important;
}
div[data-testid="stChatInput"] textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 1px var(--accent) !important;
}
/* Send button */
div[data-testid="stChatInput"] button {
    background: var(--accent) !important;
    color: #1a1a1a !important;
    border: none !important;
    border-radius: 50% !important;
}
div[data-testid="stChatInput"] button:hover {
    background: var(--accent-hover) !important;
}

/* ═══════════════════════════════ INPUTS ═══════════════════════════════ */
div[data-baseweb="input"] > div {
    background: var(--bg-surface) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    transition: border-color 0.2s ease !important;
}
div[data-baseweb="input"] > div:focus-within {
    border-color: var(--accent) !important;
}
textarea {
    background: var(--bg-surface) !important;
    color: var(--text-primary) !important;
    border-radius: var(--radius-md) !important;
}
input { color: var(--text-primary) !important; }

/* ═══════════════════════════════ SELECTBOX ═══════════════════════════════ */
div[data-baseweb="select"] > div {
    background: var(--bg-surface) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    min-height: 42px !important;
    transition: border-color 0.2s ease !important;
}
div[data-baseweb="select"] > div:focus-within {
    border-color: var(--accent) !important;
}
/* Dropdown menu */
ul[data-testid="stSelectboxVirtualDropdown"],
div[data-baseweb="popover"] > div {
    background: var(--bg-surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
}
li[role="option"] {
    color: var(--text-primary) !important;
}
li[role="option"]:hover {
    background: var(--bg-hover) !important;
}

/* ═══════════════════════════════ FORM LABELS ═══════════════════════════════ */
.stSelectbox label, .stTextInput label, .stTextArea label {
    font-weight: 500 !important;
    color: var(--text-secondary) !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}

/* ═══════════════════════════════ CAMPAIGN CARD ═══════════════════════════════ */
.campaign-card {
    background: var(--bg-surface);
    padding: 18px 22px;
    border-radius: var(--radius-md);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    margin-bottom: 14px;
    transition: var(--transition);
}
.campaign-card:hover {
    border-color: var(--border-light);
    background: var(--bg-hover);
}
.campaign-card h4 {
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    margin: 0 0 8px 0 !important;
    font-size: 0.95rem !important;
}
.campaign-card p {
    color: var(--text-secondary) !important;
    margin: 4px 0 !important;
    font-size: 0.85rem !important;
    line-height: 1.5 !important;
}

/* ═══════════════════════════════ DIVIDERS ═══════════════════════════════ */
hr {
    border-color: rgba(255,255,255,0.06) !important;
    margin: 16px 0 !important;
}

/* ═══════════════════════════════ MISC ═══════════════════════════════ */
.stAlert { border-radius: var(--radius-sm) !important; background: var(--bg-surface) !important; }
.stExpander {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    background: transparent !important;
}
.stExpander summary {
    color: var(--text-primary) !important;
    font-weight: 500 !important;
}
p, li { color: var(--text-primary) !important; }
span { color: inherit !important; }

/* ═══════════════════════════════ FORM SUBMIT ═══════════════════════════════ */
.stFormSubmitButton > button {
    background: var(--accent) !important;
    color: #1a1a1a !important;
    border: none !important;
    font-weight: 600 !important;
    border-radius: var(--radius-sm) !important;
    padding: 8px 24px !important;
    transition: var(--transition) !important;
}
.stFormSubmitButton > button:hover {
    background: var(--accent-hover) !important;
}

/* ═══════════════════════════════ WELCOME SCREEN ═══════════════════════════════ */
.welcome-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 80px 24px 40px;
    text-align: center;
}
.welcome-logo {
    width: 56px;
    height: 56px;
    background: var(--accent);
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.6rem;
    margin-bottom: 20px;
    box-shadow: 0 4px 24px rgba(242,183,5,0.15);
}
.welcome-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 8px;
}
.welcome-sub {
    font-size: 0.9rem;
    color: var(--text-secondary);
    max-width: 460px;
    line-height: 1.6;
    margin-bottom: 32px;
}
.suggestion-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: center;
    max-width: 520px;
}
.chip {
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-xl);
    padding: 8px 18px;
    font-size: 0.8rem;
    color: var(--text-secondary);
    transition: var(--transition);
    cursor: default;
}
.chip:hover {
    border-color: var(--accent);
    color: var(--text-primary);
    background: var(--bg-hover);
}

/* ═══════════════════════════════ SELECTORS ROW ═══════════════════════════════ */
.selectors-row {
    display: flex;
    gap: 12px;
    margin-bottom: 4px;
}

/* ═══════════════════════════════ LOGIN ═══════════════════════════════ */
.login-wrap {
    max-width: 380px;
    margin: 100px auto 0;
    padding: 48px 40px 40px;
    background: var(--bg-surface);
    border-radius: var(--radius-lg);
    border: 1px solid var(--border);
    text-align: center;
    box-shadow: 0 8px 40px rgba(0,0,0,0.3);
}
.login-logo-img {
    height: 36px;
    margin-bottom: 20px;
}
.login-wrap h2 {
    font-weight: 700 !important;
    color: var(--text-primary) !important;
    font-size: 1.5rem !important;
    margin-bottom: 6px !important;
    letter-spacing: -0.02em !important;
}
.login-wrap p {
    color: var(--text-secondary) !important;
    font-size: 0.88rem !important;
    margin-bottom: 0 !important;
    line-height: 1.5 !important;
}

/* ═══════════════════════════════ SIDEBAR FOOTER ═══════════════════════════════ */
.sidebar-footer {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 280px;
    padding: 12px 16px;
    text-align: center;
    font-size: 0.68rem;
    color: var(--text-muted);
    background: linear-gradient(transparent, var(--bg-secondary) 40%);
    pointer-events: none;
    letter-spacing: 0.02em;
}

/* ═══════════════════════════════ MOBILE RESPONSIVE ═══════════════════════════════ */
@media (max-width: 768px) {
    .stMainBlockContainer {
        max-width: 100% !important;
        padding: 0.5rem 1rem !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        width: 260px !important;
    }

    /* Larger touch targets */
    .stButton > button {
        min-height: 44px !important;
        font-size: 0.88rem !important;
    }
    section[data-testid="stSidebar"] .stButton > button {
        min-height: 44px !important;
        padding: 10px 12px !important;
    }

    /* Welcome */
    .welcome-container {
        padding: 48px 16px 24px;
    }
    .welcome-title { font-size: 1.25rem; }
    .welcome-sub { font-size: 0.85rem; }
    .suggestion-chips { gap: 6px; }
    .chip { padding: 7px 14px; font-size: 0.78rem; }

    /* Chat messages */
    div[data-testid="stChatMessage"] {
        padding: 14px 0 !important;
    }
    div[data-testid="stChatMessage"] p {
        font-size: 0.9rem !important;
    }

    /* Chat input */
    div[data-testid="stChatInput"] textarea {
        font-size: 16px !important; /* prevents iOS zoom */
        border-radius: var(--radius-lg) !important;
        padding: 10px 16px !important;
    }

    /* Campaign cards */
    .campaign-card {
        padding: 14px 16px;
    }

    /* Login */
    .login-wrap {
        margin: 60px 16px 0;
        padding: 36px 24px 32px;
    }

    /* Sidebar footer */
    .sidebar-footer {
        width: 260px;
    }

    /* Headings */
    h1 { font-size: 1.15rem !important; }
    h2 { font-size: 1.05rem !important; }
}

@media (max-width: 480px) {
    .stMainBlockContainer {
        padding: 0.25rem 0.75rem !important;
    }
    .welcome-container {
        padding: 32px 12px 16px;
    }
    .chip { padding: 6px 12px; font-size: 0.75rem; }
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────────────────────────────────────
def check_password():
    if st.session_state.get("password_correct", False):
        return True

    import base64, pathlib
    _logo_path = pathlib.Path("assets/jemp_logo.png")
    if _logo_path.exists():
        _logo_b64 = base64.b64encode(_logo_path.read_bytes()).decode()
        _logo_tag = f'<img src="data:image/png;base64,{_logo_b64}" class="login-logo-img" alt="JEMP">'
    else:
        _logo_tag = '<div style="font-size:2rem;margin-bottom:14px;">✦</div>'

    st.markdown(f"""
    <div class="login-wrap">
      {_logo_tag}
      <h2>JEMP Copilot</h2>
      <p>Area riservata JEMPer.<br>Inserisci la password per accedere.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        pwd = st.text_input("Password", type="password",
                            label_visibility="collapsed", placeholder="Password...")
        submitted = st.form_submit_button("Accedi", use_container_width=True)

    if submitted:
        expected = os.getenv("APP_PASSWORD") or ""
        if not expected:
            try: expected = st.secrets.get("APP_PASSWORD", "SuperJEMP2026!")
            except: expected = "SuperJEMP2026!"
        if hmac.compare_digest(pwd, expected):
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("❌ Password errata.")
    return False

if not check_password():
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# DATA LAYER (GitHub or local)
# ─────────────────────────────────────────────────────────────────────────────
CAMPAIGNS_FILE = "active_campaigns.json"
THREADS_FILE = "chat_threads.json"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")

def _gh_repo():
    if GITHUB_TOKEN and GITHUB_REPO and Github:
        return Github(GITHUB_TOKEN).get_repo(GITHUB_REPO)
    return None

def _load_json(filename, default):
    repo = _gh_repo()
    if repo:
        try:
            content = repo.get_contents(filename)
            return json.loads(content.decoded_content.decode("utf-8"))
        except Exception:
            pass
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return default

def _save_json(filename, data):
    content_str = json.dumps(data, indent=2, ensure_ascii=False)
    repo = _gh_repo()
    if repo:
        try:
            try:
                fi = repo.get_contents(filename)
                repo.update_file(fi.path, f"Copilot: update {filename}", content_str, fi.sha)
            except Exception:
                repo.create_file(filename, f"Copilot: create {filename}", content_str)
        except Exception as e:
            st.error(f"Impossibile salvare su GitHub: {e}")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content_str)

def load_campaigns():   return _load_json(CAMPAIGNS_FILE, [])
def save_campaigns(d):  _save_json(CAMPAIGNS_FILE, d)
def load_threads():     return _load_json(THREADS_FILE, [])
def save_threads(d):    _save_json(THREADS_FILE, d)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state["page"] = "chat_new"      # "dashboard" | "chat_new" | "chat_<id>"
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = []
if "active_thread_id" not in st.session_state:
    st.session_state["active_thread_id"] = None

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    # ── Brand header with logo ──
    import base64, pathlib
    _logo_path = pathlib.Path("assets/jemp_logo.png")
    if _logo_path.exists():
        _logo_b64 = base64.b64encode(_logo_path.read_bytes()).decode()
        st.markdown(f"""
        <div class="sidebar-brand">
          <img src="data:image/png;base64,{_logo_b64}" style="height:26px;width:auto;">
          <span class="sidebar-brand-text">Copilot</span>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div class="sidebar-brand"><span style="color:#f2b705;font-weight:800;font-size:1.2rem;">JEMP</span><span class="sidebar-brand-text">Copilot</span></div>', unsafe_allow_html=True)

    st.divider()

    # ── Primary navigation ──
    if st.button("✏️  Nuova Chat", use_container_width=True):
        st.session_state["page"] = "chat_new"
        st.session_state["chat_messages"] = []
        st.session_state["active_thread_id"] = None
        st.rerun()

    if st.button("📊  Dashboard Campagne", use_container_width=True):
        st.session_state["page"] = "dashboard"
        st.rerun()

    # ── Thread history ──
    threads = load_threads()
    if threads:
        st.markdown('<div class="sidebar-section">Recenti</div>', unsafe_allow_html=True)
        for t in reversed(threads[-20:]):
            label = t.get("title", "Chat senza titolo")
            label_short = label[:30] + "…" if len(label) > 31 else label
            col_t, col_d = st.columns([5, 1])
            with col_t:
                if st.button(label_short, key=f"thread_{t['id']}", use_container_width=True):
                    st.session_state["page"] = f"chat_{t['id']}"
                    st.session_state["active_thread_id"] = t["id"]
                    st.session_state["chat_messages"] = t.get("messages", [])
                    if t.get("camp_title"):
                        st.session_state["thread_camp"] = t["camp_title"]
                    if t.get("time_label"):
                        st.session_state["thread_time"] = t["time_label"]
                    st.rerun()
            with col_d:
                if st.button("✕", key=f"del_thread_{t['id']}", help="Elimina thread"):
                    updated = [x for x in threads if x["id"] != t["id"]]
                    save_threads(updated)
                    if st.session_state.get("active_thread_id") == t["id"]:
                        st.session_state["page"] = "chat_new"
                        st.session_state["chat_messages"] = []
                        st.session_state["active_thread_id"] = None
                    st.rerun()

    # ── Footer ──
    st.markdown('<div class="sidebar-footer">JEMP Copilot · AI Assistant</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD CAMPAGNE PAGE
# ─────────────────────────────────────────────────────────────────────────────
def render_dashboard():
    st.markdown("""
    <div style="padding:8px 0 4px;">
      <h2 style="margin:0 0 4px;">📊 Dashboard Campagne</h2>
      <p style="color:var(--text-secondary);font-size:0.88rem;margin:0;">Gestisci i brief delle campagne attive. L'AI li userà come contesto nelle chat.</p>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    # Form nuova campagna
    st.markdown("### ➕ Aggiungi Nuova Campagna")
    with st.form("new_campaign_form", clear_on_submit=True):
        title = st.text_input("Titolo Campagna *", placeholder="Es. Recruiting Primaverile IT")
        desc = st.text_area("Descrizione *", placeholder="Di cosa parla questa campagna?")
        st.markdown("**Contesto per l'AI (facoltativo):**")
        colA, colB = st.columns(2)
        with colA:
            target = st.text_input("Target Audience", placeholder="Es. Studenti Magistrali Polimi")
            goal = st.text_input("Obiettivo Pratico", placeholder="Es. Portare click al modulo")
        with colB:
            past = st.text_area("Cosa ha funzionato in passato?", placeholder="Es. Post sui 6 Plugin Figma")
            end_date = st.date_input("Scadenza prevista *")
        if st.form_submit_button("Crea Campagna"):
            if not title.strip():
                st.error("Il titolo non può essere vuoto!")
            else:
                camps = load_campaigns()
                camps.append({
                    "id": str(uuid.uuid4())[:8], "title": title,
                    "description": desc, "target_audience": target,
                    "jemper_goal": goal, "past_content": past,
                    "end_date": end_date.strftime("%Y-%m-%d"), "status": "active"
                })
                save_campaigns(camps)
                st.success("✅ Campagna aggiunta!")
                st.rerun()

    st.divider()
    camps = load_campaigns()

    # Attive
    st.markdown("### 📋 Campagne In Corso")
    active = [c for c in camps if c.get("status") == "active"]
    if not active:
        st.info("Nessuna campagna attiva.")
    for c in active:
        st.markdown(f"""<div class="campaign-card">
            <h4>{c['title']}</h4>
            <p><strong>Scadenza:</strong> {c['end_date']}</p>
            <p>{c.get('description','')}</p>
        </div>""", unsafe_allow_html=True)
        if st.button(f"✅ Termina '{c['title']}'", key=f"end_{c['id']}"):
            for idx, x in enumerate(camps):
                if x["id"] == c["id"]: camps[idx]["status"] = "completed"
            save_campaigns(camps); st.rerun()

    st.divider()

    # Archivio
    archived = [c for c in camps if c.get("status") == "completed"]
    with st.expander(f"🗄️ Archivio Storico ({len(archived)})"):
        if not archived:
            st.info("Nessuna campagna archiviata.")
        for c in archived:
            st.markdown(f"""<div class="campaign-card" style="border-left-color:#36373c;opacity:.7;">
                <h4 style="color:#7e7d81!important;"><del>{c['title']}</del></h4>
                <p>Scadenza originale: {c['end_date']}</p>
            </div>""", unsafe_allow_html=True)
            if st.button(f"🗑 Elimina definitivamente", key=f"del_{c['id']}"):
                camps = [x for x in camps if x["id"] != c["id"]]
                save_campaigns(camps); st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# CHAT PAGE
# ─────────────────────────────────────────────────────────────────────────────
def render_chat():
    from services.searcher import get_weekly_trends, TIMELIMIT_MAP
    from services.llm_agent import chat_with_jemp_bot

    camps = load_campaigns()
    active_camps = [c for c in camps if c.get("status") == "active"]
    camp_options = ["— Nessuna campagna specifica —"] + [c["title"] for c in active_camps]
    time_options = list(TIMELIMIT_MAP.keys())

    # ---- Header ----
    st.markdown("""
    <div style="padding:8px 0 2px;display:flex;align-items:baseline;gap:10px;">
      <h2 style="margin:0;">JEMP Copilot</h2>
      <span style="font-size:0.78rem;color:var(--text-muted);font-weight:400;">AI Marketing Assistant</span>
    </div>
    """, unsafe_allow_html=True)

    # Calcola l'index corretto per i selectbox (ripristino da thread salvato)
    saved_camp   = st.session_state.get("thread_camp", None)
    saved_time   = st.session_state.get("thread_time", None)
    camp_idx  = camp_options.index(saved_camp) if saved_camp in camp_options else 0
    time_idx  = time_options.index(saved_time) if saved_time in time_options else 2

    sel_col1, sel_col2 = st.columns(2)
    with sel_col1:
        selected_camp_title = st.selectbox(
            "🎯 Campagna di contesto",
            camp_options,
            index=camp_idx,
            key="chat_camp_select",
            help="L'AI tratterà questa campagna come contesto invisibile."
        )
    with sel_col2:
        selected_time_label = st.selectbox(
            "🌐 Web Scraping",
            time_options,
            index=time_idx,
            key="chat_time_select",
            help="Vuoi che l'AI ricerca le notizie più recenti prima di rispondere?"
        )

    # Reset dei valori ripristino dopo il primo render (evita override permanente)
    st.session_state.pop("thread_camp", None)
    st.session_state.pop("thread_time", None)

    selected_campaign = next((c for c in active_camps if c["title"] == selected_camp_title), None)
    timelimit = TIMELIMIT_MAP[selected_time_label]

    st.divider()

    # ---- Messages ----
    messages = st.session_state.get("chat_messages", [])

    if not messages:
        st.markdown("""
        <div class="welcome-container">
          <div class="welcome-logo">✦</div>
          <div class="welcome-title">Ciao JEMPer!</div>
          <div class="welcome-sub">
            Dimmi come posso aiutarti oggi. Posso creare contenuti, analizzare trend,
            scrivere copy per LinkedIn e molto altro.
          </div>
          <div class="suggestion-chips">
            <div class="chip">💡 Idee per post LinkedIn</div>
            <div class="chip">📈 Analisi trend settimana</div>
            <div class="chip">✍️ Copy per campagna</div>
            <div class="chip">🎯 Strategia recruiting</div>
            <div class="chip">🔍 Trend del settore</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    for msg in messages:
        with st.chat_message(msg["role"], avatar="🟡" if msg["role"] == "assistant" else "👤"):
            st.markdown(msg["content"])

    # ---- Input ----
    prompt = st.chat_input("Chiedi qualcosa a JEMP Copilot...")

    if prompt:
        messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # Trend: cache per sessione (fetch solo la prima volta o se cambia il timeframe)
        cache_key = f"trends_{timelimit}"
        if timelimit is None:
            trends = []
        elif cache_key not in st.session_state:
            with st.spinner(f"🌐 Ricerca web in corso ({selected_time_label.lower()})..."):
                try:
                    trends = get_weekly_trends(timelimit=timelimit)
                    st.session_state[cache_key] = trends
                except Exception as e:
                    st.warning(f"Ricerca web non riuscita: {e}. Continuo senza dati web.")
                    trends = []
        else:
            trends = st.session_state[cache_key]

        # AI response
        with st.chat_message("assistant", avatar="🟡"):
            with st.spinner("JEMP Copilot sta pensando…"):
                try:
                    reply = chat_with_jemp_bot(messages, campaign=selected_campaign, trends=trends)
                except ValueError as ve:
                    reply = f"⚠️ **Errore di configurazione:** {ve}"
                except Exception as e:
                    reply = f"❌ **Errore:** {e}"
            st.markdown(reply)

        messages.append({"role": "assistant", "content": reply})
        st.session_state["chat_messages"] = messages

        # Salva/aggiorna thread (con contesto campagna e timing)
        _save_thread(messages, selected_camp_title, selected_time_label)
        st.rerun()

def _save_thread(messages, camp_title, time_label="Ultima settimana"):
    """Salva o aggiorna il thread corrente — include campagna e timelimit."""
    threads = load_threads()
    tid = st.session_state.get("active_thread_id")

    # Genera titolo automatico dal primo messaggio utente
    first_user = next((m["content"] for m in messages if m["role"] == "user"), "Chat")
    auto_title = first_user[:50]
    if camp_title and "Nessuna" not in camp_title:
        auto_title = f"[{camp_title}] {auto_title}"

    if tid:
        for t in threads:
            if t["id"] == tid:
                t["messages"]   = messages
                t["camp_title"] = camp_title
                t["time_label"] = time_label
                t["updated_at"] = datetime.now().isoformat()
                break
    else:
        tid = str(uuid.uuid4())[:8]
        st.session_state["active_thread_id"] = tid
        threads.append({
            "id": tid, "title": auto_title,
            "messages": messages,
            "camp_title": camp_title,
            "time_label": time_label,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        })

    save_threads(threads)

# ─────────────────────────────────────────────────────────────────────────────
# ROUTER
# ─────────────────────────────────────────────────────────────────────────────
page = st.session_state.get("page", "chat_new")

if page == "dashboard":
    render_dashboard()
else:
    render_chat()
