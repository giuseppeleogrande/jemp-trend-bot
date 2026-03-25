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

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS (Brand Book 2024: #f28e00 yellow, Barlow, Source Serif)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;600;700;800&family=Source+Serif+4:wght@400;600&display=swap');

/* Base */
.stApp { background-color: #0a0a0a; color: #dbdcdb; font-family: 'Source Serif 4', Georgia, serif; }
section[data-testid="stSidebar"] { background-color: #111111 !important; border-right: 1px solid #222; }

/* Headings */
h1,h2,h3,h4,h5 { font-family:'Barlow',sans-serif !important; font-weight:800 !important; color:#fff !important; }
h1 { color:#f28e00 !important; font-size:1.6rem !important; }

/* Sidebar items */
.sidebar-section { font-family:'Barlow',sans-serif; font-size:0.72rem; font-weight:700;
  color:#58575c; text-transform:uppercase; letter-spacing:1px; padding:16px 8px 4px; }
.thread-btn { display:block; width:100%; text-align:left; background:none; border:none;
  color:#aaa9ac; font-family:'Source Serif 4',Georgia,serif; font-size:0.88rem;
  padding:8px 12px; cursor:pointer; border-radius:6px; transition:background 0.15s; }
.thread-btn:hover { background:#1e1e1e; color:#fff; }
.thread-btn.active { background:#1e1e1e; color:#f28e00 !important; border-left:3px solid #f28e00; }

/* Buttons */
.stButton>button { background:#f28e00 !important; color:#000 !important;
  font-family:'Barlow',sans-serif !important; font-weight:700 !important;
  border-radius:6px !important; border:none !important; box-shadow:none !important; }
.stButton>button:hover { background:#f7aa01 !important; }
button[kind="secondary"] { background:#191b20 !important; color:#dbdcdb !important; }

/* Chat messages */
div[data-testid="stChatMessage"] { border-radius:8px; }
div[data-testid="stChatMessage"][data-role="user"] { background:#1a1a0a; }
div[data-testid="stChatMessage"][data-role="assistant"] { background:#111518; }

/* Inputs */
div[data-baseweb="input"]>div, textarea {
  background:#191b20 !important; color:#dbdcdb !important; border:1px solid #36373c !important; }
input { font-family:'Source Serif 4',Georgia,serif !important; }

/* Dividers */
hr { border-color:#222 !important; }

/* Campaign card */
.campaign-card { background:#191b20; padding:18px 22px; border-radius:8px;
  border-left:4px solid #f28e00; margin-bottom:14px; }
.campaign-card h4 { color:#f28e00 !important; font-family:'Barlow',sans-serif !important;
  font-weight:700 !important; margin-top:0; }
.campaign-card p { color:#aaa9ac !important; margin:4px 0; }

/* Form */
.stSelectbox label, .stTextInput label, .stTextArea label {
  font-family:'Barlow',sans-serif !important; font-weight:600 !important; color:#fff !important; }

/* Chat input */
div[data-testid="stChatInput"] textarea { background:#191b20 !important; }

/* Selectbox */
div[data-baseweb="select"] div { background:#191b20 !important; color:#dbdcdb !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────────────────────────────────────
def check_password():
    if st.session_state.get("password_correct", False):
        return True

    st.markdown("""
    <style>
    .stApp { background:#000; }
    .login-wrap { max-width:400px; margin:80px auto 0; padding:40px 36px;
      background:#191b20; border-radius:12px; border-top:4px solid #f28e00; text-align:center; }
    .login-wrap h2 { font-family:'Barlow',sans-serif; font-weight:800;
      color:#f28e00 !important; font-size:2rem; margin-bottom:6px; }
    .login-wrap p { color:#7e7d81 !important; font-size:0.95rem; margin-bottom:20px; }
    </style>
    <div class="login-wrap">
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
    st.markdown("""
    <div style="padding:16px 8px 8px;display:flex;align-items:center;gap:10px;">
      <span style="font-family:'Barlow',sans-serif;font-size:1.4rem;font-weight:800;color:#f28e00;">JEMP</span>
      <span style="font-family:'Source Serif 4',serif;color:#7e7d81;font-size:0.9rem;">Copilot</span>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # New Chat button
    if st.button("💬 Nuova Chat", use_container_width=True):
        st.session_state["page"] = "chat_new"
        st.session_state["chat_messages"] = []
        st.session_state["active_thread_id"] = None
        st.rerun()

    # Dashboard Campagne button
    st.markdown("")
    if st.button("📊 Dashboard Campagne", use_container_width=True):
        st.session_state["page"] = "dashboard"
        st.rerun()

    # Thread history
    threads = load_threads()
    if threads:
        st.markdown('<div class="sidebar-section">Thread Recenti</div>', unsafe_allow_html=True)
        for t in reversed(threads[-20:]):
            label = t.get("title", "Chat senza titolo")
            label_short = label[:28] + "…" if len(label) > 29 else label
            col_t, col_d = st.columns([5, 1])
            with col_t:
                if st.button(f"🧵 {label_short}", key=f"thread_{t['id']}", use_container_width=True):
                    st.session_state["page"] = f"chat_{t['id']}"
                    st.session_state["active_thread_id"] = t["id"]
                    st.session_state["chat_messages"] = t.get("messages", [])
                    if t.get("camp_title"):
                        st.session_state["thread_camp"] = t["camp_title"]
                    if t.get("time_label"):
                        st.session_state["thread_time"] = t["time_label"]
                    st.rerun()
            with col_d:
                if st.button("🗑", key=f"del_thread_{t['id']}", help="Elimina thread"):
                    updated = [x for x in threads if x["id"] != t["id"]]
                    save_threads(updated)
                    # Se era il thread attivo, torna a nuova chat
                    if st.session_state.get("active_thread_id") == t["id"]:
                        st.session_state["page"] = "chat_new"
                        st.session_state["chat_messages"] = []
                        st.session_state["active_thread_id"] = None
                    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD CAMPAGNE PAGE
# ─────────────────────────────────────────────────────────────────────────────
def render_dashboard():
    st.markdown("## 📊 Dashboard Campagne")
    st.markdown("Gestisci i brief delle campagne attive. L'AI li userà come contesto nelle chat.")
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

    # ---- Header selectors ----
    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown("## 💬 JEMP Copilot")
    with col2:
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

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
        <div style="text-align:center;padding:60px 20px;color:#36373c;">
          <div style="font-size:3rem;">🟡</div>
          <div style="font-family:'Barlow',sans-serif;font-size:1.2rem;font-weight:700;color:#58575c;margin-top:12px;">
            Ciao JEMPer! Dimmi come posso aiutarti oggi.
          </div>
          <div style="font-size:0.9rem;color:#36373c;margin-top:8px;">
            Puoi chiedermi idee per post, analisi di trend, copy da LinkedIn, strategie per le campagne attive e molto altro.
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
