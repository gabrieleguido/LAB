from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import urllib.parse
import json
import requests


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


backend_url = "http://backend:8003"

# funzione per web ui
@app.get("/", response_class=HTMLResponse)
def home(request:Request):
    # valori di default per lo status
    status = {
        "backend":"error",
        "mariadb":"error",
        "ollama":"error"
    }

    try:
        url_status = f"{backend_url}/status"

        response = requests.get(url_status, timeout=2)
        response.raise_for_status()
        response_json = response.json()
    
        status["backend"] = response_json.get("backend", "error")
        status["mariadb"] = response_json.get("database", "error")
        status["ollama"] = response_json.get("ollama", "error")

    except requests.exceptions.RequestException as e:
        print(f"Errore durante la connessione al server: {str(e)}")
    except json.JSONDecodeError:
        print(f"Errore nella decodifica del json")
    except Exception as e:
        print(f"Errore in GET/status: {str(e)}")


    domains_list = []

    try:
        url_domini = f"{backend_url}/domains"

        response = requests.get(url_domini, timeout=2)
        response.raise_for_status()
        response_json = response.json()

        domains_list = response_json.get("domains", [])
    
    except requests.exceptions.RequestException as e:
        print(f"Errore durante la connessione al server: {str(e)}")
    except json.JSONDecodeError:
        print(f"Errore nella decodifica del json")
    except Exception as e:
        print(f"Errore in GET/domains: {e}") 


    ui_data = {
        "request":request,
        "status_backend":status["backend"],
        "status_mariadb":status["mariadb"],
        "status_ollama":status["ollama"],
        "domains":domains_list
    }

    return templates.TemplateResponse(request=request, name="home.html", context=ui_data)



