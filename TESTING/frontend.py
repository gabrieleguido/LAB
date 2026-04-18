from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import urllib.request
import json

##   esegui con comando --->  uvicorn frontend:app --reload --port 8004    ##

app = FastAPI()

templates = Jinja2Templates(directory="templates")

backend_url = "http://127.0.0.1:8003"

# funzione per web ui
@app.get("/", response_class=HTMLResponse)
def web_ui(request:Request, domain:str=None):
    """
    Gestisce la web ui
    """
    
    domains_list = []

    try:
        url = f"{backend_url}/domains"
        with urllib.request.urlopen(url) as response:   # si collega al backend su url, con with la connessione viene automaticamente chiusa alla fine del blocco
            if response.status == 200:
                data = response.read().decode('utf-8')  # legge il body della risposta HTTP del server (testo grezzo) e la legge con codifica utf-8
                data_json = json.loads(data)    # trasforma la stringa di testo in un dizionario python

                domains_list = data_json.get("domains", []) # restituisce la chiave "domains", se non la trova restituisce lista vuota senza crashare
    except Exception as e:
        print(f"Errore di connessione al backend {e}")    
    
    ui_data = {
        "request": request,
        "lista_domini": domains_list,
        "dominio_scelto": domain
    }

    return templates.TemplateResponse(request=request, name="index.html", context=ui_data)