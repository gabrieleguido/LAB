from pydantic import BaseModel
import re 

class Cleaner(BaseModel):
    @staticmethod
    def parsed_clean_to_file(file_name_src:str,file_name_dst:str,enc:str,link_del_flag:bool=False)->None:
        """
            Scrive nel file di output il testo markdown preso in input pulito
            Argomenti:
                file_name_src(str):Nome file del markdown da pulire
                file_name_dst(str):Nome file destinazione del testo pulito
                enc(str):Encoding dei file 
                link_del_flag(bool): True per eliminare i link
        """
        markdown_file = open(file_name_src,"r",encoding=enc)
        clean_file = open(file_name_dst,"w",encoding=enc)
        for line in markdown_file:
            if(link_del_flag):
                line = re.sub(r'\(\s*https?://[^)]*\)',' ',line)
            #elimino le note []
            line = re.sub(r'\[\[\d+\]\]',' ',line)
            line = re.sub(r'[^a-zA-Z0-9]',' ',line)
        markdown_file.close()
        clean_file.close()
    
    @staticmethod
    def parsed_clean_to_string(markdown:str)->str:
        """Data la stringa markdown in input restituisce la stringa
            markdown pulita
        """
        #regex per le note []
        cleaned = re.sub(r'\[\[\d+\]\]',' ',markdown)
        #regex per le #cite_note...
        cleaned = re.sub(r'#cite_note[^)]*\)'," ",cleaned)
        #regex per caratteri non alfanumerici
        cleaned = re.sub(r'[^a-zA-Z0-9]',' ',cleaned)
        return cleaned
    
    
    @staticmethod
    def get_title_from_html(html_text:str)->str:
        """Restiuisce il titolo preso dall html_text"""
        match = re.search(r"<title>(.*?)</title>",html_text)
        if(match):
            return match.group(1)
        else:
            return "Titolo sconosciuto"
        
    @staticmethod 
    def get_domain_from_url(url:str)->str:
        """
            Restituisce il dominio estratto dalla stringa url
        """
        line = url.split('/')
        return line[2]

    
        
