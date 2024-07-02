import csv
import json
from urllib.request import urlopen
import sys
import json
import numpy as np

# TODO : Khaadi, Bareeze, Junaid Jamshed, Gul Ahmed

# limelight has most products : 27,284
# products scraped close to 110,000

# to get product url : {base_url}/products/{product["handle"]}
# to check availability : product["variants"][i]["available"]

base_url = "https://www.kayseria.com"
url = base_url + '/products.json'

file_name = "kayseria.json"

def get_page(page):
    data = urlopen(url + '?page={}'.format(page)).read()
    products = json.loads(data)['products']
    return products
  
with open(file_name, "w") as f : 
    page = 1
    products = get_page(page)
    arr = np.array(products)
    while products : 
        page += 1
        products = get_page(page)
        arr = np.append(arr , products)

    json.dump(arr.tolist()  , f , indent=4)
    print(f"total products scraped = {len(arr)}")
