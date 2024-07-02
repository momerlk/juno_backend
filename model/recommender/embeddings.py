import pandas as pd
import json

# Load JSON data
user_data = json.load(open('user_data.json'))
product_data = json.load(open('products_data.json'))

# Convert to DataFramex
user_df = pd.DataFrame(user_data)
product_df = pd.DataFrame(product_data)

from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer

# TODO : Conform to the data model in the mongodb database

# One-hot encode categorical features
encoder = OneHotEncoder()
user_preferences = encoder.fit_transform(user_df['preferences'].apply(lambda x: ' '.join(x)).values.reshape(-1, 1)).toarray()
product_category = encoder.fit_transform(product_df['category'].values.reshape(-1, 1)).toarray()

# Normalize numerical features
scaler = StandardScaler()
product_price = scaler.fit_transform(product_df['price'].values.reshape(-1, 1))

# # Vectorize text features
vectorizer = TfidfVectorizer()
product_description = vectorizer.fit_transform(product_df['description']).toarray()

# # Combine features
user_features = pd.concat([user_df[['user_id']], pd.DataFrame(user_preferences)], axis=1)
product_features = pd.concat([product_df[['product_id']], pd.DataFrame(product_category), pd.DataFrame(product_price), pd.DataFrame(product_description)], axis=1)


import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Embedding, Flatten, Dot, Dense

# User and product embedding layers
user_input = Input(shape=(1,))
user_embedding = Embedding(input_dim=user_df.shape[0], output_dim=50)(user_input)
user_vec = Flatten()(user_embedding)

product_input = Input(shape=(1,))
product_embedding = Embedding(input_dim=product_df.shape[0], output_dim=50)(product_input)
product_vec = Flatten()(product_embedding)

# Dot product of user and product embeddings
dot_product = Dot(axes=1)([user_vec, product_vec])

# Build and compile the model
model = Model([user_input, product_input], dot_product)
model.compile(optimizer='adam', loss='mean_squared_error')

# Train the model
# Note: You need interaction data (e.g., ratings) for training
interactions = None # Load interactions data from actions collection in database
model.fit([interactions['user_id'], interactions['product_id']], interactions['rating'], epochs=10)
