from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
from urllib.parse import urlparse,unquote
from token_compare import TokenCompare
import os
from typing import List,Dict 
import parser_wikipedia as parser_wikipedia
from cleaner import Cleaner
import asyncio

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





@app.get("/domains")
def get_domains()->DomainsListModel:
    """
    Restituisce oggetto JSON contenente la lista dei domini assegnati
    """
    return DomainsListModel(domains=domains_list)



@app.get("/gold_standard/{url_in:path}")
def get_gold_standard(url_in: str)->GoldStandardModel:
    """
    Restituisce oggetto JSON contenente il gold standard del dominio in input
    """
    url = unquote(url_in)
    domain = Cleaner.get_domain_from_url(url)
    
    if domain not in domains_list:
        raise HTTPException(status_code=404, detail="Dominio non supportato")
    
    
    file_name = domain_to_name_dict[domain]
    file_path = f"../../gs_data/{file_name}_gs.json"

    # if not os.path.exists(file_path):
    #     raise HTTPException(status_code=500, detail=f"File {file_path} non trovato")

    with open(file_path, "r", encoding="utf-8") as f:
        try:
            gs_list = json.load(f)
            for gs in gs_list:
                if gs.get("url") in url:
                    return GoldStandardModel(
                        url=gs.get("url"),
                        domain=gs.get("domain"),
                        title = gs.get("title"),
                        html_text=gs.get("html_text"),
                        gold_text=gs.get("gold_text")
                        )
            raise HTTPException(status_code=404, detail="Url non trovato")
            
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="File json corrrotto")
        


@app.get("/full_gold_standard")
def get_full_gold_standard(url:str)->FullGoldStandardModel:
    """
    Restituisce oggetto JSON contenente la lista degli elementi di un GS per un dominio specifico
    """
    # url = unquote(url)
    domain = Cleaner.get_domain_from_url(url)

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
    "www.nbcnews.com": parser_wikipedia,
    "it.uefa.com": parser_wikipedia,
    "en.wikipedia.it":parser_wikipedia
}
@app.get("/parse/{url_in:path}")
def parse_url(url_in: str)->ParseOutputModel:
    """
    Restituisce oggetto JSON contenente il risultato del parsing del testo di una pagina web
    """
    url = unquote(url_in)
    try:
        domain = Cleaner.get_domain_from_url(url)
    except Exception:
        raise HTTPException(status_code=400, detail="Formato url non valido")
    
    if domain not in domains_list:
        raise HTTPException(status_code=404, detail="Dominio non supportato")
    

    try:
        #chiamata alla funzione di parsing specifica per il dominio

        #parser_module = CUSTOM_PARSERS[domain]
        
        domain=Cleaner.get_domain_from_url(url)

        if(domain in ["en.wikipedia.org","www.nbcnews.com","it.uefa.com"]):
            result_dict = asyncio.run(parser_wikipedia.extract(url))
        else:
            raise HTTPException(status_code=404, detail="Dominio non supportato")
        # Estrazione titolo della pagina
        title = Cleaner.get_title_from_html(result_dict["html"])

        
        return ParseOutputModel(
            url=url,
            domain = domain,
            title = title,
            html_text = result_dict["html"],
            parsed_text = result_dict["parsed"]
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

    url = unquote(input.url)
    domain = Cleaner.get_domain_from_url(url)
    if(domain not in domains_list):
        raise HTTPException(status_code=404, detail="Dominio non supportato")
    html = input.html_text 

    #impongo al crawler di parsare l'html che gli passo in url
    url = f'raw:{html}'

    if(domain in ["en.wikipedia.org","www.nbcnews.com","it.uefa.com"]):
        result_dict = asyncio.run(parser_wikipedia.extract(url))
    else:
        raise HTTPException(status_code=404, detail="Parser non implementato")


    return ParseOutputModel(
            url=unquote(input.url),
            domain = domain,
            title = Cleaner.get_title_from_html(html),
            html_text = result_dict["html"],
            parsed_text = result_dict["parsed"]
         )

@app.get("/full_gs_eval/{url_in:path}")
def get_full_gs_eval(url_in:str)->EvaluateOutputModel:
    """"
        Restituisce l'intero gold standard del dominio dell'url in input
    """

    url = unquote(url_in)
    domain = Cleaner.get_domain_from_url(url)
    if(domain not in domains_list):
        raise HTTPException(status_code=404, detail="Dominio non supportato")

    file_name = domain_to_name_dict[domain]
    count = 0
    precision = float()
    recall = float()
    f1 = float()
    with open(f"../../gs_data/{file_name}_gs.json","r",encoding = 'UTF-8') as gs_json:
        gs_list = json.load(gs_json)
    for gs_elem_dict in gs_list:
        if(domain in ["en.wikipedia.org","www.nbcnews.com","it.uefa.com"]):
            #in questo caso passiamo al parser sempre l'html che abbiamo associato al gs
            parser_result = asyncio.run(parser_wikipedia.extract(f"raw:{gs_elem_dict['html_text']}"))
            parsed_text = parser_result["parsed"]
            gs_text = gs_elem_dict["gold_text"]
            stats = TokenCompare.build_eval_from_parsed_gs_string(parsed_text,gs_text)
            precision += stats["precision"]
            recall += stats["recall"]
            f1 += stats["f1"]
            count += 1
        else:
            raise HTTPException(status_code=404, detail="Parser non implementato")
        
        final_stats = {
            "precision":float(precision/count),
            "recall":float(recall/count),
            "f1":float(recall/count)
           }
        return EvaluateOutputModel(token_level_eval=final_stats)
        
    

