import os
import json
import sys


URL_EUROPE_SERVER = "https://europe.albion-online-data.com/"
URL_ASIA_SERVER = "https://east.albion-online-data.com/"
URL_AMERICAS_SERVER = "https://west.albion-online-data.com/"

STATS_PRICES = "api/v2/stats/prices/"

LOCATION = "?locations="
QUALITIES_URL = "&qualities="

LOCATIONS = ['BlackMarket','Caerleon','Fortsterling','Martlock','Thetford','Lymhurst','Bridgewatch']

TIERS = ['T4_', 'T5_', 'T6_', 'T7_', 'T8_']
RARYTYES = ['', '@1', '@2', '@3', '@4']



class UrlGenerator:
    def __init__(self, parcing_list: list = None, items_info: dict = None):

        self.parcing_list = parcing_list 
        self.items_info_list = items_info 

        for it in parcing_list:
            print(self.get_info_item(item_class= it["class"], item_name= it["item"],))


    
    # api/v2/stats/prices/T4_BAG,T5_BAG?locations=Caerleon,Bridgewatch&qualities=2
    def create_url(self, items_list, locations_list, server_id):

        if server_id == "eu":
            server = URL_EUROPE_SERVER
        elif server_id == "as":
            server = URL_ASIA_SERVER
        elif server_id == "us":
            server = URL_AMERICAS_SERVER
        else:
            return None

        Url = server 
        + STATS_PRICES 
        + items_list 
        + LOCATION
        + locations_list 
        + QUALITIES_URL






        return Url


    def create_items_list(self):

        items = []

        #tier = 
        #char = 

        for it in parcing_list:
            print(self.get_info_item(item_class= it["class"], item_name= it["item"],))





        return items



    def get_info_item(self, item_class, item_name):
        """Returns the code name for the item"""

        if item_class in self.items_info_list:
            for item in self.items_info_list[item_class]:
                if item == item_name:
                    return self.items_info_list[item_class][item_name]["code_name"]
        return None  













if __name__ == '__main__':
    pass
