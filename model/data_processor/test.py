import pprint
import re

product = {
    'product_id': 'a74a2b87-04f9-41cf-80b9-d1f5b1cbcd5e',
    'product_url': 'https://www.afrozeh.com/products/mahjabeen-1',
    'shopify_id': 8002372829418,
    'handle': 'mahjabeen-1',
    'title': 'MAHJABEEN-22',
    'vendor': 'afrozeh',
    'vendor_title': 'Afrozeh',
    'category': '',
    'product_type': '',
    'image_url': 'https://cdn.shopify.com/s/files/1/0052/2030/2897/products/5.jpg?v=1668433218',
    'description': (
        'Net Embellished +\xa0Embroidered Front + Back Body (0.66 M)'
        'Net Embellished +\xa0Embroidered Front & Back Panels (14 PCS)'
        'Net Embroidered Sleeves (0.66 Meters)'
        'Net EMBROIDERED SLEEVES BORDER (1 Meters)'
        'Raw Silk Embroidered Sleeves Border (1 Meters)'
        'Raw Silk Embroidered Front + Back Border (4.57 Meters)'
        'Net Embroidered Dupatta 4 Side Border (7.91 Meters)'
        'Net Embroidered Dupatta (2.63 Meters)'
    ),
    'price': '29900',
    'currency': 'PKR',
    'options': [
        {
            'name': 'Type',
            'position': 1,
            'values': ['Unstitched', 'Stitched']
        }
    ],
    'tags': [
        '14-07-2023', '22-07-2023', "22-8-23'", '24-7-2023-SALE',
        'Afrozeh Brides’22', 'Mahjabeen', 'New In', 'Peshwas & Lehngas',
        'products_from_sheet', 'saleafrozehjan', 'xs_xl'
    ],
    'available': True
}

# Pretty print the dictionary
pretty_product = pprint.pformat(product)
print(pretty_product)

# Function to count tokens
def count_tokens(string):
    # Split the string by any whitespace or punctuation
    tokens = re.findall(r'\w+|[^\w\s]', string, re.UNICODE)
    return len(tokens)

# Count the tokens in the pretty-printed dictionary
token_count = count_tokens(pretty_product)

print(f"Number of tokens: {token_count}")