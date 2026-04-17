import re

class ParseCleaner: 
    
    @staticmethod
    def clean_string(text: str) -> str:
        text = re.sub(r'\(\s*https?://[^)]*\)', ' ', text)
        text = re.sub(r'\[\[\d+\]\]', ' ', text)
        text = re.sub(r'[^a-zA-Z0-9]', ' ', text)
        words = [w for w in text.split(" ") if w]
        
        # Restituisce i termini separati da spazio in un'unica stringa
        return " ".join(words)

    @staticmethod
    def parsed_clean(file_name_src: str, file_name_dst: str, enc: str) -> None:
        with open(file_name_src, "r", encoding=enc) as src, \
             open(file_name_dst, "w", encoding=enc) as dst:
            
            raw_text = src.read()
            cleaned = ParseCleaner.clean_string(raw_text)
            dst.write(cleaned)