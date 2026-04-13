import json 

# Usa il context manager 'with' per gestire l'apertura/chiusura
try:
    with open("federcalcio-isole-faroe.html", "r", encoding="utf-8") as html_file:
        html_text = html_file.read()
    
    with open("federcalcio-isole-faroe.txt", "r", encoding="utf-8") as golden_file:
        golden_text = golden_file.read() 

    json_entry = {
        "url": "https://it.uefa.com/news-media/news/025b-0ee5446e6b25-2d76abebda6d-1000--federcalcio-isole-faroe/",
        "domain": "it.uefa.com",
        "title": "federcalcio-isole-faroe",
        "html_text": html_text,
        "gold_text": golden_text
    }

    with open("federcalcio-isole-faroe.json", "w", encoding="utf-8") as result:
        # Usa indent per rendere il JSON leggibile, altrimenti è un muro di testo inutile
        json.dump(json_entry, result, indent=4, ensure_ascii=False)
        
    print("File JSON generato con successo.")

except FileNotFoundError:
    print("Errore: Uno dei file di input non è stato trovato.")
except UnicodeDecodeError as e:
    print(f"Errore di codifica: {e}. Controlla che i file siano davvero in UTF-8.")