from pydantic import BaseModel
import re 
import mistune
from bs4 import BeautifulSoup

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
    def parsed_clean_to_string(markdown:str,is_weather:bool=False)->str:
        """Data la stringa markdown in input restituisce la stringa
            markdown pulita, se imposti is_weather a true fa le magie su weather
        """
        
        #regex per i link
        cleaned = re.sub(r'\(\s*https?://[^)]*\)',' ',markdown)
        #regex per le note []
        cleaned = re.sub(r'\[\[\d+\]\]',' ',cleaned)
        #regex per le #cite_note...
        cleaned = re.sub(r'#cite_note[^)]*\)'," ",cleaned)


        #IF E CORPO GENERATI DA GEMMINI!!!!
        if(is_weather):
            # 1. TRATTAMENTO PREVENTIVO SIMBOLI FUSI
            # Sostituiamo ° e % con uno spazio PRIMA di toccare il resto, 
            # così "Percepiti18°" diventa "Percepiti18 " e "Umidità74%" diventa "Umidità74 "
            cleaned = cleaned.replace("°", " ").replace("%", " ")

            # 2. SEPARAZIONE PAROLA-NUMERO (es. Percepiti18 -> Percepiti 18, coperto57 -> coperto 57)
            # Cerca una lettera minuscola seguita direttamente da un numero
            cleaned = re.sub(r'([a-z])(\d)', r'\1 \2', cleaned)
            
            # Cerca un numero seguito direttamente da una lettera minuscola (es. 0mm -> 0 mm)
            cleaned = re.sub(r'(\d)([a-z])', r'\1 \2', cleaned)

            # 3. SEPARAZIONE DEL VENTO (es. VentoNE -> Vento NE, VentoENE -> Vento ENE)
            # Separa la parola 'Vento' se attaccata a una direzione maiuscola
            cleaned = re.sub(r'(Vento)([A-Z])', r'\1 \2', cleaned)
            # Separa una lettera minuscola da una sigla di vento maiuscola (es. chilometri fusi: km/hNE -> km/h NE)
            cleaned = re.sub(r'([a-z])([A-Z]{1,3}\b)', r'\1 \2', cleaned)        
        


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
    
    @staticmethod
    def remove_markdown(md:str)->str:
        """
            Rimuove il markdown da una stringa restituendo il testo pulito
        """
        html = mistune.html(md)
        soup = BeautifulSoup(html,"html.parser")
        for tag in soup.find_all(True):
            tag.unwrap()
        text = re.sub(r'[\t]'," ",str(soup))
        text = re.sub(r'\n+','\n',text)
        return text.strip()


    
        
