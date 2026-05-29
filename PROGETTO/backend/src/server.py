import time

from fastapi import FastAPI, HTTPException
import requests
import json
from urllib.parse import urlparse,unquote
import urllib.request
from pydantic_models import StatsModelDB,AddGoldStandardInputModel, AddOutputModel, AddWebResourceInputModel, DBSchemaModel, DBStatsModel, DomainsListModel, EvaluateInputModel, EvaluateJudgeOutputModel, EvaluateOutputModel, FullEvaluateModel, GoldStandardModel, GoldStandardModelDB, GoldStandardUrlsOutputModel, ParseOutputModel, PostParseInputModel, StatusResponse, WebResourcesModel
from token_compare import TokenCompare
import os
from typing import List,Tuple, Optional 
import parser_wikipedia as parser_wikipedia
import parser_nbcnews as parser_nbcnews
import parser_uefa as parser_uefa
import parser_weather as parser_weather
from cleaner import Cleaner
import asyncio
import mariadb
from populate_db import Populator

DEBUG = 1
status_mariadb = {"mariadb":False}

#region MARIADB & OLLAMA SETUP


#url ollama e modello 
OLLAMA_URL = "http://ollama:11434/api/chat"
OLLAMA_MODEL = "llama3.2:3b"
OLLAMA_MAX_CHARS = 2000

#funzione per le query
def execute_query(conn:mariadb.Connection,query:str,param:Tuple=None)->List[Tuple[str]]:
    """funzione per eseguire le query che ritorna una lista di tuple (di stringhe).
    Ha un parametro opzionale con la tupla della query parametrizzata"""
    try:
        conn.ping()
    except:
        conn = create_connection(conn)    
    with conn.cursor() as cursor:
        cursor.execute(query,param)
        conn.commit()
        #Se la query non seleziona, ritorno una lista vuota
        if cursor.description is None:
            return []
        result = cursor.fetchall()
        return result
    
#funzione per la connessione
def create_connection(conn:mariadb.Connection)->mariadb.Connection:
    if conn is not None:
        try:
            conn.close() 
        except:
            pass
    return mariadb.connect(
        host = "db",
        port = 3306,
        user = "backend_user",
        password = "backend_password",
        database = "lab_db"
    )   


#connessione al db 
conn = None
# conn = create_connection(conn)

# cnt = 10
# while cnt:
#     try:
#         conn.ping() 
#         cnt = 0
#     except:
#         conn = create_connection(conn)
#         cnt-=1 
#         time.sleep(5)

for i in range(10):
    try:
        conn = create_connection(conn)
        conn.ping()
        break
    except mariadb.Error as e:
        time.sleep(5)
    
        



#POPOLAZIONE DB (solo se db vuoto)
if(len(execute_query(conn,"SELECT url FROM web_resources"))==0):
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
        markdown_txt = result_dict.get("parsed")

        return ParseOutputModel(
                url=unquote(input.url),
                domain = domain,
                title = title,
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
    try:
        domain = Cleaner.get_domain_from_url(url_pulito)
    except:
        raise HTTPException(status_code=404, detail="Url non valido")

    
    if domain not in domains_list:
        raise HTTPException(status_code=404, detail="Dominio non supportato")
    
    
    res = execute_query(conn,"select w.url,w.domain,w.title,w.html_text,g.gold_text from "
        "web_resources as w join gold_standard as g on w.url = g.url "
        "where w.url = ? ",(url,))
    if res:
        gs = res[0]
        return GoldStandardModel(url = gs[0],
                                domain=gs[1],
                                title=gs[2],
                                html_text=gs[3],
                                gold_text=gs[4]
                                )
    else:
        raise HTTPException(status_code=404, detail="GS non disponibile")



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
            model_name=f"{OLLAMA_MODEL}",
            judge_score=1,
            judge_feedback="Impossibile valutare, i testi sono vuoti"
        )

    
    model_used = f"{OLLAMA_MODEL}"

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
        testo estratto: {clean_parsed_text[:OLLAMA_MAX_CHARS]}
        gold text: {clean_gold_text[:OLLAMA_MAX_CHARS]}
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
        Restituisce le valutazioni token_level e llm_score del gold standar relativo al dominio in input
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
    score = 0.0


    for gs_elem_dict in gs_list:
        html = gs_elem_dict["html_text"]
        gs_text = gs_elem_dict["gold_text"]

        #in questo caso passiamo al parser sempre l'html che abbiamo associato al gs
        parser_result = asyncio.run(parser_module.extract(f"raw:{html}"))
        parsed_text = parser_result.get("parsed")

        try:
            judge_res = judge(EvaluateInputModel(parsed_text=parsed_text,gold_text=gs_text))
            score += judge_res.judge_score 
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Errore nella richiesta al modello llm: {e}")
                    
        stats = TokenCompare.build_eval_from_parsed_gs_string(parsed_text, gs_text)

        precision += stats.get("precision", 0.0)
        recall += stats.get("recall", 0.0)
        f1 += stats.get("f1", 0.0)
        count += 1
        if DEBUG and count >= 4:
            break 
        
    if count==0:
        final_stats = {
            "precision": 0.0,
            "recall": 0.0,
            "f1": 0.0
        }
        score = 0
    else:
        final_stats = {
            "precision":float(precision/count),
            "recall":float(recall/count),
            "f1":float(f1/count)
        }
        score = float(score/count)
        
    return FullEvaluateModel(token_level_eval=final_stats,judge_score=score)


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
        return AddOutputModel(status="error")


    return AddOutputModel(status='ok')


