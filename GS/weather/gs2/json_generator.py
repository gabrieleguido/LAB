import json 

# Usa il context manager 'with' per gestire l'apertura/chiusura
try:
    with open("gs2_html.html", "r", encoding="utf-8") as html_file:
        html_text = html_file.read()
    
    with open("gs2.txt", "r", encoding="utf-8") as golden_file:
        golden_text = golden_file.read() 

    json_entry = {
        "url": "https://weather.com/it-IT/tempo/orario/l/104b5c3a7e17868e40f84026b44fd565a02ee18193bb030a5cbd3076e58c01bc",
        "domain": "www.weather.com",
        "title": "Previsioni meteo per ora- Roma, città metropolitana di Roma Capitale",
        "html_text": html_text,
        "gold_text": golden_text
    }

    with open("gs2.json", "w", encoding="utf-8") as result:
        # Usa indent per rendere il JSON leggibile, altrimenti è un muro di testo inutile
        json.dump(json_entry, result, indent=4, ensure_ascii=False)
        
    print("File JSON generato con successo.")

except FileNotFoundError:
    print("Errore: Uno dei file di input non è stato trovato.")
except UnicodeDecodeError as e:
    print(f"Errore di codifica: {e}. Controlla che i file siano davvero in UTF-8.")