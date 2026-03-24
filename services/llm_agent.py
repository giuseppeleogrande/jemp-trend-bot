import os
from groq import Groq

JEMP_SYSTEM_PROMPT = """Sei JEMP AI, l'assistente interno di JEMP (Junior Enterprise of Politecnico di Milano).
Sei specializzato in marketing strategico, contenuti social, employer branding e recruiting universitario.
Il tuo target si divide in:
- Aziende (B2B): per vendere consulenze e fare employer branding in collaborazione con noi.
- Studenti (B2C): per recruiting interno e branding universitario dell'associazione.

Regole di stile:
- Rispondi SEMPRE in italiano (salvo richiesta esplicita contraria).
- Tono: fresco, universitario, creativo ma professionale. Usa emoji dove utile.
- Sii IPER-PRATICO: proponi sempre titoli di post, formati specifici (Carosello, Reels, Stories, LinkedIn), copy o dati reali.
- VIETATE le frasi fatte come "nel panorama in continua evoluzione" o "soluzioni innovative".
- Usa Markdown per formattare le risposte (grassetto, liste, titoli).
"""

def build_campaign_context(campaign):
    """Costruisce il contesto della campagna selezionata come stringa di sistema."""
    if not campaign:
        return "Nessuna campagna specifica selezionata. Ragiona in modo generale sul brand JEMP."
    ctx = f"""
Campagna ATTIVA su cui stai lavorando: **{campaign.get('title', 'N/A')}**
- Descrizione: {campaign.get('description', 'N/A')}
- Scadenza: {campaign.get('end_date', 'N/A')}
- Target Audience: {campaign.get('target_audience', 'Non specificato')}
- Obiettivo Pratico del JEMPer: {campaign.get('jemper_goal', 'Non specificato')}
- Contenuti Passati (cosa ha funzionato): {campaign.get('past_content', 'Non specificato')}
""".strip()
    return ctx

def build_trends_context(trends):
    """Converte la lista di trend in testo leggibile."""
    if not trends:
        return "Nessuna ricerca web effettuata per questa sessione."
    lines = []
    for t in trends:
        lines.append(f"- {t.get('title', '')}: {t.get('snippet', '')}")
    return "\n".join(lines)

def chat_with_jemp_bot(messages_history, campaign=None, trends=None):
    """
    Funzione principale conversazionale. Accetta lo storico completo e restituisce la risposta AI.
    messages_history: lista di dict {"role": "user"/"assistant", "content": "..."}
    campaign: dict campagna selezionata (o None)
    trends: lista di trend DuckDuckGo (o None/vuota)
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY non configurata nel file .env o nei Secrets di Streamlit.")

    client = Groq(api_key=api_key)

    campaign_ctx = build_campaign_context(campaign)
    trends_ctx = build_trends_context(trends)

    system_message = f"""{JEMP_SYSTEM_PROMPT}

--- CONTESTO CORRENTE ---
{campaign_ctx}

--- NOTIZIE DAL WEB (Ricerca in tempo reale) ---
{trends_ctx}
--- FINE CONTESTO ---

Usa queste informazioni come "memoria di sfondo" invisibile nelle tue risposte, senza citarle testualmente a meno che l'utente non le menzioni o chieda esplicitamente di usarle."""

    # Costruzione messaggi per Groq: system + storico
    groq_messages = [{"role": "system", "content": system_message}] + messages_history

    chat_completion = client.chat.completions.create(
        messages=groq_messages,
        model="llama-3.3-70b-versatile",
        temperature=0.75,
        max_tokens=2048,
    )

    return chat_completion.choices[0].message.content


# --- Funzione legacy per il bot automatico settimanale (main.py) ---
def generate_strategic_inspo(trends, active_campaigns):
    """Funzione usata da main.py per il report settimanale automatico su Slack."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY non configurata nel file .env")

    client = Groq(api_key=api_key)

    trends_formatted = [f"- {t.get('title', '')}: {t.get('snippet', '')}" for t in trends]
    trends_text = "\n".join(trends_formatted)

    camp_list = []
    for c in active_campaigns:
        camp_str = f"[{c['title']}] Scadenza: {c['end_date']}\n- Descrizione: {c['description']}"
        if c.get("target_audience"): camp_str += f"\n- Target: {c['target_audience']}"
        if c.get("jemper_goal"): camp_str += f"\n- Obiettivo: {c['jemper_goal']}"
        if c.get("past_content"): camp_str += f"\n- Passato: {c['past_content']}"
        camp_list.append(camp_str)

    campaigns_text = "\n\n".join(camp_list) or "Nessuna campagna attiva."

    prompt = f"""{JEMP_SYSTEM_PROMPT}

Trend web estratti (ultimi 7 giorni):
{trends_text}

Campagne attive:
{campaigns_text}

Scrivi un briefing settimanale Markdown per il team JEMP con:
1. **🔥 I Trend della Settimana** (2 macro-trend con spiegazione in 1 riga)
2. **🎯 Azioni Pratiche per le Campagne Attive** (cosa postare ESATTAMENTE, formato, argomento)
3. **💡 Nuove Inspo (Fuori Campagna)** (2 spunti extra con formato e argomento specifici)
"""

    completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
    )
    return completion.choices[0].message.content
