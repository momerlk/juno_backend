image_urls = ["https://cdn.shopify.com/s/files/1/0252/1160/0992/files/WhatsAppImage2024-06-04at21.34.09.jpg?v=1717588739","https://cdn.shopify.com/s/files/1/0252/1160/0992/files/WhatsAppImage2024-06-04at21.34.09_1.jpg?v=1717588754","https://cdn.shopify.com/s/files/1/0252/1160/0992/files/WhatsAppImage2024-06-04at21.34.11.jpg?v=1717588754","https://cdn.shopify.com/s/files/1/0252/1160/0992/files/WhatsAppImage2024-06-04at21.34.10_2.jpg?v=1717588754","https://cdn.shopify.com/s/files/1/0252/1160/0992/files/WhatsAppImage2024-06-04at21.34.10_1.jpg?v=1717588754","https://cdn.shopify.com/s/files/1/0252/1160/0992/files/WhatsAppImage2024-06-04at21.34.10.jpg?v=1717588754","https://cdn.shopify.com/s/files/1/0252/1160/0992/files/WhatsAppImage2024-06-04at21.34.09_2.jpg?v=1717588754"]

import cv2
import numpy as np
import requests
from moviepy.editor import ImageSequenceClip
from io import BytesIO
from PIL import Image

def download_image(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img = img.convert('RGB')  # Ensure the image is in RGB format
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)  # Convert RGB to BGR for OpenCV

def apply_pan_effect(image, zoom_in=True, duration=2, fps=30, aspect_ratio=(9, 16)):
    height, width, _ = image.shape
    ar_width, ar_height = aspect_ratio
    target_height = height
    target_width = int(target_height * ar_width / ar_height)
    
    # Crop the image to the desired aspect ratio
    if width > target_width:
        x_offset = (width - target_width) // 2
        image = image[:, x_offset:x_offset+target_width]
    else:
        target_width = width
        target_height = int(target_width * ar_height / ar_width)
        y_offset = (height - target_height) // 2
        image = image[y_offset:y_offset+target_height, :]

    height, width, _ = image.shape
    zoom_factor = 1.2 if zoom_in else 0.8
    num_frames = duration * fps
    frames = []

    for i in range(num_frames):
        scale = 1 + (zoom_factor - 1) * (i / num_frames)
        center_x, center_y = width // 2, height // 2
        new_width = int(width / scale)
        new_height = int(height / scale)

        x1 = max(0, center_x - new_width // 2)
        y1 = max(0, center_y - new_height // 2)
        x2 = min(width, center_x + new_width // 2)
        y2 = min(height, center_y + new_height // 2)

        cropped_img = image[y1:y2, x1:x2]
        resized_img = cv2.resize(cropped_img, (width, height))

        resized_img = cv2.cvtColor(np.array(resized_img), cv2.COLOR_BGR2RGB)  # Convert RGB to BGR for OpenCV

        frames.append(resized_img)

    return frames

def create_slideshow(image_urls, output_path, duration_per_image=2, fps=30, aspect_ratio=(9, 16)):
    all_frames = []
    zoom_in = True

    for image_url in image_urls:
        image = download_image(image_url)
        frames = apply_pan_effect(image, zoom_in=zoom_in, duration=duration_per_image, fps=fps, aspect_ratio=aspect_ratio)
        all_frames.extend(frames)
        zoom_in = not zoom_in

    clip = ImageSequenceClip(all_frames, fps=fps)
    clip = clip.resize(height=1920)  # Resize to vertical height (1080x1920)
    clip.write_videofile(output_path, codec='libx264')


output_path = 'vertical_slideshow.mp4'
create_slideshow(image_urls, output_path)
