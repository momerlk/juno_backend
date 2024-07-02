import numpy as np

# Define user data
user_data = {
    "_id": {
        "$oid": "665a161d2bda72febe9c6262"
    },
    "user_id": "96e93c9b-8252-4639-bd0e-9d6f166dcc84",
    "user_ethnicity": [
        "Pakistani",
        "Indian",
        "Middle-Eastern",
        "Western"
    ],
    "user_demographics": [
        "Lahore",
        "Karachi",
        "Islamabad",
        "Peshawar"
    ],
    "language": "Urdu",
    "Occupation": "Occupied",
    "Income Level": "50000",
    "Search-History": {},
    "Product-History": {},
    "favourite_product_categories": "Bridal Wear",
    "shopping_behaviour": {
        "shopping frequency": "10 products per month",
        "money_spent_per_month": "10000",
        "Average_product_price_for_purchase": "3000",
        "Most_frequent_category_clothes": "Bridal",
        "user_buying trends": {
            "User_activity": "Month",
            "Duration_between_purchase": "40 days"
        }
    },
    "most_active_time": "23:00",
    "session_intent": {
        "occasion": "Wedding",
        "Category": ["Shoes", "Clothes", "Accessories"]
    },
    "num_bought_occasion": {},
    "averagetime_product": "23 seconds",
    "averagetime_day": "3 hours",
    "totaltime_week": "10 hours",
    "totaltime_overall": "14 hours",
    "most_active_day": "Monday",
    "least_active_day": "Sunday"
}

# Preprocess and encode categorical variables
def encode_categorical(data):
    encoded_data = []
    for key, value in data.items():
        if isinstance(value, dict):
            # Recursively encode nested dictionaries
            encoded_data.extend(encode_categorical(value))
        elif isinstance(value, list):
            # Encode list elements as separate features
            for item in value:
                encoded_data.append(str(key) + '_' + str(item))
        else:
            # Encode non-list values directly
            encoded_data.append(str(key) + '_' + str(value))
    return encoded_data

encoded_user_data = encode_categorical(user_data)

# Define numerical features
numerical_features = [
    'shopping_frequency',
    'money_spent_per_month',
    'average_product_price_for_purchase',
    'duration_between_purchase',
    'averagetime_product',
    'averagetime_day',
    'totaltime_week',
    'totaltime_overall'
]

# Extract numerical values from user_data
numerical_values = [
    user_data['shopping_behaviour']['shopping frequency'],
    user_data['shopping_behaviour']['money_spent_per_month'],
    user_data['shopping_behaviour']['Average_product_price_for_purchase'],
    user_data['shopping_behaviour']['user_buying trends']['Duration_between_purchase'],
    user_data['averagetime_product'],
    user_data['averagetime_day'],
    user_data['totaltime_week'],
    user_data['totaltime_overall']
]

# Convert numerical values to floats
numerical_values = [float(value.split(' ')[0]) for value in numerical_values]

# Combine categorical and numerical features
all_features = encoded_user_data + numerical_features
all_values = encoded_user_data + numerical_values

# Create a matrix from the features and values
user_matrix = np.array(all_values).reshape(1, -1)

print("User matrix:")
print(user_matrix)
print("Shape:", user_matrix.shape)