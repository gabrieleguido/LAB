from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
from urllib.parse import urlparse,unquote
from token_compare import TokenCompare
import os
from typing import List
from bs4 import BeautifulSoup
from parser_nbcnews import extract
import parser_nbcnews
from cleaner import Cleaner
import asyncio
import crawler_test
app = FastAPI()

# Lista dei domini assegnati
domains_list = TokenCompare.get_domain_list()


# Modello di risposta per GET /domains
class DomainsListModel(BaseModel):
    domains: List[str]


# Modello di risposta per GET /gold_standard
class GoldStandardModel(BaseModel):
    url: str
    domain: str
    title: str
    html_text: str
    gold_text: str


# Modello di risposta per GET /full_gold_standard
class FullGoldStandardModel(BaseModel):
    gold_standard: List[GoldStandardModel]


# Modello di risposta per GET /parse
class ParserOutputModel(BaseModel):
    url:str
    title:str
    domain:str
    html_text:str
    parsed_text:str





@app.get("/domains")
def get_domains()->DomainsListModel:
    """
    Restituisce oggetto JSON contenente la lista dei domini assegnati
    """
    return DomainsListModel(domains=domains_list)



@app.get("/gold_standard/{url_in}")
def get_gold_standard(url_in: str)->GoldStandardModel:
    """
    Restituisce oggetto JSON contenente il gold standard del dominio in input
    """
    url = unquote(url_in)
    domain = Cleaner.get_domain_from_url(url)
    
    if domain not in domains_list:
        raise HTTPException(status_code=404, detail="Dominio non supportato")
    
    
    file_name = domain.split('.')[1]
    file_path = f"gs_data/{file_name}_gs.json"

    if not os.path.exists(file_path):
        raise HTTPException(status_code=500, detail=f"File {file_path} non trovato")

    with open(file_path, "r", encoding="utf-8") as f:
        try:
            gs_list = json.load(f)

            for gs in gs_list:
                if gs.get("url") in url:
                    return GoldStandardModel(**gs)
            raise HTTPException(status_code=404, detail="Url non trovato")
            
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="File json corrrotto")
        


@app.get("/full_gold_standard/{url_in}")
def get_full_gold_standard(url_in:str)->FullGoldStandardModel:
    """
    Restituisce oggetto JSON contenente la lista degli elementi di un GS per un dominio specifico
    """
    url = unquote(url_in)
    domain = Cleaner.get_domain_from_url(url)

    if domain not in domains_list:
        raise HTTPException(status_code=404, detail="Dominio non supportato")

    file_name = domain.split('.')[1]    
    file_path = f"gs_data/{file_name}_gs.json"

    if not os.path.exists(file_path):
        raise HTTPException(status_code=500, detail=f"File {file_path} non trovato")

    with open(file_path, "r", encoding="utf-8") as f:
        try:
            gs_list = json.load(f)
            return FullGoldStandardModel(gold_standard=gs_list)

        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="File json corrrotto")
        
# Mapping dominio -> funzione parser
CUSTOM_PARSERS = {
    "www.nbcnews.com": parser_nbcnews,
    "it.uefa.com": parser_nbcnews,
    "en.wikipedia.it":parser_nbcnews
}
@app.get("/parse/{url_in}")
def parse_url(url_in: str)->ParserOutputModel:
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
            result_dict = asyncio.run(parser_nbcnews.extract(url))
        else:
            raise HTTPException(status_code=404, detail="Dominio non supportato")
        # Estrazione titolo della pagina
        title = Cleaner.get_title_from_html(result_dict["html"])

        
        return ParserOutputModel(
            url=url,
            title = title,
            domain = domain,
            html_text = result_dict["html"],
            parsed_text = result_dict["parsed"]
            )
    except Exception as e:
        # Errore nel parser 
        raise HTTPException(status_code=500, detail=f"Errore interno del parser: {str(e)}")


