from fastapi import FastAPI, HTTPException
import requests
from pydantic import BaseModel
import json
from urllib.parse import urlparse,unquote
import urllib.request
from token_compare import TokenCompare
import os
from typing import List,Dict,Tuple, Optional 
import parser_wikipedia as parser_wikipedia
import parser_nbcnews as parser_nbcnews
import parser_uefa as parser_uefa
import parser_weather as parser_weather
from cleaner import Cleaner
import asyncio
import mariadb
from populate_db import Populator

#region MARIADB_SETUP
#stato delle componenti: db e ollama
status = {"mariadb":False,
          "ollama":False}

#funzione per le query
def execute_query(conn:mariadb.Connection,query:str,param:Tuple=None)->List[Tuple[str]]:
    """funzione per eseguire le query che ritorna una lista di tuple (di stringhe).
    Ha un parametro opzionale con la tupla della query parametrizzata"""
    with conn.cursor() as cursor:
        cursor.execute(query,param)
        conn.commit()
        #Se la query non seleziona, ritorno una lista vuota
        if cursor.description is None:
            return []
        result = cursor.fetchall()
        return result


#connessione al db 
conn = mariadb.connect(
    host = "127.0.0.1",
    port = 3306,
    user = "backend_user",
    password = "backend_password",
    database = "lab_db"
)


#POPOLAZIONE DB (solo se db vuoto)
if(len(execute_query(conn,"SELECT * FROM web_resources AS w JOIN gold_standard g ON w.url = g.url"))==0):
    Populator.populate(conn)

#endregion

##   esegui con comando --->  uvicorn server:app --reload --port 8003    ##

app = FastAPI()

# Lista dei domini assegnati
domains_list = TokenCompare.get_domain_list("../../domains.json")

#questo dizionario facilita la ricerca dei nomi dei file dato un dominio
domain_to_name_dict = {
    "www.nbcnews.com":"nbcnews",
    "en.wikipedia.org":"wikipedia",
    "it.uefa.com":"uefa",
    "weather.com":"weather"
}

# Mapping dominio -> funzione parser
CUSTOM_PARSERS = {
    "www.nbcnews.com": parser_nbcnews,
    "it.uefa.com": parser_uefa,
    "en.wikipedia.it":parser_wikipedia,
    "weather.com": parser_weather
}


#region MODELLI I/O FASTAPI
# Modello di risposta per GET /domains
class DomainsListModel(BaseModel):
    """    
        domains: List[str]
    """
    domains: List[str]


# Modello di risposta per GET /gold_standard
class GoldStandardModel(BaseModel):
    """
        url: str\n
        domain: str\n
        title: str\n
        html_text: str\n
        gold_text: str
    """
    url: str
    domain: str
    title: str
    html_text: str
    gold_text: str


# Modello di risposta per GET /full_gold_standard
class FullGoldStandardModel(BaseModel):
    """
            gold_standard: List[GoldStandardModel]
    """
    gold_standard: List[GoldStandardModel]


# Modello di risposta per GET /parse
class ParseOutputModel(BaseModel):
    """
        url:str\n
        domain:str\n
        title:str\n
        html_text:str\n
        parsed_text:str
    """
    url:str
    domain:str
    title:str
    html_text:str
    parsed_text:str

#modello del body nella POST /evaluate
class EvaluateInputModel(BaseModel):
    """
        parsed_text:str\n
        gold_text:str
    """
    parsed_text:str
    gold_text:str 

#modello di risposta nella POST /evaluate
class EvaluateOutputModel(BaseModel):
    """
        token_level_eval:Dict[str,float]

    """
    token_level_eval:Dict[str,float]

class PostParseInputModel(BaseModel):
    """
        url:str\n
        local:bool
    """
    url:str
    local:Optional[bool]

#modello di risposta della GET /gold_standard_urls
class GoldStandardUrlsOutputModel(BaseModel):
    """gold_standard_urls:List[str]"""
    gold_standard_urls:List[str]

#modelli di input di POST/add_web_resource e /add_gold_standard
class AddWebResourceInputModel(BaseModel):
    """ 
        url:str\n
        html_text:str\n
    """ 
    url:str
    html_text:str
