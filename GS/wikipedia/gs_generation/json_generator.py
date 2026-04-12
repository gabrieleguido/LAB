import json 

#---->cambiare nome dei file su cui ci stanno l'html e gs(originali non formattati) 
html_file = open("test_exapmle.html","r")
golden_file = open("test_example_GS.txt","r")

html_text = html_file.read() 
golden_text = golden_file.read() 


json_entry = {
    #----->cambiare url,dominio e titolo:
    "url":"https://en.wikipedia.org/wiki/Peroni_(company)",
    "domain":"en.wikipedia.org",
    "title":"Peroni_(company)",
    "html_text":html_text,
    "gold_text":golden_text
}

#----->dare un nome sensato al file output, cambiare nome per ogni pagina
result = open("result.json","w")
result.write(json.dumps(json_entry))