import json 
from typing import List,Dict,Set
from cleaner import Cleaner
import re 

class TokenCompare:
    @staticmethod
    def markdown_file_tokenizer(file_name:str,links_del_flag:bool=False,enc:str='UTF-8')->Set[str]:
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
                    token_set.add(w.lower())
        markdown_file.close()

        return token_set
    
    @staticmethod
    def gs_file_tokenizer(gs_file_name:str,url:str="",enc:str='UTF-8')->Set[str]:
        """Dato il nome del file del GS restituisce l'insieme dei token
            gs_file_name(str) = nome del file .json del gs 
            url(str) = url passato se si vuole solo il gs di un singolo url
                    NOTA: Assumiamo che l'url sia presente nel gs
            enc(str) = encoding del file
        """
        json_file = open(gs_file_name,'r',encoding=enc)
        json_list = json.load(json_file)
        token_set = set()
        for e in json_list:
            if(url and url != e.get("url")):
                continue
            golden_text = str(e.get("gold_text"))
            golden_text = re.sub(r'[^a-zA-Z0-9]',',',golden_text)
            golden_text = golden_text.split(",")
            for w in golden_text:
                if(w):
                    token_set.add(w.lower())
        return token_set
    
    @staticmethod
    def markdown_string_tokenizer(md_string:str)->Set[str]:
        """
            Data una stringa di testo parsato in markdown restituisce
            l'insieme di token da usare per la funzione di valutazione
        """
        parsed_text = re.sub(r'[^a-zA-Z0-9]',',',md_string)
        parsed_text = parsed_text.split(",")
        token_set = set()
        for w in parsed_text:
            if(w):
                token_set.add(w.lower())
        return token_set
    
    @staticmethod
    def gs_string_tokenizer(gs_string:str)->Set[str]:
        """
            Data una stringa di testo gs restituisce
            l'insieme di token da usare per la funzione di valutazione
        """
        golden_text = re.sub(r'[^a-zA-Z0-9]',',',gs_string)
        golden_text = golden_text.split(",")
        token_set = set()
        for w in golden_text:
            if(w):
                token_set.add(w.lower())
        return token_set

    
    @staticmethod
    def get_domain_list(domain_json_file:str="domains.json",enc:str='UTF-8')->List[str]:
        "restituisce la lista di domini presa dal file json"
        file = open(domain_json_file,"r",encoding=enc)
        domains_dict = json.load(file) 
        domains_list = domains_dict.get("domains")
        return domains_list
    
    @staticmethod
    def get_stats(markdown_tokens_set:Set[str],gs_tokens_set:Set[str])->Dict[str,float]:
        """
            Dati in input i due insiemi di token, resitituisce le statistiche
            markdown_tokens_set(set):risultato di Markdown_tokenizer
            gs_tokens_set(set):risultato di GS_tokenizer
        """
        stats = {} 
        stats["precision"] = float(len(gs_tokens_set&markdown_tokens_set)/len(markdown_tokens_set))
        stats["recall"] = float(len(gs_tokens_set&markdown_tokens_set)/len(gs_tokens_set))
        stats["f1"] = float(2*stats["precision"]*stats["recall"]/(stats["precision"]+stats["recall"]))
        return stats
    
    @staticmethod
    def build_eval_from_parsed_gs_string(md_string:str,gs_string:str,tokens_file:str="",print_stats_flag:bool=False,print_diff:bool=False)->Dict[str,float]:
        """
            Date le stringhe di testo parsato e di gold text in iput costruisce in 
            automatico le statistiche ritornate come dizionario:\n
                precision:float\n
                recall:float\n
                f1:float\n
            tokens_file(str) se inserito stampa i token sul file 
            di nome tokenfile\n
            print_stats_flag(bool) se impostato a true stampa le stats\n
            print_diff(bool): se impostato a true stampa il set differenza di token
        """
        md_set = TokenCompare.markdown_string_tokenizer(md_string)
        gs_set = TokenCompare.gs_string_tokenizer(gs_string)
        stats = TokenCompare.get_stats(md_set,gs_set)
        if(tokens_file):
            file = open(tokens_file,"w",encoding='UTF-8')
            file.write("MD tokens:\n"
                       +str(sorted(md_set))+"\n"
                       +"gs_set:\n"
                       +str(sorted(gs_set))
                       )
            file.close()
        
        if(print_diff):
            print("MD-GS")
            print(sorted(md_set-gs_set))
            print("GS-MD")
            print(sorted(gs_set-md_set))
            
        if(print_stats_flag):
            print("STATS:")
            print(stats["precision"])
            print(stats["recall"])
            print(stats["f1"])

        return stats
    
    @staticmethod
    
    



    

# url = "https://it.uefa.com/uefachampionsleague/news/02a4-2060af553568-cd2fcc38c28e-1000--anteprima-liverpool-paris-saint-germain-champions-league"
# gs_tokens = TokenCompare.GS_tokenizer("../GS/uefa/GS.json",url)
# parsed_tokens = TokenCompare.Markdown_tokenizer("crawler_result_test.md")
# ordered_gs = sorted(gs_tokens)
# ordered_parsed = sorted(parsed_tokens)
# stats = TokenCompare.get_stats(gs_tokens,parsed_tokens)
# for k in stats.keys():
#     print(stats[k])

# print(ordered_gs)
# print("\n\n\n")
# print(ordered_parsed)
# print("STATS:\n")
# precision = len(gs_tokens&parsed_tokens)/len(parsed_tokens)
# recall = len(gs_tokens&parsed_tokens)/len(gs_tokens)
# f1 = 2*precision*recall/(precision+recall)
# print(f"Precision = {precision},\nRecall = {recall},\nF1 = {f1}")

# print(TokenCompare.get_domain_list())

