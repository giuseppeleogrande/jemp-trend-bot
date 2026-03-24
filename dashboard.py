import streamlit as st
import json
import os
from datetime import datetime
import uuid
import hmac
from dotenv import load_dotenv

# Carica variabili da .env PRIMA di qualsiasi os.getenv()
load_dotenv()

try:
    from github import Github
except ImportError:
    Github = None

# Configurazione Pagina
st.set_page_config(page_title="JEMP Campaign Dashboard", page_icon="🟡", layout="centered")

def check_password():
    """Restituisce True se l'utente ha inserito la password corretta."""
    def password_entered():
        # Prende la password dal file .env (in locale) o dai Secrets (in Cloud)
        expected_password = os.getenv("APP_PASSWORD")
        if not expected_password:
            try:
                expected_password = st.secrets.get("APP_PASSWORD", "SuperJEMP2026!")
            except Exception:
                expected_password = "SuperJEMP2026!"
                
        # Usa hmac per resistere agli attacchi di temporizzazione
        if hmac.compare_digest(st.session_state["password"], expected_password):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Pulisce la memoria
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    # Schermata di Login
    st.markdown("## 🔐 Area Riservata JEMP")
    st.markdown("Questa dashboard esegue script di intelligenza artificiale aziendali. Inserisci la master password per proseguire.")
    st.text_input(
        "Password di Accesso", 
        type="password", 
        on_change=password_entered, 
        key="password"
    )
    if "password_correct" in st.session_state:
        st.error("❌ Password errata. Riprova.")
    return False

if not check_password():
    st.stop()  # Ferma totalmente l'esecuzione se non autenticato

# --- INIZIO APP VERA E PROPRIA ---

# Branding JEMP (Brand Book 2024 - Palette Ufficiale)
# Giallo: #f28e00, Arancio (accenti): #f28e00, Nero: #000000
# Grigi: #191b20, #36373c, #58575c, #7e7d81, #aaa9ac, #dbdcdb
# Font: Barlow (headings), Source Serif Pro (body)
st.markdown("""
    <style>
    /* === GOOGLE FONTS === */
    @import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;600;700;800&family=Source+Serif+4:wght@400;600&display=swap');

    /* === SFONDO E TESTO === */
    .stApp {
        background-color: #000000;
        color: #dbdcdb;
        font-family: 'Source Serif 4', 'Source Serif Pro', Georgia, serif;
    }

    /* === TIPOGRAFIA (Barlow per titoli) === */
    h1, h2, h3, h4, h5 {
        font-family: 'Barlow', sans-serif !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        letter-spacing: -0.5px;
    }
    h1 { color: #f28e00 !important; }
    p, label, span, li {
        font-family: 'Source Serif 4', Georgia, serif !important;
        color: #dbdcdb !important;
    }

    /* === INPUT E FORM === */
    div[data-baseweb="input"] > div {
        background-color: #191b20;
        color: #dbdcdb;
        border: 1px solid #36373c;
        border-radius: 6px;
    }
    textarea {
        background-color: #191b20 !important;
        color: #dbdcdb !important;
        border: 1px solid #36373c !important;
        border-radius: 6px !important;
        font-family: 'Source Serif 4', Georgia, serif !important;
    }
    input {
        font-family: 'Source Serif 4', Georgia, serif !important;
    }
    
    /* === BOTTONI GIALLI (Flat, no shadow) === */
    .stButton>button {
        background-color: #f28e00;
        color: #000000;
        font-family: 'Barlow', sans-serif;
        font-weight: 700;
        border-radius: 6px;
        border: none;
        box-shadow: none;
        transition: background-color 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #f7aa01;
        color: #000000;
        box-shadow: none;
    }
    .stButton>button:active {
        background-color: #f49c02;
        color: #000000;
    }

    /* === CARD CAMPAGNE === */
    .campaign-card {
        background-color: #191b20;
        padding: 20px 24px;
        border-radius: 8px;
        border-left: 4px solid #f28e00;
        margin-bottom: 16px;
    }
    .campaign-card h4 {
        color: #f28e00 !important;
        margin-top: 0;
        font-family: 'Barlow', sans-serif !important;
        font-weight: 700 !important;
    }
    .campaign-card p {
        color: #aaa9ac !important;
    }
    
    /* === DIVIDER === */
    hr {
        border-color: #36373c !important;
    }

    /* === SPINNER & MESSAGGI === */
    .stSpinner > div {
        border-top-color: #f28e00 !important;
    }
    .stAlert {
        border-radius: 6px;
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
    title = st.text_input("Titolo Campagna *", placeholder="Es. Recruiting Primaverile IT")
    desc = st.text_area("Descrizione Generale *", placeholder="Di cosa parla questa campagna in 2 righe?")
    
    st.markdown("**(Opzionale) Aggiungi super-contesto per addestrare l'AI:**")
    colA, colB = st.columns(2)
    with colA:
        target_audience = st.text_input("Target Audience", placeholder="Es. Studenti Magistrali Polimi")
        jemper_goal = st.text_input("Obiettivo Pratico del JEMPer", placeholder="Es. Portare click al modulo")
    with colB:
        past_content = st.text_area("Cosa ha funzionato in passato?", placeholder="Es. 'Post sui 6 plugin Figma utilissimi'")
        end_date = st.date_input("Data di Fine prevista *")
        
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
                "target_audience": target_audience,
                "jemper_goal": jemper_goal,
                "past_content": past_content,
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
                <h4>{c['title']}</h4>
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

st.divider()

# Area di Testing AI
st.markdown("### 🤖 Genera Report di Prova")
st.markdown("Usa questo pulsante per simulare il lavoro del bot ora, senza mandare veri messaggi su Slack.")
if st.button("🚀 Avvia Generazione Ora"):
    with st.spinner("Scansione del web e ragionamento in corso... (può richiedere 15-30 secondi)"):
        try:
            from services.searcher import get_weekly_trends
            from services.llm_agent import generate_strategic_inspo
            
            trends_test = get_weekly_trends()
            camp_test = [c for c in campaigns if c.get("status") == "active"]
            
            # Genera la preview invocando il servizio LLM
            report = generate_strategic_inspo(trends_test, camp_test)
            
            st.success("✅ Generazione completata!")
            st.markdown("---")
            st.markdown(report)
            st.markdown("---")
        except ValueError as ve:
            st.error(f"⚠️ **Errore:** {ve} (Assicurati di aver configurato la chiave GROQ_API_KEY nel file .env!)")
        except Exception as e:
            st.error(f"❌ **Errore imprevisto:** {str(e)}")
