from duckduckgo_search import DDGS

def get_weekly_trends():
    queries = [
        "trend social media marketing linkedin instagram",
        "employer branding gen z recruiting mondo del lavoro",
        "università studenti trend gen z italia"
    ]
    
    results = []
    with DDGS() as ddgs:
        for q in queries:
            try:
                # time='w' restringe la ricerca all'ultima settimana
                search_results = ddgs.text(q, region='it-it', safesearch='off', timelimit='w', max_results=5)
                # handle generator/iterator return type
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
                
    return results

if __name__ == "__main__":
    trend = get_weekly_trends()
    for t in trend:
        print(t)
