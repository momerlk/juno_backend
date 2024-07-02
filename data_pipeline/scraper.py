# Works only for shopify sites
import csv
import json
from urllib.request import urlopen
import sys
import numpy as np
import os
import json
from pymongo import MongoClient
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from bs4 import BeautifulSoup
import uuid
import pprint

# TODO : Khaadi, Bareeze, Junaid Jamshed, Gul Ahmed

# limelight has most products : 27,284
# products scraped close to 110,000

# to get product url : {base_url}/products/{product["handle"]}
# to check availability : product["variants"][i]["available"]

local_db_server = "mongodb://localhost:27017/"
online_db_server = 'mongodb+srv://swift:swift@hobby.nzyzrid.mongodb.net/'
MONGO_URI = online_db_server
DATABASE_NAME = 'juno'
COLLECTION_NAME = 'products'

def upload_to_mongo(db, collection, data):
    collection.insert_one(data)

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

brands = [
    # {"name" : "afrozeh" , "base_url" : "https://www.afrozeh.com"},
    # {"name" : "ali_xeeshan" , "base_url" :  "https://alixeeshanempire.com"},
    # {"name" : "alkaram_studio" , "base_url" :  "https://www.alkaramstudio.com"},
    # {"name" : "asim_jofa" , "base_url" :  "https://asimjofa.com"},
    # {"name" : "beechtree" , "base_url" :  "https://beechtree.pk"},
    # {"name" : "bonanza_satrangi" , "base_url" :  "https://bonanzasatrangi.com"},
    # {"name" : "chinyere" , "base_url" :  "https://chinyere.pk"},
    # {"name" : "cross_stitch" , "base_url" :  "https://www.crossstitch.pk"},
    # {"name" : "edenrobe" , "base_url" :  "https://edenrobe.com"},
    # {"name" : "ethnic" , "base_url" :  "https://pk.ethnc.com"},
    # {"name" : "faiza_saqlain" , "base_url" :  "https://www.faizasaqlain.pk"},
    # {"name" : "generation" , "base_url" :  "https://generation.com.pk"},
    # {"name" : "hem_stitch" , "base_url" :  "https://www.hemstitch.pk"},
    # {"name" : "hussain_rehar" , "base_url" :  "https://www.hussainrehar.com"},
    # {"name" : "kanwal_malik" , "base_url" :  "https://www.kanwalmalik.com"},
    # {"name" : "kayseria" , "base_url" :  "https://www.kayseria.com"},
    # {"name" : "limelight" , "base_url" :  "https://www.limelight.pk"},
    # {"name" : "maria_b" , "base_url" :  "https://www.mariab.pk"},
    # {"name" : "mushq" , "base_url" :  "https://www.mushq.pk"},
    # {"name" : "nishat_linen" , "base_url" :  "https://nishatlinen.com"},
    # {"name" : "sadaf_fawad_khan" , "base_url" :  "https://sadaffawadkhan.com"},
    # {"name" : "sapphire" , "base_url" :  "https://pk.sapphireonline.pk"},
    # {"name" : "zaha" , "base_url" :  "https://www.zaha.pk"},
    # {"name" : "zara_shah_jahan" , "base_url" :  "https://zarashahjahan.com"},
    # {"name" : "zellbury" , "base_url" :  "https://zellbury.com"},
    # {"name" : "outfitters" , "base_url" : "https://outfitters.com.pk/"},
    # {"label" : "Breakout" , "name" : "breakout" , "base_url" : "https://breakout.com.pk/"},
    {"label" : "Breakout" , "name" : "breakout" , "base_url" : "https://breakout.com.pk/"},

]

# TODO : Add discounts which are compare_at_price in shopify data
# TODO : Different price for each variant display price should be closest price to Rs.1000

def get_page(base_url , url , handle , page , upload=True):
    data = urlopen(url + '?page={}'.format(page)).read()
    products = json.loads(data)['products']
    extracted_pds = []
    for product in products : 
        extracted_pd = extract_fields(base_url , handle , product)
        if extracted_pd != None : 
            extracted_pds.append(extracted_pd)
            if upload == True : 
                upload_to_mongo(db,collection,extracted_pd)

    return extracted_pds


def scrape_brand(details : dict):
    base_url = details["base_url"]
    name = details["name"]
    handle = name.lower().replace(" " , "_")
    
    file_name = f"{handle}.json"
    url = f"{base_url}/products.json"

    
    page = 1
    products = get_page(base_url,url,handle,page)
    arr = np.array(products)
    while products : 
        page += 1
        products = get_page(base_url,url,handle,page)
        arr = np.append(arr , products)

    print(f"total products scraped = {len(arr)}")

    return products


def remove_unicode_codes(string):
    # Regex pattern to match Unicode escape sequences
    unicode_code_pattern = r'\\u[0-9a-fA-F]{6}'
    # Substitute the Unicode escape sequences with an empty string
    cleaned_string = re.sub(unicode_code_pattern, '', string)
    return cleaned_string

def preprocess_text(text):
    # Remove HTML tags
    try : 
        text = BeautifulSoup(text, "html.parser").get_text()
    except Exception  as e :
        print(f"failed to preprocess html data, error = {e}")

    text = remove_unicode_codes(text)

    return text



def extract_fields(base_url , handle , json_data):

    
    description = json_data.get("body_html")

    if description == None or description == "" : 
        return None

    try : 
        # TODO : change preprocess to just remove html tags. 
        description = preprocess_text(description)
    except Exception as e : 
        print(f"failed to preprocess description, error = {e}, description = {description}")


    product_available = False

    variant_index = 0

    def null_to_str(val):
        if val == None : 
            return ""
        else : 
            return val

    variants = []
    for idx, variant in enumerate(json_data.get("variants")) : 
        first_dig = variant["price"].split(".")[0][0]
        if first_dig == "0" : 
            return None
        available = variant["available"]
        if available == False : 
            continue 
        
        if available == True : 
            product_available = True
        
        variants.append({
            "id" : f"{variant["id"]}",
            "price" : variant["price"],
            "option1" : null_to_str(variant["option1"]),
            "option2" : null_to_str(variant["option2"]),
            "option3" : null_to_str(variant["option3"]),
        })

        

    if product_available == False : 
        return None


    variant = json_data.get("variants")[variant_index] 

    url = f"{base_url}/products/{json_data.get("handle")}"
    vendor = handle
    price = variant["price"].split(".")[0]
    images = json_data.get("images")
    if len(images) == 0 : 
        return None 
    image_url = images[0]["src"]

    image_urls = []
    for image in images : 
        image_urls.append(image["src"])

    product =  {
        'product_id': str(uuid.uuid4()),
        'product_url' : url,
        "shopify_id" : f"{json_data.get("id")}",

        'handle' : json_data.get("handle"),
        'title': json_data.get('title').replace("-" , " ").replace("_" , " ").title(),
        "vendor" : vendor,
        "vendor_title" : vendor.replace("_" , " ").title(),
        "category" : "",
        "product_type" : json_data.get("product_type"),

        "image_url" : image_url,
        "images" : image_urls,
        "description" : description, 

        "price" : int(price),
        "currency" : "PKR",

        "variants" : variants,
        "options" : json_data.get("options"),
        "tags" : json_data.get("tags"),
        "available" : True,
    }

    # Pretty print the dictionary
    # pretty_product = pprint.pformat(product)
    # print(pretty_product)



    return product


# scrape data from all brands and upload it to mongodb
for brand in brands : 
    name = brand["name"].replace("_" , " ").title()
    brand["name"] = name 
    scrape_brand(brand)

