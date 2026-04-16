from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
from urllib.parse import urlparse
import os

app = FastAPI()

# Lista dei domini assegnati
domains_list = ["en.wikipedia.org", "www.nbcnews.com", "www.weather.com", "www.uefa.com"]

folder_map = {
    "en.wikipedia.org": "wikipedia",
    "www.nbcnews.com": "nbcnews",
    "www.weather.com": "weather",
    "www.uefa.com": "uefa"
}

# Modello di risposta per GET /domains
class DomainsModel(BaseModel):
    domains: list[str]

class GsModel(BaseModel):
    url: str
    domain: str
    title: str
    html_text: str
    gold_text: str




@app.get("/domains", response_model=DomainsModel)
async def get_domains()->json:
    """
    Restituisce oggetto JSON contenente la lista dei domini assegnati
    """
    return {"domains": domains_list}


@app.get("/gold_standard", response_model=GsModel)
async def get_gold_standard(url: str)->json:
    """
    Restituisce oggetto JSON contenente un gold standard del dominio in input
    """

    try:
        domain = urlparse(url).netloc
    except Exception:
        raise HTTPException(status_code=400, detail="Formato url non valido")
    
    if domain not in domains_list:
        raise HTTPException(status_code=404, detail="Dominio non supportato")
    
    folder_name = folder_map[domain]
    file_path = f"GS/{folder_name}/GS.json"

    if not os.path.exists(file_path):
        raise HTTPException(status_code=500, detail=f"File {file_path} non trovato")

    with open(file_path, "r", encoding="utf-8") as f:
        try:
            gs_list = json.load(f)

            if len(gs_list)>0:
                return gs_list[0]
            else:
                raise HTTPException(status_code=404, detail="Gs list vuota")
            
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="File json corrrotto")
    