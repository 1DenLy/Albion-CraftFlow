import json, os



class Files(object):
    def __init__(self):
        # Taking all the files paths
        self.file_path_file = self.open_json(path="config/json/file_path.json")
        

        # Open items file form self.file_path_file
        self.items_info = self.open_json( self.file_path_file["item_path"] )

        # Open settings file form self.file_path_file
        self.settings = self.open_json( self.file_path_file["settings_path"] )

        # Open items file form self.file_path_file
        self.parsing_list_dict = self.open_json( self.file_path_file["actual_parsing_file_path"] )
        
        


    def open_json(self, path):
        if os.path.exists(path):

            with open(path, 'r', encoding='utf-8') as file:
                try:
                    return json.load(file)
                
                except json.JSONDecodeError:
                    print(f'Error: Failed to load JSON from {path}')
                    return None


    def save_json(self, path, data):
        if os.path.exists(path):

            try:
                with open(path, 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)
                print(f'Data saved to {path}')
            except Exception as e:
                print(f'Error: Failed to save JSON to {path}: {e}')


    










