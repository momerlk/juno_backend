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
import math

# TODO : Khaadi, Bareeze, Junaid Jamshed, Gul Ahmed

# limelight has most products : 27,284
# products scraped close to 110,000

# to get product url : {base_url}/products/{product["handle"]}
# to check availability : product["variants"][i]["available"]

local_db_server = "mongodb://localhost:27017/"
online_db_server = 'mongodb+srv://swift:swift@hobby.nzyzrid.mongodb.net/'
MONGO_URI = local_db_server
DATABASE_NAME = 'juno'
COLLECTION_NAME = 'products'

def upload_to_mongo(db, collection, data):
    collection.insert_one(data)

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

brandsColl = db["brands"]

brands = []
with open("./brands.json" , "r") as f : 
    data = json.loads(f.read())
    brands = data

# brandsColl.insert_many(brands)

print("total brands =" , len(brands))

def update_product_if_exists(product):
    # Extract the Shopify ID from the product
    shopify_id = product.get('shopify_id')

    if not shopify_id:
        print("Product does not have a Shopify ID.")
        return False

    # Check if a product with the given Shopify ID exists
    existing_product = collection.find_one({'shopify_id': shopify_id}) 

    if existing_product:
        # Update the existing product
        product["product_id"] = existing_product["product_id"]
        collection.find_one_and_delete({'shopify_id' : shopify_id})
        collection.insert_one(product)
        print(f"updated product id = ${product["product_id"]}") 
        return True
    else:
        # Product does not exist, do nothing
        return False


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

    print(f"total new products scraped = {len(arr)}, from {details["name"]}")

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
    def price_fmt(price):
        if price == None : 
            return -1
        return int(price.split(".")[0])

    variants = []
    distance = 900000000000

    compare_price_vt = -1
    
    for idx, variant in enumerate(json_data.get("variants")) : 
        first_dig = variant["price"].split(".")[0][0]

        price = price_fmt(variant["price"])
        compare_price = price_fmt(variant["compare_at_price"])

        if first_dig == "0" : 
            return None
        available = variant["available"]
        if available == False : 
            continue 

        if price < 100 : 
            price = 500
            compare_price = 500

        if available == True : 
            this_distance = abs(1000 - price)
            if this_distance < distance : 
                distance = this_distance
                variant_index = idx
                compare_price_vt = compare_price
            product_available = True
        
        

        variants.append({
            "id" : f"{variant["id"]}",
            "price" : variant["price"],
            "title" : variant["title"],
            "price" : price,
            "compare_price" :compare_price,
            "option1" : null_to_str(variant["option1"]),
            "option2" : null_to_str(variant["option2"]),
            "option3" : null_to_str(variant["option3"]),
        })


    variant = json_data.get("variants")[variant_index] 

    url = f"{base_url}/products/{json_data.get("handle")}"
    vendor = handle
    price = price_fmt(variant["price"])
    images = json_data.get("images")
    if len(images) == 0 : 
        return None 
    image_url = images[0]["src"]

    image_urls = []
    for image in images : 
        image_urls.append(image["src"])

    if price < 100 : 
        price = 500
        compare_price = 500
        compare_price_vt = 500

    discount = 0
    if compare_price_vt != -1 and compare_price_vt != 0 and price != 0: 
        res = 1-(price/compare_price_vt)
        if res < 0.1 and res > 0: 
            res = 0.1
        if res > 0 :
            discount = int(res * 100)

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

        "price" : price,
        "compare_price" : compare_price_vt,
        "discount" : discount,
        "currency" : "PKR",

        "variants" : variants,
        "options" : json_data.get("options"),
        "tags" : json_data.get("tags"),
        "available" : product_available,
    }
    

    # if exists just update
    exists = update_product_if_exists(product)
    if exists == True : 
        return None

    # Pretty print the dictionary
    # pretty_product = pprint.pformat(product)
    # print(pretty_product)

    # if product not available just update it
    if product_available == False : 
        return None

    return product


# scrape data from all brands and upload it to mongodb
for brand in brands : 
    name = brand["name"].replace("_" , " ").title()
    brand["name"] = name 
    scrape_brand(brand)

