import json 

lista = []

bermuda_json = open("./weather/gs1/gs1.json","r",encoding = 'UTF-8')
chatgpt_json = open("./weather/gs2/gs2.json","r",encoding = 'UTF-8')
laika_json = open("./weather/gs3/gs3.json","r",encoding = 'UTF-8')
python_json = open("./weather/gs4/gs4.json","r",encoding = 'UTF-8')
referee_json = open("./weather/gs5/gs5.json","r",encoding = 'UTF-8')

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

GS_json = open("./weather/GS.json","w",encoding = 'UTF-8')

GS_json.write(json.dumps(lista,indent=1))

bermuda_json.close()
chatgpt_json.close()
laika_json.close()
python_json.close()
referee_json.close()





