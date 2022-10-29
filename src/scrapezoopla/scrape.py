import pandas as pd
import requests, json, os, re
from datetime import datetime

import bs4
from bs4 import BeautifulSoup as soup

def search_zoopla(area, page_num=1):
    html = requests.get(f'https://www.zoopla.co.uk/for-sale/property/{area}/?pn={page_num}')
    return soup(html.content, features="html.parser")

def get_property_page(id_):
    """_summary_

    Args:
        id_ (_type_): _description_

    Returns:
        _type_: _description_
    """
    html = requests.get(f'https://www.zoopla.co.uk/for-sale/details/{id_}/')
    return soup(html.content, features="html.parser")    

def get_property_ids(search_term: str, 
                     page_start: int = 0, 
                     page_end: int = -1, 
                     verbose: bool = False):
    """Get property IDs from a zoopla search page.

    Args:
        search (soup): A soup of a Zoopla property search. Can use scrape_zoopla.scrape.search_zoopla to get this. 
        page_start (int, optional): Start page for search. Defaults to 0.
        page_end (int, optional): End page for search. Defaults to -1 (i.e. take all).
        verbose (bool, optional): Print messages when each page is completed. Defaults to False.

    Returns:
        list: list of property ids
    """

    search = search_zoopla(search_term)

    # Get last page
    pagination = search.select("div[data-testid~=pagination]")[0]
    page_nums = [t.text for t in pagination.find_all("li") if t.text not in ["< Back", "Next >"]]

    if verbose: print("Search has", len(page_nums), "pages")

    if page_end == -1: page_nums = page_nums[page_start:]
    else: page_nums = page_nums[page_start:(page_end+1)] 

    all_ids = []
    for i in page_nums:
        page = search_zoopla(search_term, i)
        properties = page.select("div[data-testid*=search-result_listing]")
        ids = [p["id"][8:] for p in properties]    
        all_ids += ids
        if verbose: print("Ran page", i)
            
    return all_ids

class ScriptData:
    def __init__(self, property_num):
        # Property Details
        self.page_url = f'https://www.zoopla.co.uk/for-sale/details/{property_num}/'
        self.property_page = get_property_page(property_num)
        self.property_num = property_num

        # Get base Script Dict
        json_data = self.property_page.find("script")
        self.script_dict = self.process_json(json_data)
        
        self.residence_details = self.script_dict["@graph"][3]
        self.type_ = self.residence_details["@type"]
        self.geo = self.residence_details["geo"]

        # Get Bedrooms. Sometimes this is missing, in which case None
        find = self.property_page.find("use", attrs = {"href": "#bedroom-medium"})
        if find is None: 
          self.bedrooms_text, self.bedrooms_num = "", float("nan")
        else: 
          self.bedrooms_text = find.parent.parent.parent.get_text()
          self.bedrooms_num = int(re.findall(r"\d+", self.bedrooms_text)[0])        

        self.photo_dict = self.residence_details["photo"]
        self.photo_urls = [p["contentUrl"] for p in self.photo_dict]
        
        # Get Price
        self.price = self.property_page.find("p", attrs = {"data-testid": "price"}).get_text()

        # Get output json
        ## First, get numeric values
        price_text = self.price.replace("£", "").replace(",", "")
        try:
            self.price_num = int(price_text)
        except:
            self.price_num = float("nan")
            
        gd = self.geo.copy()
        gd.pop("@type")
        self.gd = gd

        feat_bullet = self.property_page.select("ul[data-testid=listing_features_bulletted]")
        text_bs = feat_bullet[0].find_all("li") if len(feat_bullet) > 0 else []
        self.features_text = [t.text for t in text_bs]

        text_all = list(self.property_page.select("div[data-testid=truncated_text_container]")[0].find("span").descendants)
        self.description_text = []
        for t in text_all:
            if isinstance(t, bs4.element.Tag): pass
            elif isinstance(t, bs4.element.NavigableString): self.description_text.append(t)
            else: raise TypeError("Type not supported. Should be bs4.element.Tag or bs4.element.NavigableString")

        try:
            self.out_dict = {"bedrooms_num": self.bedrooms_num,
                            "bedrooms_text": self.bedrooms_text,
                          "latitude": self.gd["latitude"],
                          "longitude": self.gd["longitude"], 
                          "features": self.features_text,
                          "description": self.description_text,
                          "photos": self.photo_urls, 
                          "price": self.price_num, 
                          "extract_time": datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
        except:
            raise ValueError("Failed. This is likely due to missing data")


    def process_json(self, json_data):
        json_str = json_data.text
        json_str = json_str.replace("\n", "")
        json_str = json_str.replace("\t", "")
        
        return json.loads(json_str)
    
    def write_local_json(self, write_path):
        base_path = os.path.join(write_path, self.property_num)
        os.makedirs(base_path, exist_ok = True)

        json_obj = json.dumps(self.out_dict)

        with open(os.path.join(base_path, "out.json"), "w") as f:
            f.write(json_obj)