class AddGoldStandardInputModel(BaseModel):
    """ 
        url:str\n
        gold_text:str\n
    """ 
    url:str
    gold_text:str
#modello di risposta delle POST di inserimento dati (qui sopra)
class AddOutputModel(BaseModel):
    """status:str"""
    status:str

#modello per il web_resources
class WebResourcesModel(BaseModel):
    """
    url:str\n
    domain:str\n
    title:str\n
    html_text:str\n 
    created_at:str \n
    """
    url:str
    domain:str
    title:str
    html_text:str 
    created_at:str 

#modello per il gold_standard
class GoldStandardModelDB(BaseModel):
    """url:str\n
    gold_text:str\n
    created_at:str"""
    url:str
    gold_text:str
    created_at:Optional[str] = None


#modello di risposta della GET/db_schema
class DBSchemaModel(BaseModel):
    """web_resources:WebResourcesModel\n
    gold_standard:GoldStandardModelDB"""
    web_resources:WebResourcesModel
    gold_standard:GoldStandardModelDB

#modello di risposta GET/status
class StatusResponse(BaseModel):
    """
    backend:str\n
    database:str \n
    ollama:str 
    """
    backend:str
    database:str 
    ollama:str 

#modello di risposta di POST/evaluate_judge
class EvaluateJudgeOutputModel(BaseModel):
    """
    model_name:str,\n
    judge_score:int,\n
    judge_feedback:str
    """
    model_name:str
    judge_score:int
    judge_feedback:str

#modello di risposta di GET/full_gs_eval 
class FullEvaluateModel(BaseModel):
    """token_level_eval:Dict[str:float]\n
    judge_score:float"""
    token_level_eval:Dict[str, float]
    judge_score:float

#endregion

#region FASTAPI

#POST/parse
@app.post("/parse")
def parse_html(input:PostParseInputModel)->ParseOutputModel:
    """
        Riceve in input un url e un bool e restituisce :\n
        url\n
        dominio\n
        titolo (estratto dall'html)\n
        testo html\n
        testo risultato del parser

        Se local = true usa la pagina nel DB senza crawl
    """

    url_orig = unquote(input.url).strip()
    domain = Cleaner.get_domain_from_url(url_orig)
    
    if(domain not in domains_list):
        raise HTTPException(status_code=404, detail="Dominio non supportato")
    
    url_to_parse = ""
    html = ""
    if(input.local):
        #CERCO URL NEL DB E PRENDO L'HTML
        try:
            res = execute_query(conn,"SELECT html_text FROM web_resources WHERE url = ?",(url_orig,))
            if(len(res)==0):
                raise HTTPException(status_code=404, detail="url assente nel db")
            else:
                html = res[0][0]
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"{e}")
        
        url_to_parse = f'raw:{html}'            
    else:
        #RICERCA LIVE DEL URL
        url_to_parse = url_orig

    try:
        parser_module = CUSTOM_PARSERS.get(domain, parser_wikipedia)
        result_dict = asyncio.run(parser_module.extract(url_to_parse))
        html = result_dict.get("html")
        title = Cleaner.get_title_from_html(html)

        markdown_txt = f"# {title}\n\n{result_dict['parsed']}"

        return ParseOutputModel(
                url=unquote(input.url),
                domain = domain,
                title = Cleaner.get_title_from_html(html),
                html_text = html,
                parsed_text = markdown_txt
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore: {str(e)}")


#GET/domains
@app.get("/domains")
def get_domains()->DomainsListModel:
    """
    Restituisce oggetto JSON contenente la lista dei domini assegnati
    """
    return DomainsListModel(domains=domains_list)


#GET/gold_standard
@app.get("/gold_standard")
def get_gold_standard(url: str)->GoldStandardModel:
    """
    Restituisce oggetto JSON contenente il gold standard del dominio in input
    """
    url_pulito = unquote(url).strip()
    domain = Cleaner.get_domain_from_url(url_pulito)
    
    if domain not in domains_list:
        raise HTTPException(status_code=404, detail="Dominio non supportato")
    
    
    file_name = domain_to_name_dict.get(domain)
    file_path = f"../../gs_data/{file_name}_gs.json"

    # if not os.path.exists(file_path):
    #     raise HTTPException(status_code=500, detail=f"File {file_path} non trovato")

    with open(file_path, "r", encoding="utf-8") as f:
        try:
            gs_list = json.load(f)
            for gs in gs_list:
                if url_pulito.strip() == gs.get("url", "").strip():
                    return GoldStandardModel(**gs)
            raise HTTPException(status_code=404, detail="Url non trovato")
            
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="File json corrotto")


