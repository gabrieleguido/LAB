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
    def parsed_clean_to_string(markdown:str)->str:
        """Data la stringa markdown in input restituisce la stringa
            markdown pulita
        """
        #regex per i link
        cleaned = re.sub(r'\(\s*https?://[^)]*\)',' ',markdown)
        #regex per le note []
        cleaned = re.sub(r'\[\[\d+\]\]',' ',cleaned)
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


    
        
class WeatherCleaner(Cleaner):
    @staticmethod
    def clean_weather_html(cleaned_html: str) -> str:
        if not cleaned_html:
            return ""

        # 1. Estrazione testo con BS4 (niente Markdown = niente cancelletti o asterischi!)
        soup = BeautifulSoup(cleaned_html, 'html.parser')
        text = soup.get_text(separator='\n')

        # rimuove sezioni inutili a fine pagina
        stops = [
            "Monitoraggio allergie", 
            "Indice di qualità", 
            "Previsioni per la tua zona", 
            "Mappa meteorologica",
            "I video più visti",
            "Dati forniti da"
        ]
        for stop in stops:
            if stop in text:
                text = text.split(stop)[0]

        # 3. FIX DEI GRADI E PERCENTUALI (La magia che risolve il tuo screen!)
        # Unisce "18 \n °" in "18°" e "50 \n %" in "50%"
        text = re.sub(r'(\d+)\s*\n\s*°', r'\1°', text)
        text = re.sub(r'(\d+)\s*\n\s*%', r'\1%', text)
        
        # 4. FIX DEL MAX/MIN
        # Trasforma "Max Min" (su una o più righe) in "Max/Min" come vuole il GS
        text = re.sub(r'\bMax\s*\n?\s*Min\b', 'Max/Min', text, flags=re.IGNORECASE)

        # 5. RIMOZIONE JUNK UI (Senza causare overfitting sulle varie pagine)
        junk = [
            "Advertisement", "Pubblicità", "Recenti", "Cerca città o CAP",
            "Non hai posizioni recenti", "Passa al contenuto principale", 
            "Assistenza per accessibilità", "Ibrido", "C/millimetri/km/km/h/millibar",
            "Dettagli", "Nascondi dettagli", "Altro", "Altre previsioni",
            "Previsioni specializzate"
        ]
        for j in junk:
            text = re.sub(rf'\b{j}\b', '', text, flags=re.IGNORECASE)

        # 6. PULIZIA CARATTERI (Preserviamo accenti, °, %, il trattino - e lo slash /)
        text = re.sub(r'[^a-zA-Z0-9\u00c0-\u00ff°%:\-/\n]', ' ', text)
        
        # 7. NORMALIZZAZIONE RIGHE
        lines = [re.sub(r' +', ' ', line.strip()) for line in text.splitlines() if line.strip()]
        
        return "\n".join(lines)