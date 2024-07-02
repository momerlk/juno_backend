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

# MongoDB connection details
local_db_server = "mongodb://localhost:27017/"
online_db_server = 'mongodb+srv://swift:swift@hobby.nzyzrid.mongodb.net/'
MONGO_URI = local_db_server
DATABASE_NAME = 'swift'
COLLECTION_NAME = 'products'

# Path to the directory containing JSON files
DIRECTORY_PATH = './data'

base_urls = {
    "afrozeh.json" : "https://www.afrozeh.com",
    "ali_xeeshan.json" : "https://alixeeshanempire.com",
    "alkaram_studio.json" : "https://www.alkaramstudio.com",
    "asim_jofa.json" : "https://asimjofa.com",
    "beechtree.json" : "https://beechtree.pk",
    "bonanza_satrangi.json" : "https://bonanzasatrangi.com",
    "chinyere.json" : "https://chinyere.pk",
    "cross_stitch.json" : "https://www.crossstitch.pk",
    "edenrobe.json" : "https://edenrobe.com",
    "ethnic.json" : "https://pk.ethnc.com",
    "faiza_saqlain.json" : "https://www.faizasaqlain.pk",
    "generation.json" : "https://generation.com.pk",
    "hem_stitch.json" : "https://www.hemstitch.pk",
    "hussain_rehar.json" : "https://www.hussainrehar.com",
    "kanwal_malik.json" : "https://www.kanwalmalik.com",
    "kayseria.json" : "https://www.kayseria.com",
    "limelight.json" : "https://www.limelight.pk",
    "maria_b.json" : "https://www.mariab.pk",
    "mushq.json" : "https://www.mushq.pk",
    "nishat_linen.json" : "https://nishatlinen.com",
    "sadaf_fawad_khan.json" : "https://sadaffawadkhan.com",
    "saira_shakira_usd.json" : "https://www.sairashakira.com",
    "sapphire.json" : "https://pk.sapphireonline.pk",
    "zaha.json" : "https://www.zaha.pk",
    "zara_shah_jahan.json" : "https://zarashahjahan.com",
    "zellbury.json" : "https://zellbury.com",
}

def upload_to_mongo(db, collection, data):
    collection.insert_one(data)

def extract_fields(json_data , fname):

    description = json_data.get("body_html")

    if description == None or description == "" : 
        return None

    try : 
        # TODO : change preprocess to just remove html tags. 
        description = preprocess_text(description)
    except Exception as e : 
        print(f"failed to preprocess description, error = {e}, description = {description}")


    available = False

    variant_index = 0

    for idx, variant in enumerate(json_data.get("variants")) : 
        first_dig = variant["price"].split(".")[0][0]
        if first_dig == "0" : 
            return None
        available = variant["available"]
        if available == True : 
            variant_index = idx
            break

    if available == False : 
        return None


    variant = json_data.get("variants")[variant_index] 

    url = f"{base_urls[fname]}/products/{json_data.get("handle")}"
    vendor = fname.split(".")[0]
    price = variant["price"].split(".")[0]
    images = json_data.get("images")
    if len(images) == 0 : 
        return None 
    image_url = images[0]["src"]

    
    

    product =  {
        'product_id': str(uuid.uuid4()),
        'product_url' : url,
        "shopify_id" : json_data.get("id"),

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
        "currency" : "PKR",

        "options" : json_data.get("options"),
        "tags" : json_data.get("tags"),
        "available" : True,
    }


    return product

def process_files(directory_path):
    
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]

    uploaded = 0

    for filename in os.listdir(directory_path):
        if filename.endswith('.json'):
            file_path = os.path.join(directory_path, filename)

            with open(file_path, 'r') as json_file:
                try:
                    json_data = json.load(json_file)
                    for item in json_data : 
                        extracted_data = extract_fields(item, file_path)
                        if extracted_data != None : 
                            try : 
                                upload_to_mongo(db,collection,extracted_data)
                            except Exception as e : 
                                print(f"failed to upload data to mongoDB, error : {e} , data = {extracted_data}")
                                continue 
                            uploaded+=1

                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON from file {file_path}: {e}")
            print(f"uploaded {uploaded} documents to mongoDB")

def main():
    process_files(DIRECTORY_PATH)

# INCORRECT PRICING IN A LOT OF PRODUCTS THAT DON"T HAVE PRICING ESPECIALLY IN BRIDALWEAR
if __name__ == '__main__':
    main()