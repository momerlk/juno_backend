# constantly scrape data from the different websites, update product availabilities 

# use collection scraped_products temporarily for scraping products
# process with gemini and then merge with products collection

import os
import json
import time
from pymongo import MongoClient
from bson import ObjectId
import google.generativeai as genai
import concurrent.futures
from threading import Lock
import pprint
import re
# MongoDB connection details
MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "juno"
COLLECTION_NAME = "products"
PROGRESS_FILE = "progress.json"

# Configure the Gemini API
api_key_codexia = "AIzaSyAMDhR6P2tvj0HUgFoWnaZosHNwN9sQF94"
api_key_genai = "AIzaSyDqrejFnUfci4AauXuAgOIwku0FBac_5Gk"
api_key_bobai = "AIzaSyBdGFOVRTXHx-RLMF2Sr4m1ylm3bP8FzBI"
api_key_learnables = "AIzaSyBLYG1uOII3fbKLoO86_NjE-n_qfWb6RZM"
genai.configure(api_key=api_key_learnables)

batch_size = 20
temperature = 0.13

# Create the model with appropriate configurations
generation_config = {
    "temperature": temperature,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 50000,
    "response_mime_type": "application/json",
}


model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)


chat_session = model.start_chat()

def generate_prompt(data : str) -> str : 
    schema = """{
        category : {broad category of the product e.g "clothes", "shoes", "accessories". should be lower case, no spaces},
        category_type : {specific product_type such as "womens_clothing", "earrings", "mens_shoes"},
        meta_tags: {
            details: { details inferred from description such as fabric, etc. datatype : array[string], max length : 5 },
            product_type : {type of "clothing" or "shoe" etc. can be "three piece summer dress" "two piece suit".},
            garment_type : {is the garment "unstitched", "stitched", if both then add both. datatype : array[string], max_length : 3},
            fabric : {ONLY IF CATEGORY IS CLOTHING/CLOTHES. type of fabric of the product if product is a cloth inferred from description. datatype : string},            
        },
        keywords: { keywords for recommendation. datatype : array[string] },
        audience: {
            price_range: { price range/income class },
            user_type: { type of user }
        }
    }"""

    prompt = f"""
    Using this schema "{schema}", convert this data "{data}" into Product objects.
    1. Extract "user_type" from "description", "title".
    2. Generate "details" from "description".
    3. Infer "keywords", "fabric", "details" for recommendations from the given data.
    4. Infer category, product type and generate data for "category", "product_type" fields according to schema. make sure these fields don't have punctuation or spaces and are lowercase.
    5. Carefully interpret the instructions and descriptions in the schema.
    6. Infer "type" and "garment_type" from "title", "description" of product
    7. I will decode this data inside python so don't use any "" double quotes inside any field data.
    only use single quotes ''. 
    Your(Gemini's) output format is JSON, no javascript or any coding or any other comments.
    """

    return prompt

# TODO : Add previous gemini responses as part of the chat to guarantee sameness and lowercase
# TODO : Add image modality 


def extract_info(products):
    # TODO : Reduce size of data
    data = []
    for product in products : 
        data.append({

            'title': product.get("title"),
            "vendor_title" : product.get("vendor_title"),
            "product_type" : product.get("product_type"),

            "description" : product.get("description"), 

            "price" : product.get("price"),
            "currency" : "PKR",
            "options" : product.get("options"),

            "tags" : product.get("tags"),
        })
    
    prompt = generate_prompt(f"{data}")

    global chat_session
    response = None
    retries = 0
    limit = 4
    # create new chat session after deadline exceeded
    while True : 
        error = False
        try : 
            if retries > 0 :
                chat_session = model.start_chat()
                print(f"starting new model chat session")
                response = chat_session.send_message(prompt)
            else :
                response = chat_session.send_message(prompt)
        except Exception as e :
            
            if str(e).find("finish_reason: RECITATION") != -1  :
                # try to increase temperature so the model doesn't recite training data
                print("recitation error")
                
                return None
            print(f"response error = ") 
            pprint.pprint(e)
            error = True

        if error == False or retries >= limit  : 
            break
        else : 
            retries += 1
            print(f"could not get response trying again after 20 seconds ...")
            time.sleep(20)
    print("response received")


    return response

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as file:
            progress = json.load(file)
            if "last_processed_id" in progress:
                progress["last_processed_id"] = ObjectId(progress["last_processed_id"])
            
            return progress
    return {"last_processed_id": None , "total_requests" : 0}

def save_progress(last_processed_id , total_requests):
    with open(PROGRESS_FILE, "w") as file:
        progress = {"last_processed_id": str(last_processed_id) , "total_requests" : total_requests}
        json.dump(progress, file)



# Initialize MongoDB client
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]
new_collection = db["products_text_features"]

# Load progress
progress = load_progress()
last_processed_id = progress["last_processed_id"]
total_requests = progress["total_requests"]

# Query to fetch products
query = {}
if last_processed_id:
    query["_id"] = {"$gt": last_processed_id}

