import json

# Legge l'HTML
with open("html_to_format.html", "r", encoding="utf-8") as f:
    html = f.read()

# Crea il JSON
with open("html_formatted.json", "w", encoding="utf-8") as f:
    json.dump({"html": html}, f, indent=4)

print("Fatto!")
