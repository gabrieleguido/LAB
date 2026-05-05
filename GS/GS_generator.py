import json 

lista = []

gs1_json = open("./nbcnews/gs1/gs1.json","r",encoding = 'UTF-8')
gs2_json = open("./nbcnews/gs2/gs2.json","r",encoding = 'UTF-8')
gs3_json = open("./nbcnews/gs3/gs3.json","r",encoding = 'UTF-8')
gs4_json = open("./nbcnews/gs4/gs4.json","r",encoding = 'UTF-8')
gs5_json = open("./nbcnews/gs5/gs5.json","r",encoding = 'UTF-8')
gs6_json = open("./nbcnews/gs6/gs6.json","r",encoding = 'UTF-8')
gs7_json = open("./nbcnews/gs7/gs7.json","r",encoding = 'UTF-8')
gs8_json = open("./nbcnews/gs8/gs8.json","r",encoding = 'UTF-8')
gs9_json = open("./nbcnews/gs9/gs9.json","r",encoding = 'UTF-8')
gs10_json = open("./nbcnews/gs10/gs10.json","r",encoding = 'UTF-8')


gs1_obj = json.load(gs1_json)
gs2_obj = json.load(gs2_json)
gs3_obj = json.load(gs3_json)
gs4_obj = json.load(gs4_json)
gs5_obj = json.load(gs5_json)
gs6_obj = json.load(gs6_json)
gs7_obj = json.load(gs7_json)
gs8_obj = json.load(gs8_json)
gs9_obj = json.load(gs9_json)
gs10_obj = json.load(gs10_json)

lista.append(gs1_obj)
lista.append(gs2_obj)
lista.append(gs3_obj)
lista.append(gs4_obj)
lista.append(gs5_obj)
lista.append(gs6_obj)
lista.append(gs7_obj)
lista.append(gs8_obj)
lista.append(gs9_obj)
lista.append(gs10_obj)

GS_json = open("./nbcnews/GS.json","w",encoding = 'UTF-8')

GS_json.write(json.dumps(lista,indent=1))

gs1_json.close()
gs2_json.close()
gs3_json.close()
gs4_json.close()
gs5_json.close()
gs6_json.close()
gs7_json.close()
gs8_json.close()
gs9_json.close()
gs10_json.close()





