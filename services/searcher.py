from duckduckgo_search import DDGS
import time

def get_weekly_trends():
    queries = [
        "trend social media marketing linkedin instagram",
        "employer branding gen z recruiting mondo del lavoro",
        "università studenti trend gen z italia"
    ]
    
    results = []
    for q in queries:
        try:
            # Timeout esplicito di 10s per evitare hang su server cloud
            with DDGS(timeout=10) as ddgs:
                search_results = ddgs.text(
                    q,
                    region='it-it',
                    safesearch='off',
                    timelimit='w',
                    max_results=5
                )
                if search_results:
                    for r in search_results:
                        results.append({
                            "query_category": q,
                            "title": r.get('title', ''),
                            "snippet": r.get('body', ''),
                            "link": r.get('href', '')
                        })
        except Exception as e:
            print(f"Errore ricerca per '{q}': {e}")
            # Continua con le prossime query invece di crashare
            continue
        
        time.sleep(1)  # Piccola pausa tra le query per evitare rate limiting

    return results

if __name__ == "__main__":
    trend = get_weekly_trends()
    for t in trend:
        print(t)
