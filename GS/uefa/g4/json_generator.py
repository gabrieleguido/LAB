import json 

# Usa il context manager 'with' per gestire l'apertura/chiusura
try:
    with open("il-calcio-italiano-piange-rocco-commisso.html", "r", encoding="utf-8") as html_file:
        html_text = html_file.read()
    
    with open("il-calcio-italiano-piange-rocco-commisso.txt", "r", encoding="utf-8") as golden_file:
        golden_text = golden_file.read() 

    json_entry = {
        "url": "https://it.uefa.com/news-media/news/02a1-1fb7c7f00ff2-a70c366a7484-1000--il-calcio-italiano-piange-rocco-commisso/",
        "domain": "it.uefa.com",
        "title": "il-calcio-italiano-piange-rocco-commisso",
        "html_text": html_text,
        "gold_text": golden_text
    }

    with open("il-calcio-italiano-piange-rocco-commisso.json", "w", encoding="utf-8") as result:
        # Usa indent per rendere il JSON leggibile, altrimenti è un muro di testo inutile
        json.dump(json_entry, result, indent=4, ensure_ascii=False)
        
    print("File JSON generato con successo.")

except FileNotFoundError:
    print("Errore: Uno dei file di input non è stato trovato.")
except UnicodeDecodeError as e:
    print(f"Errore di codifica: {e}. Controlla che i file siano davvero in UTF-8.")