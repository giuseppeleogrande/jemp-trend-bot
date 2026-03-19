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
Rispondi *esclusivamente* in italiano. Scrivi e formatta in puro Markdown un briefing strategico per il team Marketing. Devi includere esattamente:
1. **Highlight della Settimana**: I 2 macro-trend o argomenti più rilevanti e freschi.
2. **Spunti per le Campagne Attive**: Come possiamo integrare i temi caldi visti sopra all'interno delle campagne che stiamo già facendo? Fornisci consigli pratici e diretti su formato/messaggio. Se non ci sono campagne, offri consigli generali per l'assenza di campagne in corso.
3. **Idee Nuove**: 2 spunti originali (formati o post pratici) per attrarre aziende o studenti.

Mantieni un tono: Professionale, Dinamico, B2B-friendly ma "fresco". Usa emoji pertinenti, evita frasi fatte e vai dritto al punto.
"""

    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-70b-8192",
    )
    
    return chat_completion.choices[0].message.content