#POST/add_gold_standard
@app.post("/add_gold_standard")
def add_gs_in_db(input:AddGoldStandardInputModel)->AddOutputModel:
    """Aggiunge in gold_standard i dati del body, solo se l'url è già in web_sources"""   
    url = input.url
    gold_text = input.gold_text
    try:
        execute_query(
            conn,
            "INSERT INTO gold_standard (url, gold_text) VALUES (?,?)",
            (url,gold_text)
        )
    # except mariadb.IntegrityError as e:
    #     if e.errno == 1452:
    #         raise HTTPException(status_code=400, detail="Url assente in web_resources (FK-ERROR)")
    #     else:
    #         raise HTTPException(status_code=400, detail="Errore query")
    except Exception:
        return AddOutputModel(status="error")

    return AddOutputModel(status='ok')


#DELETE/web_resource
@app.delete("/web_resource")
def remove_web_rsrc_in_db(url:str)->AddOutputModel:
    """Cancella in web_resources le tuple con url in input """   
    status_str = ""
    try:
        # if(len(execute_query(conn,"SELECT url FROM web_resources WHERE url = ?",(url,)))==0):
        #     return AddOutputModel(status="error")
        execute_query(conn,"DELETE FROM web_resources WHERE url = ?",(url,))
        status_str = "ok"
    except:
        status_str = "error"

    return AddOutputModel(status=status_str)


#DELETE/gold_standard
@app.delete("/gold_standard")
def remove_gs_in_db(url:str)->AddOutputModel:
    """Cancella da gold_standard la entry con url in input"""   
    status_str = ""
    try:
        # if(len(execute_query(conn,"SELECT url FROM gold_standard WHERE url = ?",(url,)))==0):
        #     return AddOutputModel(status="error")
        execute_query(
            conn,
            "DELETE FROM gold_standard WHERE url = ?",
            (url,)
        )
        status_str = "ok"
    except:
        status_str = "error"
    return AddOutputModel(status=status_str)


