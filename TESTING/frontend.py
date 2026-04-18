from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import urllib.request
import json

app = FastAPI()

templates = Jinja2Templates(directory="templates")

backend_url = "http://127.0.0.1:8000"

# funzione per web ui
@app.get("/", response_class=HTMLResponse)
def web_ui(request:Request, domain:str=None):
    
    domains_list = []

    try:
        url = f"{backend_url}/richiesta"
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                data = response.read().decode('utf-8')
                data_json = json.loads(data)

                domains_list = data_json.get("domains", [])
    except Exception as e:
        print(f"Errore di connessione al backend {e}")    
    
    ui_data = {
        "request": request,
        "lista_domini": domains_list.domains,
        "dominio_scelto": domain
    }

    return templates.TemplateResponse(request=request, name="index.html", context=ui_data)