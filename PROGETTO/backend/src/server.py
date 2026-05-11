from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
from urllib.parse import urlparse,unquote
from token_compare import TokenCompare
import os
from typing import List,Dict,Tuple 
import parser_wikipedia as parser_wikipedia
import parser_nbcnews as parser_nbcnews
import parser_uefa as parser_uefa
import parser_weather as parser_weather
from cleaner import Cleaner
import asyncio
import mariadb


#connessione al db 
conn = mariadb.connect(
    host = "127.0.0.1",
    port = 3306,
    user = "backend_user",
    password = "backend_password",
    database = "lab_db"
)

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
        html_text:str
    """
    url:str
    html_text:str

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
class GoldStandardModel(BaseModel):
    """url:str\n
    gold_text:str\n
    created_at:str"""
    url:str
    gold_text:str
    created_at:str


#modello di risposta della GET/db_schema
class DBSchemaModel(BaseModel):
    """web_resources:WebResourcesModel\n
    gold_standard:GoldStandardModel"""
    web_resources:WebResourcesModel
    gold_standard:GoldStandardModel

@app.get("/domains")
def get_domains()->DomainsListModel:
    """
    Restituisce oggetto JSON contenente la lista dei domini assegnati
    """
    return DomainsListModel(domains=domains_list)



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
        


@app.get("/full_gold_standard")
def get_full_gold_standard(domain:str)->FullGoldStandardModel:
    """
    Restituisce oggetto JSON contenente la lista degli elementi di un GS per un dominio specifico
    """
    if domain not in domains_list:
        raise HTTPException(status_code=404, detail="Dominio non supportato")

    file_name = domain_to_name_dict.get(domain)
    file_path = f"../../gs_data/{file_name}_gs.json"

    # if not os.path.exists(file_path):
    #     raise HTTPException(status_code=500, detail=f"File {file_path} non trovato")

    with open(file_path, "r", encoding="utf-8") as f:
        gs_list = json.load(f)
        return FullGoldStandardModel(gold_standard=gs_list)
        
# Mapping dominio -> funzione parser
CUSTOM_PARSERS = {
    "www.nbcnews.com": parser_nbcnews,
    "it.uefa.com": parser_uefa,
    "en.wikipedia.it":parser_wikipedia,
    "weather.com": parser_weather
}
@app.get("/parse")
def parse_url(url: str)->ParseOutputModel:
    """
    Restituisce oggetto JSON contenente il risultato del parsing del testo di una pagina web
    """
    url_dec = unquote(url).strip()
    try:
        domain = Cleaner.get_domain_from_url(url_dec)
    except Exception:
        raise HTTPException(status_code=400, detail="Formato url non valido")
    
    if domain not in domains_list:
        raise HTTPException(status_code=404, detail="Dominio non supportato")
    

    try:
        #chiamata alla funzione di parsing specifica per il dominio

        parser_module = CUSTOM_PARSERS.get(domain, parser_wikipedia)

        result_dict = asyncio.run(parser_module.extract(url_dec))

        # Estrazione titolo della pagina
        title = Cleaner.get_title_from_html(result_dict["html"])

        #testo markdown
        markdown_txt = f"# {title}\n\n{result_dict['parsed']}"
        
        return ParseOutputModel(
            url=url_dec,
            domain = domain,
            title = title,
            html_text = result_dict["html"],
            parsed_text = markdown_txt
        )
    except Exception as e:
        # Errore nel parser 
        raise HTTPException(status_code=500, detail=f"Errore interno del parser: {str(e)}")

@app.post("/evaluate")
def evaluate(input_item:EvaluateInputModel)->EvaluateOutputModel:
    """
        Restituisce le valutazioni per un testo parsato e il suo gs passati nel body
    """
    #prendo il dizionario con le statistiche di token evaluation, 
    #vedere TokenCompare per i dettagli
    stats = TokenCompare.build_eval_from_parsed_gs_string(input_item.parsed_text,input_item.gold_text,print_stats_flag=True)
    return EvaluateOutputModel(token_level_eval=stats)


@app.post("/parse")
def parse_html(input:PostParseInputModel)->ParseOutputModel:
    """
        Riceve in input un url e un html e restituisce :\n
        url\n
        dominio\n
        titolo (estratto dall'html)\n
        testo html\n
        testo risultato del parser
    """

    url_orig = unquote(input.url).strip()
    domain = Cleaner.get_domain_from_url(url_orig)
    
    if(domain not in domains_list):
        raise HTTPException(status_code=404, detail="Dominio non supportato")
    
    html = input.html_text 

    #impongo al crawler di parsare l'html che gli passo in url
    url_pars = f'raw:{html}'

    try:
        parser_module = CUSTOM_PARSERS.get(domain, parser_wikipedia)
        result_dict = asyncio.run(parser_module.extract(url_pars))
        title = Cleaner.get_title_from_html(html)

        markdown_txt = f"# {title}\n\n{result_dict['parsed']}"

        return ParseOutputModel(
                url=unquote(input.url),
                domain = domain,
                title = Cleaner.get_title_from_html(html),
                html_text = result_dict["html"],
                parsed_text = markdown_txt
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore: {str(e)}")

@app.get("/full_gs_eval")
def get_full_gs_eval(domain:str)->EvaluateOutputModel:
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
        
    return EvaluateOutputModel(token_level_eval=final_stats)
        
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
    gold_schema = GoldStandardModel(
        url = "varchar(768),PK,FK(web_resources.url)",
        gold_text = "longtext",
        created_at="datetime"
    )
    return DBSchemaModel(
        web_resources=web_schema,
        gold_standard=gold_schema
        )


