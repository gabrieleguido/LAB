from pydantic import BaseModel
from typing import Dict, List
from typing import List,Tuple, Optional 


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

#modello per stats
class StatsModelDB(BaseModel):
    """url:str\n
    prec:str\n
    rec:str\n
    f1:str \n
    score:str\n
    created_at:str
 """
    url:str
    prec:str
    rec:str
    f1:str 
    score:str 
    created_at:str

#modello di risposta della GET/db_schema
class DBSchemaModel(BaseModel):
    """web_resources:WebResourcesModel\n
    gold_standard:GoldStandardModelDB"""
    web_resources:WebResourcesModel
    gold_standard:GoldStandardModelDB
    stats:StatsModelDB


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

#modello di risposta di GET/db_stats
class DBStatsModel(BaseModel):
    """ 
     web_resources:Dict[str,int]\n
    gold_standard:Dict[str,int]\n
    avg_eval:Dict[str,Dict[str,Dict[str,float]]]\n
    avg_judge_score:Dict[str,Dict[str,float]]
    
    """
    web_resources:Dict[str,int] 
    gold_standard:Dict[str,int]
    avg_eval:Dict[str,Dict[str,Dict[str,float]]]
    avg_eval_judge:Dict[str,Dict[str,float]]
    
    
    
