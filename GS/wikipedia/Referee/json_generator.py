import json 

# Usa il context manager 'with' per gestire l'apertura/chiusura
try:
    with open("Referee_html.html", "r", encoding="utf-8") as html_file:
        html_text = html_file.read()
    
    with open("Referee_GS.txt", "r", encoding="utf-8") as golden_file:
        golden_text = golden_file.read() 

    json_entry = {
        "url": "https://en.wikipedia.org/wiki/Referee",
        "domain": "en.wikipedia.org",
        "title": "Referee",
        "html_text": html_text,
        "gold_text": golden_text
    }

    with open("Referee.json", "w", encoding="utf-8") as result:
        # Usa indent per rendere il JSON leggibile, altrimenti è un muro di testo inutile
        json.dump(json_entry, result, indent=4, ensure_ascii=False)
        
    print("File JSON generato con successo.")

except FileNotFoundError:
    print("Errore: Uno dei file di input non è stato trovato.")
except UnicodeDecodeError as e:
    print(f"Errore di codifica: {e}. Controlla che i file siano davvero in UTF-8.")