import os
import json
from dotenv import load_dotenv
from services.searcher import get_weekly_trends
from services.llm_agent import generate_strategic_inspo
from services.slack_notifier import send_message

def load_active_campaigns():
    file_path = "active_campaigns.json"
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            campaigns = json.load(f)
            return [c for c in campaigns if c.get("status") == "active"]
        except Exception:
            return []

def run_bot():
    print("🚀 Inizializzazione Bot JEMP: Caricamento environment...")
    load_dotenv()
    
    print("📊 1/4 - Lettura campagne attive dal tracciatore JSON...")
    active_campaigns = load_active_campaigns()
    print(f"Campagne in corso trovate: {len(active_campaigns)}")
    
    print("🌐 2/4 - Ricerca web dei trend (Social, HR, Gen Z)...")
    trends = get_weekly_trends()
    if not trends:
        print("Nessuna notizia iper-recente trovata o timeout di rete. Procedo con ragionamento base.")
    else:
        print(f"Estratti {len(trends)} input dal web.")
        
    print("🤖 3/4 - Analisi Strategica con Gemini 1.5 Flash...")
    try:
        strategic_message = generate_strategic_inspo(trends, active_campaigns)
        
        print("📨 4/4 - Invio report a Slack...")
        send_message(strategic_message)
        
    except ValueError as ve:
        print(f"\n[ERRORE CONFIGURAZIONE] {ve}")
    except Exception as e:
        print(f"\n[ERRORE GENERALIZZATO] Si è verificato un errore durante la generazione/invio: {e}")

if __name__ == "__main__":
    run_bot()
