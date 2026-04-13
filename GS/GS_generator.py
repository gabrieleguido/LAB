import json 

lista = []

bermuda_json = open("./wikipedia/BermudaTriangle/BermudaTriangle.json","r",encoding = 'UTF-8')
chatgpt_json = open("./wikipedia/ChatGPT/ChatGPT.json","r",encoding = 'UTF-8')
laika_json = open("./wikipedia/Laika/Laika.json","r",encoding = 'UTF-8')
python_json = open("./wikipedia/Python/Python.json","r",encoding = 'UTF-8')
referee_json = open("./wikipedia/Referee/Referee.json","r",encoding = 'UTF-8')

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

GS_json = open("./wikipedia/GS.json","w",encoding = 'UTF-8')

GS_json.write(json.dumps(lista,indent=1))

bermuda_json.close()
chatgpt_json.close()
laika_json.close()
python_json.close()
referee_json.close()





