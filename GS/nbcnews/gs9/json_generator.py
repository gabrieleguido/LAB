import json 

# Usa il context manager 'with' per gestire l'apertura/chiusura
try:
    with open("gs9_html.html", "r", encoding="utf-8") as html_file:
        html_text = html_file.read()
    
    with open("gs9.txt", "r", encoding="utf-8") as golden_file:
        golden_text = golden_file.read() 

    json_entry = {
        "url": "https://www.nbcnews.com/tech/tech-news/musk-lawyer-hammers-openai-co-founder-30-billion-stake-rcna343518",
        "domain": "www.nbcnews.com",
        "title": "Musk's lawyer hammers OpenAI co-founder over nearly $30 billion stake in organization",
        "html_text": html_text,
        "gold_text": golden_text
    }

    with open("gs9.json", "w", encoding="utf-8") as result:
        # Usa indent per rendere il JSON leggibile, altrimenti è un muro di testo inutile
        json.dump(json_entry, result, indent=4, ensure_ascii=False)
        
    print("File JSON generato con successo.")

except FileNotFoundError:
    print("Errore: Uno dei file di input non è stato trovato.")
except UnicodeDecodeError as e:
    print(f"Errore di codifica: {e}. Controlla che i file siano davvero in UTF-8.")