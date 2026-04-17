from pydantic import BaseModel
import re 

class ParseCleaner(BaseModel):
    @staticmethod
    def parsed_clean(file_name_src:str,file_name_dst:str,enc:str,link_del_flag:bool=True)->None:
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
            #link delete: line = re.sub(r'\(\s*https?://[^)]*\)',' ',line)
            if(link_del_flag):
                #elimino le note []
                line = re.sub(r'\[\[\d+\]\]',' ',line)

            line = re.sub(r'[^a-zA-Z0-9]',' ',line)
        markdown_file.close()
        clean_file.close()

    
        
