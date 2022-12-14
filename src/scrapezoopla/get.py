import json, os, boto3
import pandas as pd

from scrapezoopla.scrape import search_zoopla, get_property_ids, ScriptData
from datetime import datetime

"""
Need to formalise docs for this. 

In my head this module will do 3 things:
- Read and save (local and/or s3) properties data in bulk
- Collate df for all properties (probably)       

"""

class GetAll:
    def __init__(self, search_term:str, init_get: bool = False):
        """Get info about all properties in a given search term.  

        Args:
            search_term (str): to search in zoopla
            init_get (bool, optional): if True, will download data on initialisation. Defaults to False.
        """
        self.search_term = search_term
        self.timestamp = round(datetime.now().timestamp()) # used for file name
        if init_get:
            self.get_ids()
            self.get_data()
        
    def get_ids(self):
        """Get property ids for the search
        """
        # self.search = search_zoopla(self.search_term)
        self.ids = get_property_ids(self.search_term)

    def get_data(self):
        """Get data for all properties in the search
        """
        self.data = [ScriptData(i).out_dict for i in self.ids]

    def write_local(self, base_path: str):
        """Save property data locally as json. 
        DEPRECATED (see write_s3). Might delete later.

        Args:
            base_path (str): path to save
        """
        for (i, d) in zip(self.ids, self.data):
            path = os.path.join(base_path, i)
            os.makedirs(path, exist_ok = True)

            json_obj = json.dumps(d)
            with open(os.path.join(path, f"{self.timestamp}_data.json"), "w") as f: f.write(json_obj)

    def write_s3(self, local_path: str, s3_path: str):
        """Write data to an s3 bucket

        Args:
            local_path (str): _description_
            s3_path (str): _description_
        """
        bucket = boto3.resource("s3").Bucket("zooplaproperties")

        for (i, d) in zip(self.ids, self.data):
            pl = os.path.join(local_path, i)
            os.makedirs(pl, exist_ok = True)

            f_str = f"{self.timestamp}_data.json"
            local_file = os.path.join(pl, f_str)
            remote_file = os.path.join(os.path.join(s3_path, i), f_str)

            json_obj = json.dumps(d)
            with open(local_file, "w") as f: f.write(json_obj)

            bucket.upload_file(local_file, remote_file)
        
def get_latest_properties(base_path):
    pf = os.listdir(base_path)

    files = []
    for p in pf: 
        fs = os.listdir(os.path.join(base_path, p))
        fs.sort(reverse = True)
        files.append(os.path.join(base_path, p, fs[0]))

    all_data = []
    for f in files:
        with open(f) as js:
            data = json.load(js)
        data = {k: [v] if isinstance(v, list) else v for k, v in data.items()}
        all_data.append(data)
    
    return pd.DataFrame(all_data)

def get_all_properties(base_path):
    pf = os.listdir(base_path)

    files = []
    for p in pf: 
        fs = os.listdir(os.path.join(base_path, p))
        fs.sort(reverse = True)
        files + os.path.join(base_path, p, fs)

    all_data = []
    for f in files:
        with open(f) as js:
            data = json.load(js)
        data = {k: [v] if isinstance(v, list) else v for k, v in data.items()}
        all_data.append(data)

    return pd.DataFrame(all_data)

def equal_dicts(lst):
    ele, chk = lst[0], True
    for item in lst:
        if ele != item:
            chk = False
            break
    return chk

def clean_files(base_dir):
    all_properties = os.listdir(base_dir)
    data_files = [os.listdir(os.path.join(base_dir, p)) for p in all_properties]
    num_data = [len(f) for f in data_files]

    count = 0
    for i, p, d in zip(num_data, all_properties, data_files):
        d.sort(reverse=True)
        if i > 1:
            count += 1
            all_data, times = [], []
            for d_ in d:
                with open(os.path.join(base_dir, p, d_), "r") as j: 
                    data = json.loads(j.read())
                times.append(data["extract_time"])
                data.pop("extract_time")
                all_data.append(data)

            # checks if all the same. if so replace extract_time with list of extract_times
            if equal_dicts(all_data):
                paths = [os.path.join(base_dir, p, d_) for d_ in d]
                for p in paths: os.remove(p)
                out = all_data[0]
                out["extract_time"] = times
                json_obj = json.dumps(out)
                with open(paths[0], "w") as w: w.write(json_obj)
    print("change", count, "files")