import json 

# Usa il context manager 'with' per gestire l'apertura/chiusura
try:
    with open("anteprima-liverpool-paris-saint-germain-champions-league.html", "r", encoding="utf-8") as html_file:
        html_text = html_file.read()
    
    with open("anteprima-liverpool-paris-saint-germain-champions-league.txt", "r", encoding="utf-8") as golden_file:
        golden_text = golden_file.read() 

    json_entry = {
        "url": "https://it.uefa.com/uefachampionsleague/news/02a4-2060af553568-cd2fcc38c28e-1000--anteprima-liverpool-paris-saint-germain-champions-league",
        "domain": "it.uefa.com",
        "title": "anteprima-liverpool-paris-saint-germain-champions-league",
        "html_text": html_text,
        "gold_text": golden_text
    }

    with open("anteprima-liverpool-paris-saint-germain-champions-league.json", "w", encoding="utf-8") as result:
        # Usa indent per rendere il JSON leggibile, altrimenti è un muro di testo inutile
        json.dump(json_entry, result, indent=4, ensure_ascii=False)
        
    print("File JSON generato con successo.")

except FileNotFoundError:
    print("Errore: Uno dei file di input non è stato trovato.")
except UnicodeDecodeError as e:
    print(f"Errore di codifica: {e}. Controlla che i file siano davvero in UTF-8.")