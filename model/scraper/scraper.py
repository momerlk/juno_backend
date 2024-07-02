import requests
from bs4 import BeautifulSoup
import uuid
import json
import numpy as np


def remove_query_params(url):
    # Find the index of '.jpg' in the URL
    jpg_index = url.find('.jpg')
    
    # If '.jpg' is found, return the substring up to '.jpg', otherwise return the original URL
    if jpg_index != -1:
        return url[:jpg_index + 4]  # Add 4 to include the '.jpg' extension
    else:
        return url


def scrape_website(url , title , company):
    # Send a GET request to the URL
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all product items
        product_items = soup.find_all('div', class_='product-item-info')
        
        # List to store dictionaries of scraped data
        scraped_data = []
        
        # Iterate over each product item
        for item in product_items:
            # Initialize dictionary to store data for this item
            item_data = {}
            item_data["id"] = str(uuid.uuid4())
            item_data["title"] = title
            item_data["company"] = company

            
            # Extract URL
            url_element = item.find('a', href=True)
            if url_element:
                url = url_element['href']
                if url == "#" : 
                    continue # moves to next iteration
                item_data['url'] = url
                
            
            # Extract price
            price_element = item.find('span', class_='price')
            if price_element:
                price = price_element.text.strip()
                item_data['price'] = price
                if price == "PKR 0.00" : 
                    item_data['price'] = "TBD"
            
            # Extract image source
            image_element = item.find('img', class_='product-image-photo', src=True)
            if image_element:
                image_src = image_element['src']
                item_data['image'] = remove_query_params(image_src)
            
            # Append item data to the list
            if item_data:
                scraped_data.append(item_data)
        
        return scraped_data
    else:
        # Request was not successful
        print("Failed to retrieve data from the website")
        return None




def scrape_and_save(url, title , company):
    scraped_data = scrape_website(url , title, company)

    with open('data.json', 'r') as json_file:
        existing_data = json.load(json_file)

    # Append scraped data to existing data
    if scraped_data:
        existing_data.extend(scraped_data)

    # Write updated data back to the JSON file
    with open('data.json', 'w') as json_file:
        json.dump(existing_data, json_file, indent=4)

    return len(scraped_data)

def scrape_collection(url, title, brand, total_pages) : 
    total_items = 0

    for i in range(1,total_pages+1):
        url = f"{url}?p={i}"
        n = scrape_and_save(url , title , brand)
        total_items += n

    print(f"total items = {total_items}")


def load_json(file_path: str):
    # Load the JSON data from the file
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    return data

from lxml import html


def scrape_product_details(url):
    # Send a GET request to the URL
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to retrieve data from the website: {url}")
        return None

    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract product description
    description_div = soup.find('div', itemprop='description')
    description = description_div.get_text("\n", strip=True) if description_div else "No description available"
    
    # Extract sizes using the JS path equivalent
    sizes_container = soup.select_one("#product-options-wrapper > div > div > div.swatch-attribute.size > div")
    sizes = []
    print(f"sizes container = {sizes_container}")
    if sizes_container:
        size_elements = sizes_container.find_all('div', class_='swatch-option')
        for size_element in size_elements:
            size = size_element.get_text(strip=True)
            sizes.append(size)

    # Return the scraped data
    product_details = {
        'url': url,
        'description': description,
        'sizes': sizes
    }
    
    return product_details

from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_and_parse(session, item):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    # Send a GET request to the URL with proper headers
    response = session.get(item["url"], headers=headers)

    product_details = item
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to retrieve data from the website: {url}")
        return None

    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract product description
    description_div = soup.find('div', itemprop='description')
    description = description_div.get_text("\n", strip=True) if description_div else "No description available"
    
    # Extract sizes
    sizes_div = soup.find('div', class_='swatch-attribute-options')
    sizes = [size.get_text(strip=True) for size in sizes_div.find_all('div', class_='swatch-option')] if sizes_div else []


    product_details["description"] = description
    product_details["sizes"] = sizes
    
    return product_details

def concurrent_scrape(products, max_workers=10):
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        with requests.Session() as session:
            # Submit all tasks
            futures = [executor.submit(fetch_and_parse, session, product) for product in products]
            
            # Process completed tasks
            for future in as_completed(futures):
                result = future.result()
                if result:
                    results.append(result)
                    print("result gotten")
    
    return results

# arr = load_json("data.json")
# print(len(arr))

# new_data = np.array([])
# for i, item in enumerate(arr):
#     new_item = item
#     details = scrape_product_details(new_item["url"])
#     new_item["description"] = details["description"]
#     if len(details["sizes"]) == 0 : 
#         details["sizes"] = ["sizes not available"]
#     new_item["sizes"] = details["sizes"]

#     new_data = np.append(new_data , new_item)

#     print(f"items scraped = ${i+1}")

# new_data = concurrent_scrape(arr , max_workers=20)

# with open("new_data.json" , "w") as file : 
#     json.dump(new_data, file, indent=4)

print(scrape_product_details("https://www.sanasafinaz.com/pk/ss24ese214p2t-ss24ese214p2t.html"))

# url_to_scrape = "https://www.sanasafinaz.com/pk/luxury-pret.html"  
# pages = 1
# collection_title = "Luxury Pret"
# collection_brand = "Sana Safinaz"

# scrape_collection(url_to_scrape, collection_title, collection_brand , pages)

