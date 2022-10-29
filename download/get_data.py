from scrapezoopla.get import GetAll, get_latest_properties
from datetime import datetime

search_term = "bristol"

ga = GetAll(search_term, True)
ga.write_s3("data\\properties", "properties")

date = datetime.now().strftime("%d%m%Y")

properties_df = get_latest_properties("data\\properties")
properties_df.to_parquet(f"data\\tables\\{search_term}_{date}.parquet")
