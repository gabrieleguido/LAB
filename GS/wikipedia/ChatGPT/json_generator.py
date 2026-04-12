import json 

#---->cambiare nome dei file su cui ci stanno l'html e gs(originali non formattati) 
html_file = open("ChatGPT.html","r")
golden_file = open("ChatGPT_GS.txt","r")

html_text = html_file.read() 
golden_text = golden_file.read() 


json_entry = {
    #----->cambiare url,dominio e titolo:
    "url":"https://en.wikipedia.org/wiki/ChatGPT",
    "domain":"en.wikipedia.org",
    "title":"ChatGPT",
    "html_text":html_text,
    "gold_text":golden_text
}

#----->dare un nome sensato al file output, cambiare nome per ogni pagina
result = open("ChatGPT.json","w")
result.write(json.dumps(json_entry))