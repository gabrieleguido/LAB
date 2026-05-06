import json 

lista = []
for i in range(1,11):
    gs_file = open(f"./wikipedia/gs{i}/gs{i}.json","r",encoding = 'UTF-8')
    json_dict = json.load(gs_file)
    lista.append(json_dict)
    gs_file.close()

GS_json = open("./wikipedia/wikipedia_gs.json","w",encoding = 'UTF-8')

GS_json.write(json.dumps(lista,indent=1))







