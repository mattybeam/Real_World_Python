import numpy as np
import requests
import bs4
import nltk
from PIL import Image
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS

# Use webscraping to obtain the text.
url = 'https://en.wikipedia.org/wiki/Saint_Judy'
page = requests.get(url)
page.raise_for_status()
soup = bs4.BeautifulSoup(page.text, 'html.parser')
p_elems = [element.text for element in soup.find_all('p')]

speech = ' '.join(p_elems)  # Make sure to join on a space!

text = nltk.word_tokenize(speech)

text = [word for word in text if word.isalpha()]

text = str(text)

text = text.replace("'", "")
text = text.replace(",", "")
text = text.replace("[", "")
text = text.replace("]", "")

# Load an image as a NumPy array.
#mask = np.array(Image.open('holmes.png'))

# Get stop words as a set and add extra words.
stopwords = STOPWORDS
stopwords.update(['us', 'one', 'will', 'said', 'now', 'well', 'man', 'may',
                  'little', 'say', 'must', 'way', 'long', 'yet', 'mean',
                  'put', 'seem', 'asked', 'made', 'half', 'much',
                  'certainly', 'might', 'came', 'Film', 'Film Festival',
                  'Saint Judy','Saint', 'Judy', 'Festival'])

# Generate word cloud.
wc = WordCloud(max_words=500,
               relative_scaling=0.5,
               background_color='white',
               stopwords=stopwords,
               margin=2,
               random_state=7,
               contour_width=2,
               contour_color='brown',
               colormap='copper').generate(str(text))

# Turn wc object into an array.
colors = wc.to_array()

# Plot and save word cloud.
plt.figure()
plt.imshow(colors, interpolation="bilinear")
plt.axis('off')
plt.show()
#plt.savefig('hound_wordcloud.png')