def rate_limit(last_request_time, requests_in_last_minute):
    now = time.time()
    if last_request_time and (now - last_request_time < 1):
        time.sleep(1 - (now - last_request_time))
    if len(requests_in_last_minute) >= 15:
        sleep_time = 60 - (now - requests_in_last_minute[0])
        if sleep_time > 0:
            time.sleep(sleep_time)
        requests_in_last_minute = requests_in_last_minute[1:]
    now = time.time()  # Update now after potential sleep
    requests_in_last_minute.append(now)
    return now, requests_in_last_minute


def fix_json_errors(json_string):
    # Define a regex pattern to find problematic characters
    problematic_chars_pattern = re.compile(r'[\x00-\x1F\x7F\u2028\u2029]')
    
    # Replace problematic characters with their escaped equivalents
    sanitized_json_string = problematic_chars_pattern.sub(
        lambda x: '\\u{:04x}'.format(ord(x.group(0))), 
        json_string
    )
    
    return sanitized_json_string

def get_description(text : str):

    # after description
    desc_idx = text.find("description")
    if desc_idx == -1 :
        return None, None, None, None
    after_desc = text[desc_idx:len(text)]

    # after colon
    colon_idx = after_desc.find(':')
    after_colon = after_desc[colon_idx+1:len(after_desc)] # text after colon

    #after quotes
    first_quote_idx = after_colon.find('"')
    after_first_quote = after_colon[first_quote_idx+1:len(after_colon)]

    last_quote_idx = after_first_quote.find('"')

    res = after_first_quote[0:last_quote_idx]

    start = desc_idx + colon_idx+1 + first_quote_idx+1
    end = desc_idx + colon_idx+1 + first_quote_idx+1 + last_quote_idx

    return res , start , end , text[end:len(text)]


def process_batch(batch, last_request_time, requests_in_last_minute, total_requests):
    products_list = []
    # process each product before sending to google gemini
    for product in batch : 
        # replace double with single quotes
        # product["description"] = product["description"].replace('"' , "'") 
        products_list.append(product)


    # Rate limiting
    last_request_time, requests_in_last_minute = rate_limit(last_request_time, requests_in_last_minute)

    total_requests += len(batch)
    # Extract information from descriptions
    response = extract_info(products_list)
    if response == None : 
        return last_request_time, requests_in_last_minute , total_requests
    text = response.text.encode().decode('unicode_escape')
    text = text.replace("```json", "").replace("```" , "")


    res, start , end , r_t = get_description(text)
    while res != None : 
        res2 = re.sub(r'(?<!\\)\n', '|/newline|', res)
        text = text.replace(res , res2)
        res, start , end , r_t = get_description(r_t)


    text = re.sub(r'(?<!\\)\n', '', text)
    data_list = None
    try : 
        data_list = json.loads(text)
    except Exception as e : 
        print(f"could not decode response, error = {e}, response :")
        pprint.pprint(text)
        return last_request_time, requests_in_last_minute , total_requests

    # for idx,data in enumerate(data_list):
    #     data_list[idx]["product_type"] = data["product_type"].lower()
    #     data_list[idx]["category"] = data["category"].lower()
    
    new_documents = []

    # Iterate over products and their corresponding extracted data
    for product, data in zip(products_list, data_list):

        try : 
            del data["_id"]
        except Exception as e : 
            e = None 

        # data["description"] = data["description"].replace("|/newline|" , "\n")
        # data["description"] = data["description"].replace("*" , "")
        data["handle"] = product["handle"]
        data["product_id"] = product["product_id"]

        new_documents.append(data)

        # Save progress
        save_progress(product["_id"] , total_requests)

    # Insert new documents into the new collection
    if new_documents:
        res = new_collection.insert_many(new_documents)

    return last_request_time, requests_in_last_minute , total_requests


# TODO : MAKE THE PROMPT SIZE MUCH MUCH MUCH MUCH SMALLER, current size is almost 2800 words

def main(total_requests):
    global batch_size

    last_request_time = 0
    requests_in_last_minute = []
    first_time = True # whether its the first query or not
    session_requests = 0


    print(f"total requests = {total_requests}")

    # TODO : sometimes a smaller batch size works and doesn't give any errors. Implement functionality
    # total products = total requests - 10 
    while True:
        if first_time == False :    
            cursor = collection.find(query).skip(session_requests).sort("_id").limit(batch_size)
        else : 
            first_time = False 
            cursor = collection.find(query).sort("_id").limit(batch_size)
        products_list = list(cursor)

        if not products_list:
            break
        
        last_request_time, requests_in_last_minute , total_requests = process_batch(products_list , last_request_time , requests_in_last_minute, total_requests)  

        print(f"total requests = {total_requests}")
        session_requests += batch_size
        # Check if we reached the daily limit
        if len(requests_in_last_minute) >= 1500:
            print("Daily limit reached, stopping execution.")
            break

    print("Processing complete.")

main(total_requests)