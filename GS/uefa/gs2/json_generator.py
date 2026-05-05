import json 

# Usa il context manager 'with' per gestire l'apertura/chiusura
try:
    with open("il-calcio-europeo-piange-mircea-lucescu.html", "r", encoding="utf-8") as html_file:
        html_text = html_file.read()
    
    with open("il-calcio-europeo-piange-mircea-lucescu.txt", "r", encoding="utf-8") as golden_file:
        golden_text = golden_file.read() 

    json_entry = {
        "url": "https://it.uefa.com/news-media/news/02a4-2055ce941e1b-ef117e3ca3d2-1000--il-calcio-europeo-piange-mircea-lucescu/",
        "domain": "it.uefa.com",
        "title": "il-calcio-europeo-piange-mircea-lucescu",
        "html_text": html_text,
        "gold_text": golden_text
    }

    with open("il-calcio-europeo-piange-mircea-lucescu.json", "w", encoding="utf-8") as result:
        # Usa indent per rendere il JSON leggibile, altrimenti è un muro di testo inutile
        json.dump(json_entry, result, indent=4, ensure_ascii=False)
        
    print("File JSON generato con successo.")

except FileNotFoundError:
    print("Errore: Uno dei file di input non è stato trovato.")
except UnicodeDecodeError as e:
    print(f"Errore di codifica: {e}. Controlla che i file siano davvero in UTF-8.")