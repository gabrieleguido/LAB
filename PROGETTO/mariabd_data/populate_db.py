import mariadb
import json

conn = mariadb.connect(
    host = "127.0.0.1",
    port = 3306,
    user = "backend_user",
    password = "backend_password",
    database = "lab_db"
)

gs_files_names = ["nbcnews_gs.json","uefa_gs.json","weather_gs.json","wikipedia_gs.json"]
#per ogni file in gs_data
for file_name in gs_files_names:

    #apro il file
    with open(f"../gs_data/{file_name}") as file:
        gs_list = json.load(file)

        #inserisco i dati per ogni elemento nella lista del json
        for entry in gs_list:

            #creo le query parametrizzate (con i '?')
            query_web = "INSERT INTO web_resources VALUES (?,?,?,?)"
            query_gs = "INSERT INTO gold_standard VALUES (?,?)"

            with conn.cursor() as cursor:

                url = entry.get("url")
                domain = entry.get("domain")
                title = entry.get("title")
                html_text = entry.get("html_text")
                gold_text = entry.get("gold_text")

                cursor.execute(query_web,(url,domain,title,html_text))
                cursor.execute(query_gs,(url,gold_text))
                res = cursor.fetchall()

            conn.commit() 
            print(res)