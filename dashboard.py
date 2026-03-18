import streamlit as st
import json
import os
from datetime import datetime
import uuid
try:
    from github import Github
except ImportError:
    Github = None

# Configurazione Pagina
st.set_page_config(page_title="JEMP Campaign Dashboard", page_icon="🟡", layout="centered")

# Branding JEMP (Nero e Giallo #FFD100)
st.markdown("""
    <style>
    /* Sfondo nero */
    .stApp {
        background-color: #000000;
        color: #FFFFFF;
    }
    /* Stile testo input e forme */
    div[data-baseweb="input"] > div {
        background-color: #1a1a1a;
        color: white;
    }
    textarea {
        background-color: #1a1a1a !important;
        color: white !important;
    }
    /* Bottoni principali gialli */
    .stButton>button {
        background-color: #FFD100;
        color: #000000;
        font-weight: bold;
        border-radius: 8px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #e6bc00;
        color: #000000;
    }
    /* Forza testo globale al bianco */
    h1, h2, h3, p, label {
        color: #FFFFFF !important;
    }
    /* Card per la campagna */
    .campaign-card {
        background-color: #1a1a1a;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #FFD100;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

DATA_FILE = "active_campaigns.json"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO") # es. jemp-polimi/jemp-trend-bot

def load_campaigns():
    if GITHUB_TOKEN and GITHUB_REPO and Github:
        try:
            g = Github(GITHUB_TOKEN)
            repo = g.get_repo(GITHUB_REPO)
            content = repo.get_contents(DATA_FILE)
            return json.loads(content.decoded_content.decode('utf-8'))
        except Exception as e:
            st.warning(f"Errore lettura GitHub, fallback locale. {e}")
            pass

    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding='utf-8') as f:
        try:
            return json.load(f)
        except:
            return []

def save_campaigns(campaigns):
    content_str = json.dumps(campaigns, indent=4, ensure_ascii=False)
    
    # Salva sempre in remoto se configurato
    if GITHUB_TOKEN and GITHUB_REPO and Github:
        try:
            g = Github(GITHUB_TOKEN)
            repo = g.get_repo(GITHUB_REPO)
            try:
                file_info = repo.get_contents(DATA_FILE)
                repo.update_file(file_info.path, "Automazione: Dashboard update", content_str, file_info.sha)
            except:
                repo.create_file(DATA_FILE, "Automazione: Dashboard create", content_str)
        except Exception as e:
            st.error(f"Impossibile salvare su GitHub: {e}")
            
    # Salva sempre anche in locale a prescindere
    with open(DATA_FILE, "w", encoding='utf-8') as f:
        f.write(content_str)

# Header
col1, col2 = st.columns([1, 4])
with col1:
    logo_path = os.path.join("assets", "jemp_logo.png")
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)
with col2:
    st.title("JEMP Trend & Inspo")
    st.subheader("Gestione Campagne Attive")

st.divider()

# Nuovo Inserimento
st.markdown("### ➕ Aggiungi Nuova Campagna")
with st.form("new_campaign_form", clear_on_submit=True):
    title = st.text_input("Titolo Campagna")
    desc = st.text_area("Descrizione (Es. Obiettivo, Target, Topic da spingere)")
    colA, colB = st.columns(2)
    with colA:
        end_date = st.date_input("Data di Fine prevista")
    with colB:
        st.markdown("<br>", unsafe_allow_html=True) # Spacer per allineare al bottone
        submitted = st.form_submit_button("Crea Campagna")
    
    if submitted:
        if title.strip() == "":
            st.error("Il titolo non può essere vuoto!")
        else:
            campaigns = load_campaigns()
            new_camp = {
                "id": str(uuid.uuid4())[:8],
                "title": title,
                "description": desc,
                "end_date": end_date.strftime("%Y-%m-%d"),
                "status": "active"
            }
            campaigns.append(new_camp)
            save_campaigns(campaigns)
            st.success("Campagna aggiunta con successo!")
            st.rerun()

st.divider()

# Lista Campagne
st.markdown("### 📋 Campagne In Corso")
campaigns = load_campaigns()
active_campaigns = [c for c in campaigns if c.get("status") == "active"]

if not active_campaigns:
    st.info("Nessuna campagna attiva al momento.")
else:
    for c in active_campaigns:
        with st.container():
            st.markdown(f"""
            <div class="campaign-card">
                <h4 style="color: #FFD100 !important; margin-top: 0;">{c['title']}</h4>
                <p><strong>Scadenza:</strong> {c['end_date']}</p>
                <p>{c['description']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Pulsante per terminare la campagna
            if st.button(f"Termina Campagna '{c['title']}'", key=f"del_{c['id']}"):
                for idx, camp in enumerate(campaigns):
                    if camp['id'] == c['id']:
                        campaigns[idx]['status'] = "completed"
                save_campaigns(campaigns)
                st.rerun()

st.divider()

# Lista Campagne Archiviate (Terminate)
st.markdown("### 🗄️ Archivio Storico")
archived_campaigns = [c for c in campaigns if c.get("status") == "completed"]

if not archived_campaigns:
    st.info("Nessuna campagna in archivio.")
else:
    for c in archived_campaigns:
        with st.container():
            st.markdown(f"""
            <div class="campaign-card" style="border-left: 5px solid #555555; opacity: 0.7;">
                <h5 style="color: #999999 !important; margin-top: 0;"><del>{c['title']}</del></h5>
                <p style="font-size: 0.9em; color: #bbbbbb;"><strong>Scadenza originale:</strong> {c['end_date']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Pulsante per eliminare definitivamente
            if st.button(f"❌ Elimina definitivamente '{c['title']}'", key=f"perm_del_{c['id']}"):
                campaigns = [camp for camp in campaigns if camp['id'] != c['id']]
                save_campaigns(campaigns)
                st.rerun()
