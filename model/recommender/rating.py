import json
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


with open('/Users/ayanbinrafaih/swift_api/model/recommender/user_interactions.json', 'r') as f:
    data = json.load(f)


def flatten_json(y):
    out = {}
    def flatten(x, name=''):
        if isinstance(x, dict):
            for a, b in x.items():
                flatten(b, name + a + '_')
        else:
            out[name[:-1]] = x
    flatten(y)
    return out

flattened_data = [flatten_json(user_data) for user_data in data]
df = pd.DataFrame(flattened_data)
print(df.columns)


action_type_weights = {
    'Liked': 3,
    'Disliked': -1,
    'Added_to_Cart': 2,
    'Image_viewed_with_Interest': 1.5,
    'Purchase': 6,
    'Checkout': 2.5,
    'Clicks': 0.5,
    'Read more': 0.7,
    'share': 1.2,
    'Check Website': 0.8,
    'View Related Products': 0.9,
    'Filter_click': 0.6,
    'App Quit': -1
}

duration_weights = {
    '> 10 seconds': 0.5,
    '> 25 seconds': 1.5,
    '> 40 seconds': 2.5,
    '> 60 seconds': 3
}


def compute_weighted_action(actions):
    if isinstance(actions, list):
        return sum(action_type_weights.get(action, 0) for action in actions)
    return 0

def compute_weighted_duration(durations):
    if isinstance(durations, list):
        return sum(duration_weights.get(duration, 0) for duration in durations)
    return 0


df['action_type_weighted'] = df['user1_action_type'].apply(compute_weighted_action)
df['action_duration_weighted'] = df['user1_action_duration'].apply(compute_weighted_duration)
df['num_pics_scrolled'] = df['user1_num_pics_scrolled'].str.replace('%', '').astype(float) / 100
df['time_spent_compared_to_average'] = df['user1_time_spent_compared_to_average'].str.replace('%', '').astype(float) / 100
df['num_pics_scrolled'].fillna(0, inplace=True)
df['time_spent_compared_to_average'].fillna(0, inplace=True)
df['raw_rating'] = (df['action_type_weighted'] * df['action_duration_weighted'] * df['num_pics_scrolled'] * df['time_spent_compared_to_average']) / 4


scaler = MinMaxScaler()
df['normalized_rating'] = scaler.fit_transform(df[['raw_rating']])
result_df = df[['user1_user_id', 'normalized_rating']]
result = result_df.to_dict(orient='records')
with open('/Users/ayanbinrafaih/swift_api/model/recommender/result.json', 'w') as f:
    json.dump(result, f, indent=4)

print(result_df)