#GET/gold_standard_urls
@app.get("/gold_standard_urls")
def get_gs_urls(domain:str)->GoldStandardUrlsOutputModel:
    "Ritorna la lista degli url di un dominio in input"

    if(domain not in domains_list):
        raise HTTPException(status_code=404, detail="Dominio non supportato")

    query = "SELECT g.url " \
    " FROM web_resources AS w JOIN gold_standard AS g ON w.url = g.url " \
    "WHERE domain = ?"

    result = execute_query(
            conn,
            query,
            (domain,)
        )

    url_list = []

    for elem in result:
        url_list.append(elem[0])

    return GoldStandardUrlsOutputModel(gold_standard_urls=url_list)


#POST/evaluate
@app.post("/evaluate")
def evaluate(input_item:EvaluateInputModel)->EvaluateOutputModel:
    """
        Restituisce le valutazioni per un testo parsato e il suo gs passati nel body
    """
    #prendo il dizionario con le statistiche di token evaluation, 
    #vedere TokenCompare per i dettagli
    stats = TokenCompare.build_eval_from_parsed_gs_string(input_item.parsed_text,input_item.gold_text,print_stats_flag=True)
    return EvaluateOutputModel(token_level_eval=stats)


#POST/evaluate_judge
@app.post("/evaluate_judge")
def judge(req:EvaluateInputModel)->EvaluateJudgeOutputModel:
    """
    Utilizza ollama per valutare la qualità del testo parsato rispetto al gold standard
    """

    # pulisco parsed e gold text
    clean_parsed_text = Cleaner.remove_markdown(req.parsed_text)
    clean_gold_text = Cleaner.remove_markdown(req.gold_text)

    # gestisco il caso in cui i testi sono vuoti
    if not clean_parsed_text and not clean_gold_text:
        return EvaluateJudgeOutputModel(
            model_name="gemma4:e2b",
            judge_score=1,
            judge_feedback="Impossibile valutare, i testi sono vuoti"
        )

    # configurazione di ollama
    OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
    model_used = "gemma4:e2b"

    # tecnica "few-shot prompting" per aggirare il più possibile i limiti tecnici del modello
    sys_msg = f"""
        Sei un valutatore algoritmico severo. Il tuo compito è confrontare il seguente testo estratto da una pagina web "parsed text" con un testo "gold text".
        REGOLE DI VALUTAZIONE:
        - score 1: il testo estratto è completamente slegato dal gold text, parla di un argomento compleatamente diverso, contiene frasi casuali (es. "ciao", "hello"), è vuoto, oppure non ha senso semantico.
        - score 2-3: il testo estratto contiene alcune informazioni giuste, ma la formattazione è rotta o le frasi sono tagliate.
        - score 4-5: il testo estratto contiene tutte le informazioni del gold text ed è fluido.
        
        ESEMPIO DA SEGUIRE:
        se testo estratto = "ciao come stai" e gold text = "La NASA ha lanciato il razzo."
        risposta corretta: {{"score": 1, "feedback": "Il testo estratto è una frase casuale e non ha alcuna attinenza con il Gold Standard."}}.
        se stai analizzando dati meteo fai attenzione al luogo geografico e alla finestra temporale. se le zone sono diverse oppure sono finestre temporali diverse (es. "giornaliera",
        "mensile", "10 giorni")
        risposta corretta: {{"score": 1 o 2, "feedback": "Il testo estratto è riferito ad un'area geografica differente" o "le finestre temporali sono differenti"}}.

        Rispondi solo con formato JSON con la seguente struttura:
        {{
            "score": numero intero da 1 a 5,
            "feedback": breve descrizione della qualità del testo
        }} 
    """ 

    # invio i testi da analizzare
    user_msg = f"""
        ORA VALUTA I SEGUENTI TESTI
        testo estratto: {clean_parsed_text[:2000]}
        gold text: {clean_gold_text[:2000]}
    """

    msg_list = [
        {
            "role": "system",
            "content":sys_msg
        },
        {
            "role": "user",
            "content":user_msg
        }
    ]

    # payload della richiesta ad ollama
    payload = {
        "model": model_used,
        "messages": msg_list,
        "format":"json",
        "stream":False,
        "options":{"temperature":0.1}
    }


    # valori di default da restituire se la richiesta non va a buon fine
    final_score = 1
    final_feedback = "Impossibile valutare a causa di errori"

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status() # lancia un eccezione in automatico se trova codici di errore
        ris = response.json()
        
        msg_content = ris.get("message", {}).get("content", "{}")
        llm_response = json.loads(msg_content)

        score = llm_response.get("score")
        feedback = llm_response.get("feedback", "Nessun feedback generato")

        # controllo se il formato dello score è corretto, cioè se è un intero compreso tra 1 e 5
        if isinstance(score, int) and 1<=score<=5:
            final_score = score
            final_feedback = feedback
        else:
            final_feedback = f"Ollama ha restituito un voto non valido: {score}. Feedback: {feedback}"

    except requests.exceptions.RequestException as e:
        final_feedback = f"Errore durante la connessione ad Ollama: {str(e)}"

    except json.JSONDecodeError:
        final_feedback = f"Errore nella decodifica del json"

    except Exception as e:
        final_feedback = f"Errore: {str(e)}"

    return EvaluateJudgeOutputModel(
        model_name=model_used,
        judge_score=final_score,
        judge_feedback=final_feedback
    )


