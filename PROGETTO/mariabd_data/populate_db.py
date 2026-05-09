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
cur = conn.cursor()
for file_name in gs_files_names:

    #apro il file
    with open(f"../gs_data/{file_name}") as file:
        gs_list = json.load(file)

        #inserisco i dati per ogni elemento nella lista del json
       
        for entry in gs_list:
            try: 
                cur.execute( 
                            "INSERT IGNORE INTO web_resources (url, domain, title, html_text) VALUES (?, ?, ?, ?)",
                            (entry.get("url"), entry.get("domain"), entry.get("title"), entry.get("html_text"))
                        )
                cur.execute(
                            "INSERT IGNORE INTO gold_standard (url, gold_text) VALUES (?, ?)",
                            (entry.get("url"), entry.get("gold_text"))
                        )
            except mariadb.Error as e:
                print(f"Errore durante l'inserimento di {entry.get('url')}: {e}")
                
        conn.commit() 
    cur.close()