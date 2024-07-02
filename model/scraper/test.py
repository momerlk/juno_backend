import requests

def download_image(url, filename="test_image.jpg"):
    # Send a GET request to the URL
    response = requests.get(url, stream=True)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Open a file with the specified filename and write the image content to it
        with open(filename, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        print(f"Image successfully downloaded: {filename}")
    else:
        print("Failed to retrieve the image")

# Example usage:
image_url = "https://cdn.shopify.com/s/files/1/0595/3260/7535/files/WUW23X30679-1_ef58f3fb-c0ad-4c8d-aced-1ce53b4bb1fc.jpg?v=1714462837"
download_image(image_url)
