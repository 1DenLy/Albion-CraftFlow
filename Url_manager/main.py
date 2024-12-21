import os

import pandas, webbrowser, datetime

from Url_manager.url_generator import UrlGenerator



class URL_parser():
    def __init__(self, file_manager= None):
        
        self.file_manager = file_manager
    
        self.generator = UrlGenerator(
            parcing_list= self.file_manager.parsing_list_dict,
            items_info= self.file_manager.items_info
        )




    def url_open(self, url): webbrowser.open_new(url)


    def Save_Json_From_Url(self, url: str, parse_date_column: str, pretty_print=False):
        try:
            df = pandas.read_html(url, header=0, parse_dates=[parse_date_column])
        except Exception as e:
            print(f"Failed to read data from {url}: {e}")
            
        current_time = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        
        file_name = f"Prices_{current_time}.json"

        path_to_save = './Last_JSON_File/'
        
        if os.path.isfile(file_name):   # Проверяем, существует ли уже файл
            print(f"File {file_name} already exists, will not overwrite")
            return
        
        try:    # Записываем данные в формате JSON в файл с указанным именем
            df[0].to_json(path_to_save + file_name, date_format="iso", indent=4 if pretty_print else None)
            print(f"Data saved to {file_name}")
        except Exception as e:  # Выводим сообщение об ошибке, если сохранение не удалось
            print(f"Failed to save data to {file_name}: {e}")

        

if __name__ == '__main__':
    pass