import json
import pandas as pd

# Define the path to your JSON file
file = './user_interactions.json'

# Open the JSON file and load it into a Python dictionary
with open(file) as train_file:
    dict_train = json.load(train_file)

# Convert the dictionary to a pandas DataFrame
train = pd.DataFrame.from_dict(dict_train, orient='index')

# Reset the index to move the index (which is typically the keys from the JSON) to a column
train.reset_index(level=0, inplace=True)


# Display the DataFrame to verify
print(train.head())
