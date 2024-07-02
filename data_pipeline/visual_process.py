"""

product_type :{type of the product e.g "womens_clothing", "mens_clothing", "mens_shoes". should be lower case, no spaces},

AUDIENCE
gender: { target gender. datatype : string. },
interests: { customer interests },
age_range: { target age range. datatype : integer tuple of min age and max age.},

META_TAGS
garment_type: { type of garment. datatype : string.},
style: { style of the product. datatype : string },

"""

import google.generativeai as genai 

# Configure the Gemini API
api_key3="AIzaSyAhxlU5AY65UMbEz8Hjbl0f_NKoyMOdyMc"
api_key2 = "AIzaSyDbBPvp_zDgCg9SQX5cB6WGu_uSmtK2Mug"
api_key="AIzaSyDygoL3bOf112GeBPKp_xDyAcmjK7VEm8s"
genai.configure(api_key=api_key)

import requests
import shutil

# Function to download and resize image from URL and save locally
def download_and_process_image(url, save_path, max_size=(1024, 1024)):
    try:
        # Download image from URL
        response = requests.get(url, stream=True)
        if response.status_code != 200:
            print(f"Failed to download image from {url}. Status code: {response.status_code}")
            return False

        # Open a local file to write the downloaded image
        with open(save_path, 'wb') as file:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, file)

        # Optionally resize the image (basic resizing example)
        # You can implement your own resizing logic here if needed

        return True
    except Exception as e:
        print(f"Error processing image: {e}")
        return False

image_url = "https://cdn.pixabay.com/photo/2014/06/03/19/38/board-361516_640.jpg"
local_file_path = image_url.replace("https://" , "").replace("/" , ".")


if download_and_process_image(image_url, local_file_path):
    sample_file = genai.upload_file(path=local_file_path,
                                display_name="Sample drawing")

    file = genai.get_file(name=sample_file.name)
    print(f"Retrieved file '{file.display_name}' as: {sample_file.uri}")