import json, os
from scrape import search_zoopla, get_property_ids

class GetAll:
    def __init__(self, search_term:str):
        self.search_term = search_term

    def get_ids(self):
        self.search = search_zoopla(self.search_term)
        self.ids = get_property_ids(search)

    def get_data(self):
        self.data = [ScriptData(i).out_dict for i in self.ids]

    def write_local(self, base_path: str):
        for (i, d) in zip(self.ids, self.data):
            path = os.path.join(base_path, self.property_num)
            os.makedirs(path, exist_ok = True)

            json_obj = json.dumps(self.out_dict)

            with open(os.path.join(path, "out.json"), "w") as f: f.write(json_obj)

