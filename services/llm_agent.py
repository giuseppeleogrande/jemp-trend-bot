import os
from groq import Groq

def generate_strategic_inspo(trends, active_campaigns):
    # Passiamo a Groq (LLaMA-3) che non richiede carta di credito in Europa
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY non configurata nel file .env")
        
    client = Groq(api_key=api_key)
    
    # Formatta i trend testuali
    trends_formatted = []
    for t in trends:
        title = t.get('title', 'Senza Titolo')
        snippet = t.get('snippet', '')
        trends_formatted.append(f"- {title}: {snippet}")
    trends_text = "\n".join(trends_formatted)
    
    # Formatta le campagne
    campaigns_text = "\n".join([f"- {c['title']} (Scadenza: {c['end_date']}): {c['description']}" for c in active_campaigns])
    if not campaigns_text.strip():
        campaigns_text = "Nessuna campagna attiva al momento."

    prompt = f"""
Sei il Consulente Strategico Marketing di JEMP (Junior Enterprise of Politecnico di Milano).
Il nostro target:
1. Aziende (B2B): per vendere consulenze aziendali e fare employer branding collaborando con noi.
2. Studenti (B2C): per recruiting interno e branding universitario della nostra associazione.

Ecco i micro-trend web estratti da ricerche su notizie degli ultimi 7 giorni:
{trends_text}

Ecco le nostre campagne attualmente attive:
{campaigns_text}

Compito:
Rispondi *esclusivamente* in italiano. Scrivi e formatta in puro Markdown un briefing per il team Marketing JEMP. Non restare sul vago o sul teorico. Devi fornire idee IPER-PRATICHE e PRONTE ALL'USO. Includi esattamente:

1. **🔥 I Trend della Settimana**: I 2 macro-trend più rilevanti estratti dal web, spiegati in una riga.
2. **🎯 Azioni Pratiche per le Campagne Attive**: Per le campagne attive, proponi *esattamente* cosa postare. Sii super specifico. Esempio di livello da mantenere: "Fai un Carosello Instagram sui 5 Plugin Figma indispensabili per gli studenti di design" oppure "Post LinkedIn B2B con un'infografica su 3 dati reali sul welfare per attrarre aziende". Ipotizza tu i tool o i dati se serve essere creativi!
3. **💡 Nuove Inspo (Fuori Campagna)**: 2 spunti originali extra (B2B o B2C). Dimmi il formato esatto (Reels, Carosello, Intervista) e l'argomento pratico (es. produttività, tool AI, vita da poli).

Regole di Stile: Tono "Fresco" e da universitari creativi ma professionale. Usa emoji. VIETATE le frasi fatte come "nel panorama in continua evoluzione". Vai dritto al punto con le liste.
"""

    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
    )
    
    return chat_completion.choices[0].message.content
