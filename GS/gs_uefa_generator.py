import json 

lista = []

bermuda_json = open("./uefa/g1/anteprima-liverpool-paris-saint-germain-champions-league.json","r",encoding = 'UTF-8')
chatgpt_json = open("./uefa/g2/il-calcio-europeo-piange-mircea-lucescu.json","r",encoding = 'UTF-8')
laika_json = open("./uefa/g3/confermati-i-paesi-che-ospiteranno-uefa-euro-2028-e-2032.json","r",encoding = 'UTF-8')
python_json = open("./uefa/g4/il-calcio-italiano-piange-rocco-commisso.json","r",encoding = 'UTF-8')
referee_json = open("./uefa/g5/federcalcio-isole-faroe.json","r",encoding = 'UTF-8')

bermuda_obj = json.load(bermuda_json)
chatgpt_obj = json.load(chatgpt_json)
laika_obj = json.load(laika_json)
python_obj = json.load(python_json)
referee_obj = json.load(referee_json)

lista.append(bermuda_obj)
lista.append(chatgpt_obj)
lista.append(laika_obj)
lista.append(python_obj)
lista.append(referee_obj)

GS_json = open("./uefa/GS.json","w",encoding = 'UTF-8')

GS_json.write(json.dumps(lista,indent=1))

bermuda_json.close()
chatgpt_json.close()
laika_json.close()
python_json.close()
referee_json.close()