#GET/full_gs_eval
@app.get("/full_gs_eval")
def get_full_gs_eval(domain:str)->FullEvaluateModel:
    """"
        Restituisce l'intero gold standard del dominio dell'url in input
    """

    if(domain not in domains_list):
        raise HTTPException(status_code=404, detail="Dominio non supportato")

    parser_module = CUSTOM_PARSERS.get(domain, parser_wikipedia)
    file_name = domain_to_name_dict.get(domain)
    file_path = f"../../gs_data/{file_name}_gs.json"

    if not os.path.exists(file_path):
        raise HTTPException(status_code=500, detail="GS non trovato")
    
    with open(file_path,"r",encoding = 'UTF-8') as gs_json:
        gs_list = json.load(gs_json)


    count = 0
    precision = 0.0
    recall = 0.0
    f1 = 0.0


    for gs_elem_dict in gs_list:
        html = gs_elem_dict["html_text"]
        gs_text = gs_elem_dict["gold_text"]

        #in questo caso passiamo al parser sempre l'html che abbiamo associato al gs
        parser_result = asyncio.run(parser_module.extract(f"raw:{gs_elem_dict['html_text']}"))
        title = Cleaner.get_title_from_html(html)
        parsed_text = f"# {title}\n\n{parser_result['parsed']}"
        
        stats = TokenCompare.build_eval_from_parsed_gs_string(parsed_text, gs_text)

        precision += stats.get("precision", 0.0)
        recall += stats.get("recall", 0.0)
        f1 += stats.get("f1", 0.0)
        count += 1
        
    if count==0:
        final_stats = {
            "precision": 0.0,
            "recall": 0.0,
            "f1": 0.0
        }
    else:
        final_stats = {
            "precision":float(precision/count),
            "recall":float(recall/count),
            "f1":float(f1/count)
        }
        
    return FullEvaluateModel(token_level_eval=final_stats)


#POST/add_web_resource 
@app.post("/add_web_resource")
def add_web_rsrc_in_db(input:AddWebResourceInputModel)->AddOutputModel:
    """Aggiunge in web_resources i dati del body """   
    url = input.url
    html = input.html_text
    try:
        #ESTRAZIONE DOMINIO:
        domain = Cleaner.get_domain_from_url(url)

        #ESTRAZIONE TITOLO:
        #se non trova il titolo, il titolo sarà "Titolo sconosciuto"
        title = Cleaner.get_title_from_html(html) 

        execute_query(conn,"INSERT INTO web_resources (url, domain, title, html_text) VALUES (?,?,?,?)",(url,domain,title,html))

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")


    return AddOutputModel(status='ok')


