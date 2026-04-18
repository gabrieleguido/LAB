from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import urllib.request
import urllib.parse
import json

##   esegui con comando --->  uvicorn frontend:app --reload --port 8004    ##

app = FastAPI()

templates = Jinja2Templates(directory="templates")

backend_url = "http://127.0.0.1:8003"

# funzione per web ui
@app.get("/", response_class=HTMLResponse)
def web_ui(request:Request, domain:str=None, url:str=None):
    """
    Gestisce la web ui
    """
    
    domains_list = []
    url_list = []
    html_grezzo = ""
    testo_parsato = ""
    testo_gs = ""

    # GET /domains
    try:
        url_domini = f"{backend_url}/domains"
        with urllib.request.urlopen(url_domini) as response:   # si collega al backend su url, con with la connessione viene automaticamente chiusa alla fine del blocco
            if response.status == 200:
                data = response.read().decode('utf-8')  # legge il body della risposta HTTP del server (testo grezzo) e la legge con codifica utf-8
                data_json = json.loads(data)    # trasforma la stringa di testo in un dizionario python

                domains_list = data_json.get("domains", []) # restituisce la chiave "domains", se non la trova restituisce lista vuota senza crashare
    except Exception as e:
        print(f"Errore di connessione al backend {e}")    
    

    #GET /full_gold_standard
    if domain:
        try:
            # per passare un dominio senza bug creo un url finto, lo codifico e ne estraggo il dominio in backend dopo averlo decodificato
            url_fake = f"https://{domain}/"
            url_cod = urllib.parse.quote(url_fake, safe='')
            url_full_gs = f"{backend_url}/full_gold_standard/{url_cod}"

            with urllib.request.urlopen(url_full_gs) as response:
                if response.status == 200:
                    gs = response.read().decode('utf-8')
                    gs_json = json.loads(gs)
                    for elem in gs_json.get("gold_standard", []):
                        url_list.append(elem['url'])

        except Exception as e:
            print(f"Errore nel server, code: {e.code}")


    
    # GET /gold_standard e GET /parse
    if url:
        # blocco per GET /gold_standard e riempe textarea "Testo GS"
        try:
            url_cod = urllib.parse.quote(url, safe='')  # codifica l'url
            url_gs = f"{backend_url}/gold_standard/{url_cod}"
            with urllib.request.urlopen(url_gs) as response:
                if response.status == 200:
                    data = response.read().decode('utf-8')
                    data_json = json.loads(data)
                    testo_gs = data_json.get("gold_text", "Testo gs non trovato") 
        except urllib.error.HTTPError as e:
            if e.code == 404:
                testo_gs = "Nessun gold standard trovato per questo url"
            else:
                testo_gs = f"Errore del server, code: {e.code}" 
        except Exception as e:
            print(f"Errore generico {e}") 

        # blocco per GET /parse e riempe textarea "Testo pulito" e "HTML grezzo"
        try:
            url_parse = f"{backend_url}/parse/{url_cod}"    # riutilizzo lo stesso url codificato di get/gold_standard
            
            with urllib.request.urlopen(url_parse) as response:
                if response.status == 200:
                    data = response.read().decode('utf-8')
                    data_json = json.loads(data)

                    html_grezzo = data_json.get("html_text", "ERRORE: testo html non trovato")
                    testo_parsato = data_json.get("parsed_text", "ERRORE: testo parsato non trovato")
        except urllib.error.HTTPError as e:
            html_grezzo = f"Errore del server, code: {e.code}"
            testo_parsato = f"Errore del server, code: {e.code}"
        except Exception as e:
            print(f"Errore generico parser {e}")



    ui_data = {
        "request": request,
        "lista_domini": domains_list,
        "dominio_scelto": domain,
        "lista_url": url_list,
        "testo_html": html_grezzo,
        "testo_parsato": testo_parsato,
        "testo_gs": testo_gs
    }

    return templates.TemplateResponse(request=request, name="index.html", context=ui_data)