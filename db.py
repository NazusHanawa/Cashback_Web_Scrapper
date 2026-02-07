import libsql
import requests
import difflib
import os

from datetime import datetime
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

class DB:
    def __init__(self, database_url, auth_token, headers):
        self.database_url = os.environ.get("DATABASE_URL")
        self.auth_token = os.environ.get("AUTH_TOKEN")
        self.headers = headers

        self.conn = libsql.connect(database=self.database_url, auth_token=self.auth_token)
        self.cursor = self.conn.cursor()
        print("DATABASE CONNECTED.")
    
    def commit(self):
        self.conn.commit()
    
    def remove_tables(self):
        print("REMOVING TABLES...")
        tables = ["stores", "cashbacks", "partnerships", "platforms"]
        for table in tables:
            self.cursor.execute(f"DROP TABLE IF EXISTS {table};")
        self.commit()
        
    def create_tables(self, schema):
        print("CREATING TABLES...")
        self.cursor.executescript(schema)
        self.commit()
        
    def create_stores(self, stores):
        print("CREATING STORES...")
        stores_tuples = [
            (store["name"], store["url"]) for store in stores
        ]
        self.cursor.executemany("INSERT OR IGNORE INTO stores (name, url) VALUES (?, ?);", stores_tuples)
        self.commit()
        
    def create_platforms(self, platforms):
        print("CREATING PLATFORMS...")
        platforms_tuples = [
            (platform["name"], platform["url"], platform["cashback_value_path"], platform["cashback_description_path"])
            for platform in platforms
        ]
        self.cursor.executemany("INSERT OR IGNORE INTO platforms (name, url, cashback_value_path, cashback_description_path) VALUES (?, ?, ?, ?);", platforms_tuples)
        self.commit()
    
    def create_partners(self):
        print("CREATING PARTNERS...")

        stores = self.cursor.execute("SELECT * FROM stores").fetchall()
        platforms = self.cursor.execute("SELECT * FROM platforms").fetchall()

        partnerships = []
        for platform in platforms:
            platform_id = platform[0]
            platform_name = platform[1]
            platform_url = platform[2]
            
            parsed_url = urlparse(platform_url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

            response = requests.get(platform_url, headers=self.headers)
            soup = BeautifulSoup(response.text, "html.parser")
            html_as = soup.find_all("a")
            
            platform_links = {}
            
            for html_a in html_as:
                url_path = html_a.get('href')
                store_name = html_a.get_text(strip=True).lower()

                if not url_path or not store_name:
                    continue
                    
                if len(store_name) > 32:
                    continue
                
                platform_links[store_name] = urljoin(base_url, url_path)

            for store in stores:
                store_id = store[0]
                store_name = store[1].lower()
                
                best_name = difflib.get_close_matches(store_name, platform_links, n=1, cutoff=0.7)
                if not best_name:
                    print(f"ERRO: {store_name}")
                    exit()
                
                best_name = best_name[0]
                partnership_link = platform_links[best_name]
                
                partnership = {
                    "store_id": store_id,
                    "platform_id": platform_id,
                    "url": partnership_link
                }

                partnerships.append(partnership)

        partnerships_tuples = [
            (p["store_id"], p["platform_id"], p["url"]) for p in partnerships
        ]
        self.cursor.executemany("INSERT OR IGNORE INTO partnerships (store_id, platform_id, url) VALUES (?, ?, ?);", partnerships_tuples)
        self.commit()
    
    def get_parnerships(self):
        query = """
            SELECT 
                p.id, 
                p.url, 
                plat.cashback_value_path
            FROM partnerships p
            JOIN platforms plat ON p.platform_id = plat.id
        """
        partnerships_data = self.cursor.execute(query).fetchall()

        partnerships = []
        for p in partnerships_data:
            partnership = {
                "id": p[0], 
                "url": p[1], 
                "selector": p[2]
            }
            partnerships.append(partnership)
            
        return partnerships
    
    def create_cashbacks(self, cashbacks):
        self.update_old_cashbacks_date_end(cashbacks)
        
        base_query = "INSERT OR IGNORE INTO cashbacks (partnership_id, value, description) VALUES "
        
        placeholders = ", ".join(["(?, ?, ?)"] * len(cashbacks))
        full_query = base_query + placeholders + ";"
        
        flattened_values = []
        for c in cashbacks.values():
            flattened_values.extend([c["partnership_id"], c["value"], c["description"]])

        self.cursor.execute(full_query, flattened_values)
        self.conn.commit()
        
    def update_old_cashbacks_date_end(self, cashbacks_dict):
        ids_to_check = ", ".join(map(str, cashbacks_dict.keys()))

        query = f"""
        UPDATE cashbacks
        SET date_end = datetime('now', 'localtime')
        WHERE id IN (
            SELECT id
            FROM (
                SELECT id, date_end,
                    (julianday('now', 'localtime') - julianday(date_end)) * 24 AS diff_hours
                FROM cashbacks
                WHERE partnership_id IN ({ids_to_check})
                GROUP BY partnership_id
                HAVING id = MAX(id)
            )
            WHERE diff_hours <= 1
        );
        """
        
        self.cursor.execute(query)
        self.conn.commit()
        