@app.get("/parser_evaluation", response_class=HTMLResponse)
def parser_eval(request:Request, domain:str =None, url:str=None, action=None):
    domains_list = []

    try:
        url_domini = f"{backend_url}/domains"

        response = requests.get(url_domini, timeout=2)
        response.raise_for_status()
        response_json = response.json()

        domains_list = response_json.get("domains", [])
    
    except requests.exceptions.RequestException as e:
        print(f"Errore durante la connessione al server: {str(e)}")
    except json.JSONDecodeError:
        print(f"Errore nella decodifica del json")
    except Exception as e:
        print(f"Errore in GET/domains: {e}") 

    
    url_list = []
    html_grezzo = ""
    testo_parsed = ""
    gs_text = ""
    token_evals = {}
    precision = ""
    recall = ""
    f1 = ""
    score = ""
    feedback = ""

    if domain:
        try:
            gold_standard_urls_url = f"{backend_url}/gold_standard_urls?domain={domain}"  # url per GET/gold_standard_urls
            response = requests.get(gold_standard_urls_url)
            response.raise_for_status()
            response_json = response.json()
            
            url_list = response_json.get("gold_standard_urls", [])

        except requests.exceptions.RequestException as e:
            print(f"Errore durante la connessione al server: {str(e)}")
        except json.JSONDecodeError:
            print(f"Errore nella decodifica del json")
        except Exception as e:
            print(f"Errore in GET/gold_standard_urls: {e}") 



        if action=='live' and url:
            parse_url = f"{backend_url}/parse"  # url per POST/parse
            payload = {
                "url":url,
                "local":False
            }

            try:
                response = requests.post(parse_url, json=payload)   
                response.raise_for_status()
                response_json = response.json()
                
                html_grezzo = response_json.get("html_text", "ERRORE: testo html non trovato")
                testo_parsed = response_json.get("parsed_text", "ERRORE: testo parsato non trovato")

            except requests.exceptions.RequestException as e:
                print(f"Errore durante la connessione al server: {str(e)}")
            except json.JSONDecodeError:
                print(f"Errore nella decodifica del json")
            except Exception as e:
                print(f"Errore in GET/gold_standard_urls: {e}") 
            

            gold_standard_url = f"{backend_url}/gold_standard?url={url}"    # url per GET/gold_standard
            try:
                response = requests.get(gold_standard_url)
                response.raise_for_status()
                response_json = response.json()

                gs_text = response_json.get("gold_text", "Nessun gold text presente per questo url")

            except requests.exceptions.RequestException as e:
                print(f"Errore durante la connessione al server: {str(e)}")
                gs_text = "Nessun gold text presente per questo url"
            except json.JSONDecodeError:
                print(f"Errore nella decodifica del json")
            except Exception as e:
                print(f"Errore in GET/gold_standard: {e}") 


            if gs_text!="" and gs_text!="Nessun gold text presente per questo url":
                evaluate_url = f"{backend_url}/evaluate"    # url per POST/evaluate
                payload = {
                    "parsed_text":testo_parsed,
                    "gold_text":gs_text
                }

                try:
                    response = requests.post(evaluate_url, json=payload)
                    response.raise_for_status()
                    response_json = response.json()
                    
                    token_evals = response_json.get("token_level_eval", {})
                    precision = round(token_evals.get("precision", "N/D"), 4)   # con round arrotondo a 4 cifre decimali
                    recall = round(token_evals.get("recall", "N/D"), 4)
                    f1 = round(token_evals.get("f1", "N/D"), 4)

                except requests.exceptions.RequestException as e:
                    print(f"Errore durante la connessione al server: {str(e)}")
                except json.JSONDecodeError:
                    print(f"Errore nella decodifica del json")
                except Exception as e:
                    print(f"Errore in POST/evaluate: {e}")

                

                evaluate_judge_url = f"{backend_url}/evaluate_judge"
                payload = {
                    "parsed_text":testo_parsed,
                    "gold_text":gs_text
                }

                try:
                    response = requests.post(evaluate_judge_url, json=payload)
                    response.raise_for_status()
                    response_json = response.json()
                    
                    score = response_json.get("judge_score", "N/D")
                    feedback = response_json.get("judge_feedback", "Giudizio complessivo non disponibile")                    

                except requests.exceptions.RequestException as e:
                    print(f"Errore durante la connessione al server: {str(e)}")
                except json.JSONDecodeError:
                    print(f"Errore nella decodifica del json")
                except Exception as e:
                    print(f"Errore in POST/evaluate_judge: {e}")
        
        elif action=='local':
            parse_url = f"{backend_url}/parse"  # url per POST/parse
            payload = {
                "url":url,
                "local":True
            }

            try:
                response = requests.post(parse_url, json=payload)   
                response.raise_for_status()
                response_json = response.json()
                
                html_grezzo = response_json.get("html_text", "ERRORE: testo html non trovato")
                testo_parsed = response_json.get("parsed_text", "ERRORE: testo parsato non trovato")

            except requests.exceptions.RequestException as e:
                print(f"Errore durante la connessione al server: {str(e)}")
            except json.JSONDecodeError:
                print(f"Errore nella decodifica del json")
            except Exception as e:
                print(f"Errore in GET/gold_standard_urls: {e}") 
            

            gold_standard_url = f"{backend_url}/gold_standard?url={url}"    # url per GET/gold_standard
            try:
                response = requests.get(gold_standard_url)
                response.raise_for_status()
                response_json = response.json()

                gs_text = response_json.get("gold_text", "Nessun gold text presente per questo url")

            except requests.exceptions.RequestException as e:
                print(f"Errore durante la connessione al server: {str(e)}")
                gs_text = "Nessun gold text presente per questo url"
            except json.JSONDecodeError:
                print(f"Errore nella decodifica del json")
            except Exception as e:
                print(f"Errore in GET/gold_standard: {e}") 


            if gs_text!="" and gs_text!="Nessun gold text presente per questo url":
                evaluate_url = f"{backend_url}/evaluate"    # url per POST/evaluate
                payload = {
                    "parsed_text":testo_parsed,
                    "gold_text":gs_text
                }

                try:
                    response = requests.post(evaluate_url, json=payload)
                    response.raise_for_status()
                    response_json = response.json()
                    
                    token_evals = response_json.get("token_level_eval", {})
                    precision = round(token_evals.get("precision", "N/D"), 4)   # con round arrotondo a 4 cifre decimali
                    recall = round(token_evals.get("recall", "N/D"), 4)
                    f1 = round(token_evals.get("f1", "N/D"), 4)

                except requests.exceptions.RequestException as e:
                    print(f"Errore durante la connessione al server: {str(e)}")
                except json.JSONDecodeError:
                    print(f"Errore nella decodifica del json")
                except Exception as e:
                    print(f"Errore in POST/evaluate: {e}")

                

                evaluate_judge_url = f"{backend_url}/evaluate_judge"
                payload = {
                    "parsed_text":testo_parsed,
                    "gold_text":gs_text
                }

                try:
                    response = requests.post(evaluate_judge_url, json=payload)
                    response.raise_for_status()
                    response_json = response.json()
                    
                    score = response_json.get("judge_score", "N/D")
                    feedback = response_json.get("judge_feedback", "Giudizio complessivo non disponibile")                    

                except requests.exceptions.RequestException as e:
                    print(f"Errore durante la connessione al server: {str(e)}")
                except json.JSONDecodeError:
                    print(f"Errore nella decodifica del json")
                except Exception as e:
                    print(f"Errore in POST/evaluate_judge: {e}")


    ui_data = {
        "request":request,
        "domains":domains_list,
        "urls": url_list,
        "dominio_scelto": domain,
        "url_scelto":url,
        "testo_html":html_grezzo,
        "testo_parsato":testo_parsed,
        "testo_gs":gs_text,
        "precision":precision,
        "recall":recall,
        "f1":f1,
        "score":score,
        "feedback":feedback
    }

    return templates.TemplateResponse(request=request, name="parser_evaluation.html", context=ui_data)


