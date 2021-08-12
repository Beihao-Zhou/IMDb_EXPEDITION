from matplotlib import pyplot as plt        # Graph, data visualization tool
from wordcloud import WordCloud
from PIL import Image               # Process images
import numpy as np                  # Matrix calc
import sqlite3
import multidict
import re

# Prepare for the sentences
conn = sqlite3.connect('movie.db')
cur = conn.cursor()
sql = '''
    SELECT genre FROM movie250
'''
data = cur.execute(sql)
gen = ''
for item in data:
    gen = gen + ", " + item[0]
gen = gen[2:]+','
cur.close()
conn.close()

# Count words
# length_of_gen = len(gen.split(' '))
# print(length_of_gen)
# print(gen)

fullTermsDict = multidict.MultiDict()
tmpDict = {}

# making dict for counting frequencies
for text in gen.split(" "):
    text = re.sub(',','',text)
    val = tmpDict.get(text, 0)
    tmpDict[text.lower()] = val + 1
for key in tmpDict:
    fullTermsDict.add(key, tmpDict[key])

# put the words into an image
img = Image.open(r'.\static\assets\img\mask_img.png')
img_array = np.array(img)
wc = WordCloud(
    background_color='white',
    mask=img_array,
    font_path=r'C:\Windows\Fonts\BELLI.TTF'     #C:\Windows\Fonts
)
wc.generate_from_frequencies(fullTermsDict)
# If .generate() is used, just pass the text separated by space as the param.

# generate graph
fig = plt.figure(1)
plt.imshow(wc)
plt.axis('off')

plt.savefig(r'.\static\assets\img\genre.jpg',dpi=500)
