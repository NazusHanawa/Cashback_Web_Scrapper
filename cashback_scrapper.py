import requests
import re

from bs4 import BeautifulSoup

class CashabackScrapper:
    def __init__(self, partnerships, headers):
        self.partnerships = partnerships
        self.headers = headers
        
        self.old_cashbacks = {}
        
    def set_partnerships(self, partnerships):
        self.partnerships = partnerships
    
    def get_cashback(self, partnership):
        response = requests.get(partnership["url"], headers=self.headers)
        if response.status_code != 200:
            print(f"ERRO: {response.status_code} --> {partnership["url"]}")
            print(f"{partnership["url"]}")
            exit()
            
        soup = BeautifulSoup(response.text, "html.parser")
        cashback_part = soup.select_one(partnership["selector"])
        if cashback_part:
            cashback_value = re.search(r"\d+[.,]?\d*%", cashback_part.text).group().replace("%", "").replace(",", ".")
        else:
            print(f"Cashback not found: {cashback_part} --> {partnership["url"]}")
            cashback_value = 0
        
        cashback = {
            "partnership_id": partnership["id"],
            "value": cashback_value,
            "description": None
        }
        return cashback
    
    def get_new_cashbacks(self):
        cashbacks = {}
        for partnership in self.partnerships:        
            cashback = self.get_cashback(partnership)
            cashbacks[partnership["id"]] = cashback
        
        new_cashbacks = {}
        for partnership_id, cashback in cashbacks.items():
            old_cashback = self.old_cashbacks.get(partnership_id)
            
            if old_cashback != cashback:
                new_cashbacks[partnership_id] = cashback
                continue
            
            new_cashbacks[partnership_id] = cashback
            
        self.old_cashbacks = cashbacks
        
        return new_cashbacks
    
    def get_old_cashbacks(self):
        return self.old_cashbacks