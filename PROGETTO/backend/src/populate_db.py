import mariadb
import json

class Populator:
    def populate(connection):
        conn = connection

        gs_files_names = ["nbcnews_gs.json","uefa_gs.json","weather_gs.json","wikipedia_gs.json"]
        cur = conn.cursor()

        #popolazione da gs
        #per ogni file in gs_data
        for file_name in gs_files_names: 
            
            with open(f"../../gs_data/{file_name}", "r", encoding="utf-8") as file: 
                gs_list = json.load(file)

                #inserisco i dati per ogni elemento nella lista del json
            
                for entry in gs_list:
                    try:
                        cur.execute( 
                                    "INSERT INTO web_resources (url, domain, title, html_text) VALUES (?, ?, ?, ?)",
                                    (entry.get("url"), entry.get("domain"), entry.get("title"), entry.get("html_text"))
                                )
                        cur.execute(
                                    "INSERT INTO gold_standard (url, gold_text) VALUES (?, ?)",
                                    (entry.get("url"), entry.get("gold_text"))
                                )
                    except mariadb.Error as e:
                        print(f"Errore durante l'inserimento di {entry.get('url')}: {e}")
        
        #popolazione da stats
        with open("stats.txt","r",encoding="UTF-8") as stats_file:
            for line in stats_file: 
                line = line.strip()
                print(line)
                tokens = line.split(",")
                url = str(tokens[0])
                prec = float(tokens[1])
                rec = float(tokens[2])
                f1 = float(tokens[3])
                score = int(tokens[4])
                try:
                    cur.execute( 
                                "INSERT INTO stats(url, prec, rec, f1, score) VALUES (?, ?, ?, ?, ?)",
                                (url,prec,rec,f1,score)
                            )
                except mariadb.Error as e:
                    print(f"Errore durante l'inserimento di {url}: {e}")
                except Exception as e:
                    print(f"Errore {e}")
                    
        cur.close()        
        conn.commit() 