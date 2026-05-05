import json
import re
import os

# Metti qui il nome esatto del tuo file (aggiungi .json se serve, dall'immagine sembra senza estensione o nascosta)
input_filename = 'weather_gs.json' 
output_filename = 'weather_gs_light.json'

print(f"Caricamento di {input_filename}...")

try:
    with open(input_filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("Snellimento dell'HTML in corso...")
    for entry in data:
        if 'html_text' in entry:
            html = entry['html_text']
            
            # Rimuoviamo in blocco i tag che pesano tantissimo e non servono al parser
            html = re.sub(r'<script.*?>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
            html = re.sub(r'<style.*?>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
            html = re.sub(r'<svg.*?>.*?</svg>', '', html, flags=re.DOTALL | re.IGNORECASE)
            
            entry['html_text'] = html

    # Salviamo in un nuovo file per sicurezza
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    old_size = os.path.getsize(input_filename) / 1024
    new_size = os.path.getsize(output_filename) / 1024
    
    print(f"Fatto! Dimensione originale: {old_size:.2f} KB")
    print(f"Nuova dimensione: {new_size:.2f} KB")
    print(f"Ora rinomina '{output_filename}' in '{input_filename}' e lancia i test!")

except Exception as e:
    print(f"Errore: {e}")