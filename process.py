import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer
import tensorflow as tf
from tensorflow.keras.layers import Hashing
from sklearn.metrics.pairwise import cosine_similarity
from pymongo import MongoClient

local_db_server = "mongodb://localhost:27017/"
online_db_server = 'mongodb+srv://swift:swift@hobby.nzyzrid.mongodb.net/'
MONGO_URI = local_db_server
DATABASE_NAME = 'juno'
COLLECTION_NAME = 'products'

tf.get_logger().setLevel('FATAL')


def preprocess_data(schema, data_param):
    data = data_param
    # Initialize a MinMaxScaler for numerical normalization
    scaler = MinMaxScaler()
    
    # Initialize a Hashing layer for categorical fields
    hashing_layer = Hashing(num_bins=10, salt=133)  # Adjust num_bins as needed
    
    # Initialize a TF-IDF Vectorizer for text fields
    tfidf_vectorizer = TfidfVectorizer(max_features=1000)  # Adjust max_features as needed
    text_data = [item[field] for field, ftype in schema.items() if ftype == 'text' for item in data]
    tfidf_vectorizer.fit(text_data)
    
    # Separate fields by type
    categorical_fields = [field for field, ftype in schema.items() if ftype == 'categorical']
    numerical_fields = [field for field, ftype in schema.items() if ftype == 'numerical']
    text_fields = [field for field, ftype in schema.items() if ftype == 'text']
    
    # Process each field type
    for field in categorical_fields:
        # Collect categorical data
        categorical_data = np.array([[item[field]] for item in data])
        # Hash categorical data using Hashing layer
        hashed_data = hashing_layer(categorical_data)
        # Update data with hashed values
        for i, item in enumerate(data):
            item[field] = hashed_data[i, 0].numpy()  # Convert tensor to numpy array
    
    if numerical_fields:
        # Collect numerical data
        numerical_data = np.array([[item[field] for field in numerical_fields] for item in data], dtype=float)
        # Fit and transform the data
        normalized_data = scaler.fit_transform(numerical_data)
        # Update data with normalized values
        for i, item in enumerate(data):
            for j, field in enumerate(numerical_fields):
                item[field] = normalized_data[i, j]
    
    for field in text_fields:
        # Vectorize text data using TF-IDF Vectorizer
        text_data = tfidf_vectorizer.transform([item[field] for item in data]).toarray()
        # Update data with vectorized text data
        for i, item in enumerate(data):
            item[field] = text_data[i]
    
    return data


def create_feature_vector(schema, item):
    # Separate fields by type
    other_fields = [field for field, ftype in schema.items() if ftype != "text"]
    text_fields = [field for field, ftype in schema.items() if ftype == 'text']

    other_data = []
    text_data = []

    for field in other_fields:
        other_data.append(np.array([item[field]]))
    for field in text_fields:
        text_data.append(item[field])

    feature_vector = np.concatenate([
        *other_data,
        *text_data,
    ])

    return feature_vector


def weighted_sum(features, ratings):
    """
    Compute weighted sum of features based on ratings.

    Parameters:
    - features: numpy array of shape (n_items, n_features) containing feature vectors of items.
    - ratings: numpy array of shape (n_items,) containing ratings for each item.

    Returns:
    - numpy array representing the weighted sum feature vector.
    """
    normalized_ratings = ratings / np.sum(ratings)  # Normalize ratings to sum to 1
    weighted_features = np.zeros(features.shape[1])  # Initialize weighted sum vector
    
    for i in range(len(ratings)):
        weighted_features += features[i] * normalized_ratings[i]  # Weighted sum based on normalized ratings
    
    return weighted_features


def similarity(feature_vector1, feature_vector2):
    """
    Compute cosine similarity between two feature vectors.

    Parameters:
    - feature_vector1: numpy array representing the first feature vector.
    - feature_vector2: numpy array representing the second feature vector.

    Returns:
    - Cosine similarity between feature_vector1 and feature_vector2.
    """
    similarity_score = cosine_similarity([feature_vector1], [feature_vector2])[0][0]
    return similarity_score


def rank(weighted_sum_vector, features_vectors):
    """
    Rank feature vectors based on cosine similarity to a weighted sum vector.

    Parameters:
    - weighted_sum_vector: numpy array representing the weighted sum feature vector.
    - features_vectors: numpy array of shape (n_items, n_features) containing feature vectors of items to rank.

    Returns:
    - List of indices of feature vectors in features_vectors, ranked in descending order of similarity to weighted_sum_vector.
    """
    similarities = []
    
    for feature_vector in features_vectors:
        sim = similarity(weighted_sum_vector, feature_vector)
        similarities.append(sim)
    
    # Rank indices based on similarity (higher similarity first)
    ranked_indices = np.argsort(similarities)[::-1]
    
    return ranked_indices


def create_preference_profile(features_obj, ratings):
    user_rated_features = []
    user_ratings = []
    for product_id, rating in ratings.items():
        user_rated_features.append(features_obj[product_id])
        user_ratings.append(rating)

    user_rated_features = np.array(user_rated_features)
    user_ratings = np.array(user_ratings)

    user_profile = weighted_sum(user_rated_features, user_ratings)

    return user_profile


def recommend(data, features_obj, user_profile, k):
    similarities = []
    for item in data:
        product_id = item['product_id']
        feature_vector = features_obj[product_id]
        sim = similarity(user_profile, feature_vector)
        similarities.append((sim, item))

    # Sort by similarity score in descending order and get top k items
    similarities.sort(reverse=True, key=lambda x: x[0])
    recommendations = [item for _, item in similarities[:k]]

    return recommendations


# Example usage
schema = {
    'vendor': 'categorical',
    'title': 'text',
    'price': 'numerical',
    'description': 'text',
}

items_data = []
items_data2 = []

client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

for item in collection.find({}):
    item = {
        "product_id" : item["product_id"],
        "vendor" : item["vendor"],
        "title" : item["title"],
        "price" : item["price"],
        "description" : item["description"],
    }
    items_data.append(item)

data = preprocess_data(schema, items_data)

# Example feature vectors (concatenating all features into a single vector)
features_obj = {}
for item in data:
    feature_vector = create_feature_vector(schema, item)
    features_obj[item["product_id"]] = feature_vector

print("calculated features")

user_ratings = {"742b2a0d-fa45-4e47-97ba-249b6e8e2839": 0.1, "b06c0d15-1127-4d7e-9435-46f240f68011": 0.1, "25f3fe1e-e63f-45cc-a90b-01a35146f57b": 0.8}
user_profile = create_preference_profile(features_obj, user_ratings)

items_data2 = []

for item in collection.find({}):
    item = {
        "product_id" : item["product_id"],
        "vendor" : item["vendor"],
        "title" : item["title"],
        "price" : item["price"],
        "description" : item["description"],
    }
    items_data2.append(item)

# Get top 3 recommendations
recommendations = recommend(items_data2, features_obj, user_profile, 3)
for rec in recommendations : 
    print(rec["title"], rec["vendor"])
