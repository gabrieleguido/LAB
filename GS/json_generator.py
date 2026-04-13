import json 

#---->cambiare nome dei file su cui ci stanno l'html e gs(originali non formattati) 
html_file = open("./wikipedia/Python/Python.html","r",encoding='UTF-8')
golden_file = open("./wikipedia/Python/Python_GS.txt","r",encoding='UTF-8')

html_text = html_file.read() 
golden_text = golden_file.read() 


json_entry = {
    #----->cambiare url,dominio e titolo:
    "url":"https://en.wikipedia.org/wiki/Python_(programming_language)",
    "domain":"en.wikipedia.org",
    "title":"Python_(programming_language)",
    "html_text":html_text,
    "gold_text":golden_text
}

#----->dare un nome sensato al file output, cambiare nome per ogni pagina
result = open("./wikipedia/Python/Python.json","w",encoding='UTF-8')
result.write(json.dumps(json_entry,indent=1))
html_file.close()
golden_file.close()