#GET/db_stats
@app.get("/db_stats")
def database_stats()->DBStatsModel:
    web_res_dict = {}
    gold_std_dict = {}
    avg_eval_dict = {}
    avg_eval_judge_dict = {} 
    
    try:
        #conteggio web resources per dominio
        q_web = "SELECT domain, COUNT(*) FROM web_resources GROUP BY domain"
        web_stats = execute_query(conn, q_web)
        for row in web_stats:
            web_res_dict[row[0]] = row[1]
            
        #conteggio gold standard per dominio
        q_gold = "SELECT w.domain, COUNT(g.url) FROM gold_standard AS g JOIN web_resources AS w ON g.url = w.url GROUP BY w.domain"
        gold_stats = execute_query(conn, q_gold)
        for row in gold_stats:
            gold_std_dict[row[0]] = row[1]
            
        #media valutazione token level per dominio
        q_eval = """
            SELECT 
                w.domain,     -- index 0
                AVG(s.f1),    -- index 1
                AVG(s.prec),  -- index 2
                AVG(s.rec),   -- index 3
                AVG(s.score)  -- index 4
            FROM web_resources w 
            LEFT JOIN stats s ON s.url = w.url 
            GROUP BY w.domain;

            """
        eval_stats = execute_query(conn, q_eval)
        for row in eval_stats:
            domain = row[0] if row[0] is not None else "unknown_domain"
            avg_f1 = row[1] if row[1] is not None else 0.0
            avg_prec = row[2] if row[2] is not None else 0.0
            avg_rec = row[3] if row[3] is not None else 0.0
            avg_judge = row[4] if row[4] is not None else 0.0
            
            avg_eval_dict[domain] = {
                "token_level_eval": {
                    "f1": round(avg_f1, 2),
                    "precision": round(avg_prec, 2),
                    "recall": round(avg_rec, 2) 
                }
            }
            
            avg_eval_judge_dict[domain] = {
                "judge_score": round(avg_judge, 2)
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nel recupero delle statistiche: {e}")
    return DBStatsModel(
            web_resources=web_res_dict,
            gold_standard=gold_std_dict,
            avg_eval=avg_eval_dict,
            avg_eval_judge=avg_eval_judge_dict
        )    
  
    
            
            
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
    stats_schema = StatsModelDB(
        url = "varchar(768),PK,FK(web_resources.url)",
        prec = "float",
        rec = "float",
        f1 = "float",
        score="int",
        created_at="datetime"
    )
    return DBSchemaModel(
        web_resources=web_schema,
        gold_standard=gold_schema,
        stats=stats_schema
        )


#GET/status
@app.get("/status")
def status_service()->StatusResponse: 
    backend_status = "ok"

    local_conn = None

    try:
        local_conn = create_connection(local_conn)
        local_conn.ping()
        db_status = "ok"
    except mariadb.Error:
        db_status = "error"
    finally:
        try:
            local_conn.close()
        except:
            pass 
    
    OLLAMA_STATUS_URL = "http://ollama:11434/"
    try:
        # richiesta con metodo "head" per la sola intestazione. attende 1 secondo dopo l'invio della richiesta prima di proseguire
        response = requests.head(OLLAMA_STATUS_URL, timeout=1) 
        response.raise_for_status()
        ollama_status = "ok"

    except requests.exceptions.RequestException as e:
        ollama_status = "error"
    except Exception as e:
        ollama_status = "error"

    return StatusResponse(backend=backend_status,database=db_status,ollama=ollama_status)

#GET/extract_stats
@app.get("/extract_stats")
def extract_stats_for_gs(name:str)->AddOutputModel:
    """Funzione per estrarre le stats in un file 
    """
    file_name = f"{name}_stats.txt"
    with open(file_name,"w",encoding="UTF-8") as out_text:
        count = 0
        file_path = f"../../gs_data/{name}_gs.json"
        with open(file_path,"r",encoding="UTF-8") as gs_json:
            gs_list = json.load(gs_json)
            for gs_entry in gs_list:

                parser_res = parse_html(PostParseInputModel(url=gs_entry.get("url"),local=True))
                parsed_text = parser_res.parsed_text 
                gold_text = gs_entry.get("gold_text")

                eval_res = evaluate(EvaluateInputModel(parsed_text=parsed_text,gold_text=gold_text))
                stats_dict = eval_res.token_level_eval 
                url = gs_entry.get("url")
                precision = stats_dict.get("precision")
                recall = stats_dict.get("recall")
                f1 = stats_dict.get("f1")
                
                score = 0.0

                try:
                    judge_res = judge(EvaluateInputModel(parsed_text=parsed_text,gold_text=gold_text))
                    score = judge_res.judge_score 
                except Exception as e:
                    raise HTTPException(status_code=404, detail=f"Errore nella richiesta al modello llm: {e}")
                            
                print(f"score{score}\nCOUNT:{count}")
                out_text.write(f"{url},{precision},{recall},{f1},{score}\n")
                count += 1

    return AddOutputModel(status="ok")

              

#endregion