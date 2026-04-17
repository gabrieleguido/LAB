import json 
from typing import List,Dict,Set
from parse_cleaner import ParseCleaner
import re 

class TokenCompare:
    @staticmethod
    def Markdown_tokenizer(file_name:str,links_del_flag:bool=False,enc:str='UTF-8')->Set[str]:
        """
            Dato il nome di un file .md restituisce l'insieme dei token puliti.
            file_name(str) = nome del markdown 
            links_del_flag(bool) = True per eliminare anche i link
            enc(str) = encoding del file 
        """
        markdown_file = open(file_name,"r",encoding=enc)

        token_set = set()

        for line in markdown_file:
            if(links_del_flag):
                #elimino link
                line = re.sub(r'\(\s*https?://[^)]*\)',' ',line)
            #elimino le note []
            line = re.sub(r'\[\[\d+\]\]',' ',line)
            #elimino caratteri non alfanumerici
            line = re.sub(r'[^a-zA-Z0-9]',' ',line)
            line = line.split(" ")
            for w in line:
                if(w):
                    token_set.add(w)
        markdown_file.close()

        return token_set
    
    @staticmethod
    def GS_tokenizer(gs_file_name:str,enc:str='UTF-8')->Set[str]:
        """Dato il nome del file del GS restituisce l'insieme dei token
            gs_file_name(str) = nome del file .json del gs 
            enc(str) = encoding del file
        """
        json_file = open(gs_file_name,'r',encoding=enc)
        json_list = json.load(json_file)
        token_set = set()
        for e in json_list:
            golden_text = str(e.get("gold_text"))
            golden_text = re.sub(r'[^a-zA-Z0-9]',',',golden_text)
            golden_text = golden_text.split(",")
            for w in golden_text:
                if(w):
                    token_set.add(w)
        return token_set
    
    @staticmethod
    def get_domain_list(domain_json_file:str="domains.json",enc:str='UTF-8')->List[str]:
        file = open(domain_json_file,"r",encoding=enc)
        domains_dict = json.load(file) 
        domains_list = domains_dict.get("domains")
        return domains_list
    
    @staticmethod 
    def get_domain_from_url(url:str)->str:
        """
            Restituisce il dominio estratto dalla stringa url
        """
        line = url.split('/')
        return line[2]

# gs_tokens = TokenCompare.GS_tokenizer("../GS/nbcnews/GS.json")
# parsed_tokens = TokenCompare.Markdown_tokenizer("crawler_result_test.md")
# ordered_gs = sorted(gs_tokens)
# ordered_parsed = sorted(parsed_tokens)

# print(ordered_gs)
# print("\n\n\n")
# print(ordered_parsed)
# print("STATS:\n")
# precision = len(gs_tokens&parsed_tokens)/len(parsed_tokens)
# recall = len(gs_tokens&parsed_tokens)/len(gs_tokens)
# f1 = 2*precision*recall/(precision+recall)
# print(f"Precision = {precision},\nRecall = {recall},\nF1 = {f1}")

# print(TokenCompare.get_domain_list())

