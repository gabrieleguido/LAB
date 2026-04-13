import json 

# Usa il context manager 'with' per gestire l'apertura/chiusura
try:
    with open("gs5_html.html", "r", encoding="utf-8") as html_file:
        html_text = html_file.read()
    
    with open("gs5.txt", "r", encoding="utf-8") as golden_file:
        golden_text = golden_file.read() 

    json_entry = {
        "url": "https://www.nbcnews.com/business/markets/oil-prices-surge-trump-says-us-will-blockade-strait-hormuz-rcna330824",
        "domain": "www.nbcnews.com",
        "title": "Oil prices surge as U.S. begins blockade of Iran's ports",
        "html_text": html_text,
        "gold_text": golden_text
    }

    with open("gs5.json", "w", encoding="utf-8") as result:
        # Usa indent per rendere il JSON leggibile, altrimenti è un muro di testo inutile
        json.dump(json_entry, result, indent=4, ensure_ascii=False)
        
    print("File JSON generato con successo.")

except FileNotFoundError:
    print("Errore: Uno dei file di input non è stato trovato.")
except UnicodeDecodeError as e:
    print(f"Errore di codifica: {e}. Controlla che i file siano davvero in UTF-8.")