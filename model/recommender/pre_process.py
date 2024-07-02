import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from bs4 import BeautifulSoup


def preprocess_text(text):
    # Remove HTML tags
    text = BeautifulSoup(text, "html.parser").get_text()

    # Convert to lowercase
    text = text.lower()

    # Remove special characters and digits
    text = re.sub(r'[^a-zA-Z\s]', '', text)

    # Tokenization
    tokens = word_tokenize(text)

    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]

    # Lemmatization
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]

    # Join tokens back into a string
    preprocessed_text = ' '.join(tokens)

    return preprocessed_text

# Example HTML content
html_content = """
<p><strong></strong><strong>Product Description:</strong></p>\n<style type=\"text/css\"><!--\ntd {border: 1px solid #ccc;}br {mso-data-placement:same-cell;}\n--></style>\n<style type=\"text/css\"><!--\ntd {border: 1px solid #ccc;}br {mso-data-placement:same-cell;}\n--></style>\n<style type=\"text/css\"><!--\ntd {border: 1px solid #ccc;}br {mso-data-placement:same-cell;}\n--></style>\n<style type=\"text/css\"><!--\ntd {border: 1px solid #ccc;}br {mso-data-placement:same-cell;}\n--></style>\n<div style=\"text-align: left;\" data-mce-style=\"text-align: left;\">\n<div style=\"text-align: left;\" data-mce-style=\"text-align: left;\">\n<div style=\"text-align: left;\" data-mce-style=\"text-align: left;\">\n<div style=\"text-align: left;\" data-mce-style=\"text-align: left;\">\n<div style=\"text-align: left;\" data-mce-style=\"text-align: left;\">\n<div style=\"text-align: left;\" data-mce-style=\"text-align: left;\">\n<div style=\"text-align: left;\" data-mce-style=\"text-align: left;\">\n<p><span style=\"font-size: 0.875rem;\">A pure raw silk base in teal serves as a canvas to shimmery gold and silver hand embellishments. This lehenga and choli is incrusted with gotta, naqshi, dabka, resham, sequins and pearls. It is paired up with an exquisite net dupatta made with patch work, aari work and hand embellishments.</span><br></p>\n<p><span style=\"font-size: 0.875rem;\"><strong>No. of Pieces: </strong>3</span></p>\n</div>\n</div>\n</div>\n</div>\n</div>\n</div>\n</div>\n<p><strong>Fabric:</strong>\u00a0<br></p>\n<style type=\"text/css\"><!--td {border: 1px solid #cccccc;}br {mso-data-placement:same-cell;}--></style>\n<style type=\"text/css\"><!--td {border: 1px solid #cccccc;}br {mso-data-placement:same-cell;}--></style>\n<style type=\"text/css\"><!--td {border: 1px solid #cccccc;}br {mso-data-placement:same-cell;}--></style>\n<style type=\"text/css\"><!--td {border: 1px solid #cccccc;}br {mso-data-placement:same-cell;}--></style>\n<style type=\"text/css\"><!--td {border: 1px solid #cccccc;}br {mso-data-placement:same-cell;}--></style>\n<ul>\n<li><span data-sheets-userformat='{\"2\":1023,\"3\":{\"1\":2,\"2\":\"#,##0\",\"3\":1},\"4\":{\"1\":2,\"2\":16777215},\"5\":{\"1\":[{\"1\":2,\"2\":0,\"5\":{\"1\":2,\"2\":0}},{\"1\":0,\"2\":0,\"3\":3},{\"1\":1,\"2\":0,\"4\":1}]},\"6\":{\"1\":[{\"1\":2,\"2\":0,\"5\":{\"1\":2,\"2\":0}},{\"1\":0,\"2\":0,\"3\":3},{\"1\":1,\"2\":0,\"4\":1}]},\"7\":{\"1\":[{\"1\":2,\"2\":0,\"5\":{\"1\":2,\"2\":0}},{\"1\":0,\"2\":0,\"3\":3},{\"1\":1,\"2\":0,\"4\":1}]},\"8\":{\"1\":[{\"1\":2,\"2\":0,\"5\":{\"1\":2,\"2\":0}},{\"1\":0,\"2\":0,\"3\":3},{\"1\":1,\"2\":0,\"4\":1}]},\"9\":1,\"10\":1,\"11\":4,\"12\":0}' data-sheets-value='{\"1\":2,\"2\":\"Lehanga and choli: Raw Silk. Dupatta: Organza\"}' data-sheets-root=\"1\">Lehenga and Choli: Raw Silk</span></li>\n<li>\n<span data-sheets-userformat='{\"2\":1023,\"3\":{\"1\":2,\"2\":\"#,##0\",\"3\":1},\"4\":{\"1\":2,\"2\":16777215},\"5\":{\"1\":[{\"1\":2,\"2\":0,\"5\":{\"1\":2,\"2\":0}},{\"1\":0,\"2\":0,\"3\":3},{\"1\":1,\"2\":0,\"4\":1}]},\"6\":{\"1\":[{\"1\":2,\"2\":0,\"5\":{\"1\":2,\"2\":0}},{\"1\":0,\"2\":0,\"3\":3},{\"1\":1,\"2\":0,\"4\":1}]},\"7\":{\"1\":[{\"1\":2,\"2\":0,\"5\":{\"1\":2,\"2\":0}},{\"1\":0,\"2\":0,\"3\":3},{\"1\":1,\"2\":0,\"4\":1}]},\"8\":{\"1\":[{\"1\":2,\"2\":0,\"5\":{\"1\":2,\"2\":0}},{\"1\":0,\"2\":0,\"3\":3},{\"1\":1,\"2\":0,\"4\":1}]},\"9\":1,\"10\":1,\"11\":4,\"12\":0}' data-sheets-value='{\"1\":2,\"2\":\"Lehanga and choli: Raw Silk. Dupatta: Organza\"}' data-sheets-root=\"1\"> Dupatta: Organza</span><br>\n</li>\n</ul>\n<style type=\"text/css\"><!--\ntd {border: 1px solid #ccc;}br {mso-data-placement:same-cell;}\n--></style>\n<style type=\"text/css\"><!--\ntd {border: 1px solid #ccc;}br {mso-data-placement:same-cell;}\n--></style>\n<style type=\"text/css\"><!--\ntd {border: 1px solid #ccc;}br {mso-data-placement:same-cell;}\n--></style>\n<style type=\"text/css\"><!--\ntd {border: 1px solid #ccc;}br {mso-data-placement:same-cell;}\n--></style>\n<style type=\"text/css\"><!--td {border: 1px solid #cccccc;}br {mso-data-placement:same-cell;}--></style>\n<style type=\"text/css\"><!--td {border: 1px solid #cccccc;}br {mso-data-placement:same-cell;}--></style>\n<style type=\"text/css\"><!--td {border: 1px solid #cccccc;}br {mso-data-placement:same-cell;}--></style>\n<style type=\"text/css\"><!--td {border: 1px solid #cccccc;}br {mso-data-placement:same-cell;}--></style>\n<style type=\"text/css\"><!--td {border: 1px solid #cccccc;}br {mso-data-placement:same-cell;}--></style>\n<style type=\"text/css\"><!--td {border: 1px solid #cccccc;}br {mso-data-placement:same-cell;}--></style>
"""

# Preprocess HTML content
preprocessed_content = preprocess_text(html_content)

print("Preprocessed content:")
print(preprocessed_content)