#POST/add_gold_standard
@app.post("/add_gold_standard")
def add_web_rsrc_in_db(input:AddGoldStandardInputModel)->AddOutputModel:
    """Aggiunge in gold_standard i dati del body, solo se l'url è già in web_sources"""   
    url = input.url
    gold_text = input.gold_text
    try:
        execute_query(
            conn,
            "INSERT INTO gold_standard (url, gold_text) VALUES (?,?)",
            (url,gold_text)
        )
    except mariadb.IntegrityError as e:
        if e.errno == 1452:
            raise HTTPException(status_code=400, detail="Url assente in web_resources (FK-ERROR)")
        else:
            raise HTTPException(status_code=400, detail="Errore query")
    except Exception:
            raise HTTPException(status_code=400, detail = f"{e}")


    return AddOutputModel(status='ok')


#DELETE/web_resource
@app.delete("/web_resource")
def remove_web_rsrc_in_db(input:str)->AddOutputModel:
    """Cancella in web_resources le tuple con url in input """   
    url = input
    try:
        if(len(execute_query(conn,"SELECT url FROM web_resources WHERE url = ?",(url,)))==0):
            raise HTTPException(status_code=404, detail=f"url assente")
        execute_query(conn,"DELETE FROM web_resources WHERE url = ?",(url,))

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"{e}")

    return AddOutputModel(status='ok')


#DELETE/gold_standard
@app.delete("/gold_standard")
def remove_web_rsrc_in_db(input:str)->AddOutputModel:
    """Cancella da gold_standard la entry con url in input"""   
    url = input
    try:
        if(len(execute_query(conn,"SELECT url FROM gold_standard WHERE url = ?",(url,)))==0):
            raise HTTPException(status_code=404, detail=f"url assente")
        execute_query(
            conn,
            "DELETE FROM gold_standard WHERE url = ?",
            (url,)
        )
    except Exception as e:
            raise HTTPException(status_code=400, detail = f"{e}")
    return AddOutputModel(status='ok')


#GET/db_schema
@app.get("/db_schema")
def database_schema()->DBSchemaModel:
    """Ritorna lo schema del db"""
    web_schema = WebResourcesModel(
        url="varchar(768),PK",
        domain="varchar(255)",
        title = "varchar(500)",
        html_text = "longtext",
        created_at="datetime"
    )
    gold_schema = GoldStandardModelDB(
        url = "varchar(768),PK,FK(web_resources.url)",
        gold_text = "longtext",
        created_at="datetime"
    )
    return DBSchemaModel(
        web_resources=web_schema,
        gold_standard=gold_schema
        )


#GET/status
@app.get("/status")
def status_service()->StatusResponse: 
    try:
        conn.ping() 
        status["mariadb"] = True
    except mariadb.Error:
        status["mariadb"] = False 
    backend_status = "ok"
    db_status = "ok" if status.get("mariadb") else "error"
    
    OLLAMA_URL = "http://127.0.0.1:11434/"
    try:
        req = urllib.request.Request(OLLAMA_URL, method="HEAD") # chiede solo intestazione, quindi è più veloce di GET

        with urllib.request.urlopen(req, timeout=1) as response:    # se dopo 2 secondi non ha risposto allora è "error"
            if response.status==200:
                ollama_status = "ok"

    except Exception as e:
        ollama_status = "error"

    return StatusResponse(backend=backend_status,database=db_status,ollama=ollama_status)




#NON PIU USATA
# @app.get("/full_gold_standard")
# def get_full_gold_standard(domain:str)->FullGoldStandardModel:
#     """
#     Restituisce oggetto JSON contenente la lista degli elementi di un GS per un dominio specifico
#     """
#     if domain not in domains_list:
#         raise HTTPException(status_code=404, detail="Dominio non supportato")

#     file_name = domain_to_name_dict.get(domain)
#     file_path = f"../../gs_data/{file_name}_gs.json"

#     # if not os.path.exists(file_path):
#     #     raise HTTPException(status_code=500, detail=f"File {file_path} non trovato")

#     with open(file_path, "r", encoding="utf-8") as f:
#         gs_list = json.load(f)
#         return FullGoldStandardModel(gold_standard=gs_list)
#NON PIU USATA        

#endregion