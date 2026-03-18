import os
import google.generativeai as genai

def generate_strategic_inspo(trends, active_campaigns):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your-gemini-key-here":
        raise ValueError("GEMINI_API_KEY non configurata nel file .env")
        
    genai.configure(api_key=api_key)
    # Usa gemini-1.5-flash che è veloce, gratuito ed estremamente capace per task di sintesi e creatività
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Formatta i trend testuali limitando un po' la base di testo per evitare confusione
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
Scrivi e formatta in puro Markdown un briefing strategico per il team Marketing. Deve contenere esattamente:
1. **Highlight della Settimana**: I 2 macro-trend o argomenti più rilevanti e freschi.
2. **Spunti per le Campagne Attive**: Come possiamo integrare i temi caldi visti sopra all'interno delle campagne che stiamo già facendo? Fornisci consigli pratici e diretti su formato/messaggio.
3. **Idee Nuove (Instagram/LinkedIn)**: 2 spunti originali (non post pronti, ma format/argomenti) per attrarre aziende o studenti, sfruttando i trend analizzati.

Mantieni un tono: Professionale, Dinamico, B2B-friendly ma "fresco" da universitari tech/business. Usa emoji pertinenti, niente fluff.
Sii analitico: se i trend trovati sono deboli, tira fuori intuizioni generali legate a quel mondo (gen z, IA, lavoro).
"""

    response = model.generate_content(prompt)
    return response.text
