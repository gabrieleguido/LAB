from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
from urllib.parse import urlparse
from token_compare import TokenCompare
import os
from typing import List
from bs4 import BeautifulSoup
import parser_nbcnews
import parser_uefa
import httpx
app = FastAPI()

# Lista dei domini assegnati
domains_list = TokenCompare.get_domain_list()

folder_map = {
    "en.wikipedia.org": domains_list[0].split(".")[1],
    "www.nbcnews.com": "nbcnews",
    "www.weather.com": "weather",
    "it.uefa.com": "uefa"
}

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
    url: str
    domain: str
    title: str
    html_text: str
    parsed_text: str



@app.get("/domains", response_model=DomainsListModel)
def get_domains()->DomainsListModel:
    """
    Restituisce oggetto JSON contenente la lista dei domini assegnati
    """
    return DomainsListModel(domains=domains_list)



@app.get("/gold_standard", response_model=GoldStandardModel)
def get_gold_standard(url: str)->GoldStandardModel:
    """
    Restituisce oggetto JSON contenente il gold standard del dominio in input
    """

    try:
        domain = TokenCompare.get_domain_from_url(url)
    except Exception:
        raise HTTPException(status_code=400, detail="Formato url non valido")
    
    if domain not in domains_list:
        raise HTTPException(status_code=404, detail="Dominio non supportato")
    
    file_name = folder_map[domain]
    file_path = f"gs_data/{file_name}_gs.json"

    if not os.path.exists(file_path):
        raise HTTPException(status_code=500, detail=f"File {file_path} non trovato")

    with open(file_path, "r", encoding="utf-8") as f:
        try:
            gs_list = json.load(f)

            for gs in gs_list:
                if gs.get("url") == url:
                    return GoldStandardModel(**gs)
            raise HTTPException(status_code=404, detail="Url non trovato")
            
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="File json corrrotto")
        


@app.get("/full_gold_standard", response_model=FullGoldStandardModel)
def get_full_gold_standard(domain:str)->FullGoldStandardModel:
    """
    Restituisce oggetto JSON contenente la lista degli elementi di un GS per un dominio specifico
    """
    
    if domain not in domains_list:
        raise HTTPException(status_code=404, detail="Dominio non supportato")

    file_name = folder_map[domain]    
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
    "it.uefa.com": parser_uefa
}
@app.get("/parse",response_model=ParserOutputModel)
async def parse_url(url: str)->ParserOutputModel:
    """
    Restituisce oggetto JSON contenente il risultato del parsing del testo di una pagina web
    """
    try:
        domain = TokenCompare.get_domain_from_url(url)
    except Exception:
        raise HTTPException(status_code=400, detail="Formato url non valido")
    
    if domain not in domains_list:
        raise HTTPException(status_code=404, detail="Dominio non supportato")
    
    if domain not in CUSTOM_PARSERS:
        raise HTTPException(status_code=500, detail="Funzione di parsing non trovata per il dominio")
    # 2. Fetch dell'HTML 
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            html_content = response.text
        except httpx.HTTPStatusError:
            raise HTTPException(status_code=404, detail="Pagina non trovata sul server remoto")
        except Exception:
            raise HTTPException(status_code=503, detail="Servizio di rete non disponibile")

    try:
        #chiamata alla funzione di parsing specifica per il dominio
        parser_module = CUSTOM_PARSERS[domain]
        parsed_result = await parser_module.extract(url)
        # Estrazione titolo della pagina
        soup = BeautifulSoup(html_content, 'html.parser')
        title = soup.title.string if soup.title else "Titolo non trovato"
        
        return {
            "url": url,
            "domain": domain,
            "title": title,
            "html_text": html_content,
            "parsed_text": parsed_result
        }
    except Exception as e:
        # Errore nel parser 
        raise HTTPException(status_code=500, detail=f"Errore interno del parser: {str(e)}")


