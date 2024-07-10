import tensorflow as tf
from tensorflow.keras.applications import InceptionV3
from tensorflow.keras.applications.inception_v3 import preprocess_input
from tensorflow.keras.preprocessing import image
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Load the pre-trained model
model = InceptionV3(weights='imagenet', include_top=False, pooling='avg')

# Function to get embeddings
def image_to_embedding(image_path):
    img = image.load_img(image_path, target_size=(299, 299))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    
    # Extract features
    features = model.predict(img_array)
    return features

# Function to compare two images
def image_compare(image_path1, image_path2):
    embedding1 = image_to_embedding(image_path1)
    embedding2 = image_to_embedding(image_path2)
    
    # Compute cosine similarity
    similarity = cosine_similarity(embedding1, embedding2)
    
    return similarity[0][0]

# Example usage
similarity_score = image_compare('./1.jpg', './harvard.jpg')
print(f"Similarity Score: {similarity_score}")