#GET RENDERIZZA LA UI 
@app.get("/gold_standard_builder", response_class = HTMLResponse)
def gold_standard_builder(request: Request, domain: str = None, url: str = None, action: str = None):
    urls_list = []
    html_grezzo = ""
    domains_list = []
    titolo_estratto = ""
    if action != "carica":
        url = None  
    #RECUPERO DOMINI
    try:
        url_domini = f"{backend_url}/domains"
        response = requests.get(url_domini, timeout=2)
        response.raise_for_status()
        domains_list = response.json().get("domains", [])
    except Exception as e:
        print(f"Errore critico nel recupero dei domini dal backend: {e}")
    #RECUPERO URL
    if domain:
        try:
            url_urls = f"{backend_url}/gold_standard_urls?domain={domain}"
            response = requests.get(url_urls,timeout=2) 
            response.raise_for_status()
            urls_list = response.json().get("gold_standard_urls", [])
        except Exception as e:
            print(f"Avviso: Impossibile recuperare URL per {domain}: {e}")
    
    #AZIONE CARICA HTML E TITOLO
    if action == "carica" and url:
        try:
            parse_url = f"{backend_url}/parse"
            payload = {"url": url, "local": False}
            response = requests.post(parse_url, json=payload)
            response.raise_for_status()
            html_grezzo = response.json().get("html_text", "ERRORE: Testo HTML non trovato")
            titolo_estratto = response.json().get("title", "")
        except Exception as e:
            html_grezzo = f"Errore critico durante il download dell'HTML: {e}"
            titolo_estratto = ""
            
    #COSTRUZIONE PAYLOAD PER JINJA
    ui_data = {
        "request": request,
        "domains": domains_list,
        "dominio_scelto": domain,
        "url_scelto": url,
        "urls": urls_list,
        "testo_html": html_grezzo,
        "titolo_estratto": titolo_estratto
    }
    return templates.TemplateResponse(request=request, name="gold_standard_builder.html", context=ui_data)
#SALVATAGGIO NEL DB
@app.post("/salva_in_db")
def salva_in_db(
    domain: str = Form(...),
    url: str = Form(...), 
    title: str = Form(...), 
    html_content: str = Form(...), 
    gold_text: str = Form(...)

):
    try:
        #invio html
        payload_web = {"url": url, "domain": domain, "title": title, "html_text": html_content}
        res_web = requests.post(f"{backend_url}/add_web_resource", json=payload_web, timeout=5)
        res_web.raise_for_status()
        #invio gs
        payload_gold = {"url": url, "gold_text": gold_text}
        res_gold = requests.post(f"{backend_url}/add_gold_standard", json=payload_gold, timeout=5)
        res_gold.raise_for_status()
        
        redirect_url = f"/gold_standard_builder?domain={domain}&url={urllib.parse.quote(url)}"
        return RedirectResponse(url=redirect_url, status_code=303)

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Errore nel salvataggio: {e}")
#ELIMINAZIONE NEL DB
@app.post("/elimina_dal_db")
def elimina_dal_db(url_da_eliminare:str = Form(...),domain: str = Form(...)):
    try: 
        delete_url = f"{backend_url}/web_resource?url={url_da_eliminare}"
        res_web = requests.delete(delete_url, timeout=5)
        res_web.raise_for_status()
        
        return RedirectResponse(url=f"/gold_standard_builder?domain={domain}", status_code=303)
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Errore nell'eliminazione: {e}")
        
        
@app.get("/stats", response_class=HTMLResponse)
def database_stats_page(request:Request): 
    stats_data = {
        "web_resources":{},
        "gold_standard":{},
        "avg_eval":{},
        "avg_eval_judge":{}
        
    }
    try: 
        url_stats = f"{backend_url}/db_stats"
        response = requests.get(url_stats, timeout=5)
        response.raise_for_status()
        stats_data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Errore durante la connessione al server per le stats: {str(e)}")
    except json.JSONDecodeError:
        print(f"Errore nella decodifica del json delle stats")
    except Exception as e:
        print(f"Errore critico in GET/db_stats: {e}")
    ui_data = {
        "request":request,
        "stats_data":stats_data
    }
    return templates.TemplateResponse(request=request, name="stats.html", context=ui_data)