import pandas as pd

from scrapezoopla.get import GetAll, get_latest_properties, clean_files

terms = ['BS1', 'BS2', 'BS3', 'BS4', 'BS5', 'BS6', 'BS7', 'BS8', 'BS9', 'BS10', 
        'BS11', 'BS13', 'BS14', 'BS15', 'BS16', 'BS20', 'BS21', 'BS22', 'BS23', 'BS24', 
        'BS25', 'BS26', 'BS27', 'BS28', 'BS29', 'BS30', 'BS31', 'BS32', 'BS34', 'BS35', 
        'BS36', 'BS37', 'BS39', 'BS40', 'BS41', 'BS48', 'BS49']

all_data = []
for t in terms:
    print(f"Running term: {t}")
    # ga = GetAll(t, True)
    # ga.write_local("data/properties")

clean_files("data/properties")
