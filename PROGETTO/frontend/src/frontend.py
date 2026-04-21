from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import urllib.request
import urllib.parse
import json

##   esegui con comando --->  uvicorn frontend:app --reload --port 8004    ##

app = FastAPI()

templates = Jinja2Templates(directory="templates")

backend_url = "http://backend:8003"   # url del backend server.py da lanciare su porta 8003

# funzione per web ui
@app.get("/", response_class=HTMLResponse)
def web_ui(request:Request, domain:str=None, url:str=None, action:str=None):
    """
    Gestisce la web ui
    """
    
    # liste domini e url
    domains_list = []
    url_list = []

    # testi
    html_grezzo = ""
    testo_parsato = ""
    testo_gs = ""

    # metriche
    precision = ""
    recall = ""
    f1 = ""

    global_precision = None
    global_recall = None
    global_f1 = None

    # GET /domains
    try:
        url_domini = f"{backend_url}/domains"

        # esegue la richiesta POST e ne apre la risposta
        with urllib.request.urlopen(url_domini) as response:
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


        if action == "global_eval":
            try:
                url_globale = f"{backend_url}/full_gs_eval/{url_cod}"

                with urllib.request.urlopen(url_globale) as response:
                    if response.status == 200:
                        met_glob_data = response.read().decode('utf-8')
                        met_glob_json = json.loads(met_glob_data)
                        stats = met_glob_json.get("token_level_eval", {})

                        global_precision = round(stats.get("precision", 0), 4)
                        global_recall = round(stats.get("recall", 0), 4)
                        global_f1 = round(stats.get("f1", 0), 4)
            except Exception as e:
                global_precision = "Errore"
                global_recall = "Errore"
                global_f1 = "Errore"

    
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


    # POST /evaluate --> riempie tabella con metriche
    if testo_parsato and testo_gs and not "Errore" in testo_gs and not "Nessun" in testo_gs:
        try:
            url_eval = f"{backend_url}/evaluate"

            # dizionario con dati per POST
            payload = {
                "parsed_text": testo_parsato,
                "gold_text": testo_gs
            }

            # converto i dati in JSON (da stringa) e codifico in byte utf-8
            data_post_ev = json.dumps(payload).encode('utf-8')

            # passo i dati come richiesta POST (urllib capisce da solo che si tratta di post)
            req = urllib.request.Request(
                url_eval,
                data = data_post_ev,
                headers={'Content-Type': 'application/json'}
            )

            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    risposta = response.read().decode('utf-8')
                    risposta_json = json.loads(risposta)

                    stats = risposta_json.get("token_level_eval", {})

                    precision = round(stats.get("precision", 0), 4)   # arrotonda a 4 cifre decimali
                    recall = round(stats.get("recall", 0), 4)
                    f1 = round(stats.get("f1", 0), 4)


        except Exception as e:
            print(f"Errore generico in POST/evaluate: {e}")
            precision = "ERRORE"
            recall = "ERRORE"
            f1 = "ERRORE"



    ui_data = {
        "request": request,
        "lista_domini": domains_list,
        "dominio_scelto": domain,
        "lista_url": url_list,
        "testo_html": html_grezzo,
        "testo_parsato": testo_parsato,
        "testo_gs": testo_gs,
        "precision": precision,
        "recall": recall,
        "f1": f1
    }

    if action == "global_eval" and global_precision is not None:
        ui_data["global_precision"] = global_precision
        ui_data["global_recall"] = global_recall
        ui_data["global_f1"] = global_f1

    return templates.TemplateResponse(request=request, name="index.html", context=ui_data)


@app.post("/", response_class=HTMLResponse)
async def manual_eval(request: Request):
    """
    Gestisce la valutazione di testo parsato e testo gold standard inseriti manualmente
    """

    body_bytes = await request.body()
    body_str = body_bytes.decode('utf-8')

    form = urllib.parse.parse_qs(body_str)

    manual_parsed = urllib.parse.unquote_plus(form.get("manual_parsed", [""])[0])
    manual_gs = urllib.parse.unquote_plus(form.get("manual_gs", [""])[0])
    azione = form.get("action", [""])[0]

    domains_list = []
    # GET /domains per non far svuotare la tendina in alto
    try:
        url_domini = f"{backend_url}/domains"

        # esegue la richiesta POST e ne apre la risposta
        with urllib.request.urlopen(url_domini) as response:
            if response.status == 200:
                data = response.read().decode('utf-8')  # legge il body della risposta HTTP del server (testo grezzo) e la legge con codifica utf-8
                data_json = json.loads(data)    # trasforma la stringa di testo in un dizionario python

                domains_list = data_json.get("domains", []) # restituisce la chiave "domains", se non la trova restituisce lista vuota senza crashare
    except Exception as e:
        print(f"Errore di connessione al backend {e}")

    manual_precision = ""
    manual_recall = ""
    manual_f1 = ""

    if azione == "run_eval" and manual_parsed and manual_gs:
        if manual_parsed.strip() and manual_gs.strip():
            try:
                url_eval = f"{backend_url}/evaluate"
                payload = {
                    "parsed_text": manual_parsed,
                    "gold_text": manual_gs
                }
                data_post_eval = json.dumps(payload).encode('utf-8')

                req = urllib.request.Request(
                    url_eval,
                    data = data_post_eval,
                    headers={'Content-Type': 'application/json'}
                )

                with urllib.request.urlopen(req) as response:
                    if response.status == 200:
                        risposta = response.read().decode('utf-8')
                        risposta_json = json.loads(risposta)
                        stats = risposta_json.get("token_level_eval", {})

                        manual_precision = round(stats.get("precision", 0), 4)
                        manual_recall = round(stats.get("recall", 0), 4)
                        manual_f1 = round(stats.get("f1", 0), 4)
            except Exception as e:
                print(f"Errore valutazione manuale, {e}")

    elif azione == "run_parser" and manual_parsed:
        try:
            url_p = f"{backend_url}/parse"

            url_finto = "https://en.wikipedia.org/"

            payload_p = {
                "url": url_finto,
                "html_text": manual_parsed
            }
            data_p = json.dumps(payload_p).encode('utf-8')
            req_p = urllib.request.Request(
                url_p,
                data = data_p,
                headers={'Content-Type': 'application/json'}
            )

            with urllib.request.urlopen(req_p) as response:
                if response.status==200:
                    res = json.loads(response.read().decode('utf-8'))
                    manual_parsed = res.get("parsed_text", "Errore nel parsing")
        except Exception as e:
            manual_parsed = "Errore di connessione al parser"

    ui_data = {
        #variabili precedenti
        "request": request,
        "lista_domini": domains_list,
        "dominio_scelto": None,
        "lista_url": [],
        "testo_html": "",
        "testo_parsato": "",
        "testo_gs": "",
        "precision": "",
        "recall": "",
        "f1": "",

        #variabili sezione manuale
        "manual_parsed": manual_parsed,
        "manual_gs": manual_gs,
        "manual_precision": manual_precision,
        "manual_recall": manual_recall,
        "manual_f1": manual_f1
    }

    return templates.TemplateResponse(request=request, name="index.html", context=ui_data)   