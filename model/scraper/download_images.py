import os
import json
import uuid
import aiohttp
import aiofiles
import asyncio
from pathlib import Path
from PIL import Image
from io import BytesIO

# Create directories if they don't exist
Path("./images").mkdir(parents=True, exist_ok=True)
Path("./data").mkdir(parents=True, exist_ok=True)

MAX_CONCURRENT_DOWNLOADS = 8
RETRY_LIMIT = 0
TARGET_SIZE = (800, 800)  # Target size for resizing the images

sem = asyncio.Semaphore(MAX_CONCURRENT_DOWNLOADS)

async def download_image(session, url, filename, retries=RETRY_LIMIT):
    async with sem:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    image_data = await response.read()
                    image = Image.open(BytesIO(image_data))
                    image.thumbnail(TARGET_SIZE, Image.Resampling.LANCZOS)
                    
                    async with aiofiles.open(filename, mode='wb') as f:
                        image.save(f, format='JPEG')
                    
                    print(f"Image successfully downloaded and resized: {filename}")
                else:
                    print(f"Failed to retrieve image from {url}, status code: {response.status}")
                    if retries > 0:
                        print(f"Retrying... ({RETRY_LIMIT - retries + 1}/{RETRY_LIMIT})")
                        await download_image(session, url, filename, retries - 1)
        except Exception as e:
            print(f"Error downloading {url}: {e}")
            if retries > 0:
                print(f"Retrying... ({RETRY_LIMIT - retries + 1}/{RETRY_LIMIT})")
                await download_image(session, url, filename, retries - 1)

async def process_product(session, json_fname,  product, image_tasks):
    split_fname = json_fname.split("/")
    vendor_name = split_fname[len(split_fname)-1]

    handle = product["handle"]

    if len(product["images"]) == 0:
        return

    image = product["images"][0]
    image_url = image['src']
    image_filename = f"./images/file'{vendor_name}'-handle'{handle}'.jpg"

    try:
        image_tasks.append(download_image(session, image_url, image_filename))
    except Exception as e:
        print(f"Error when adding image task: {e}")

async def process_json_file(session, json_file, image_tasks):
    async with aiofiles.open(json_file, mode='r') as f:
        content = await f.read()
        try:
            products = json.loads(content)
        except Exception as e:
            print(f"Couldn't load JSON file, error: {e}")
            return
        
        for product in products:
            await process_product(session, json_file, product, image_tasks)

async def main():
    json_files = [f"./data/{file}" for file in os.listdir("./data") if file.endswith('.json')]

    async with aiohttp.ClientSession() as session:
        image_tasks = []
        for json_file in json_files:
            await process_json_file(session, json_file, image_tasks)

        await asyncio.gather(*image_tasks)

asyncio.run(main())
