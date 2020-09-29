# %%

from bs4 import BeautifulSoup
from requests import get
import json
import random
import string
import sqlite3
import logging

# %%

# Input/ Output
db_path = '../Data/phonereviews.db'
db_name = 'phonereviews'
log_path = '../Logs/phoneReview.log'
conn = sqlite3.connect(db_path)
c = conn.cursor()

logger = logging.getLogger()
fhandler = logging.FileHandler(filename=log_path, mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fhandler.setFormatter(formatter)
logger.addHandler(fhandler)
logger.setLevel(logging.DEBUG)

host = "https://www.cnet.com"
review_cnt = 0
already_cnt = 0
no_annotation = 0
no_rating = 0
no_text = 0
extracted_cnt = 0

def generateNode(length):
    letters_and_digits = string.ascii_letters +  string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    node = "_:znode" + result_str
    return node

list = []
url = f'https://www.cnet.com/topics/phones/products/'
response = get(url, headers={'User-Agent': 'Custom'})
soup = BeautifulSoup(response.text, 'lxml')
products = soup.find('div', class_='items').find_all('section')
for product in products:
    link = host + product.find('div', class_='itemInfo').a['href']
    list.append(link)
for page in range(2, 204):
    review_link=f'https://www.cnet.com/topics/phones/products/{page}'
    response = get(review_link, headers={'User-Agent': 'Custom'})
    soup = BeautifulSoup(response.text, 'lxml')
    products = soup.find('div', class_='items').find_all('section')
    for product in products:
        # print(host + product.find('div', class_='itemInfo').a['href'])
        link = host + product.find('div', class_='itemInfo').a['href']
        list.append(link)
# %%
for review_link in list:
    review_cnt += 1
    response = get(review_link)
    soup = BeautifulSoup(response.text, 'lxml')
    try:
        data = json.loads("".join(soup.find("script", {"type": "application/ld+json"}).contents),strict=False)
        try:
            review = data['review']
            try:
                reviewBody = review['reviewBody']
            except KeyError:
                no_text += 1
                continue
        except KeyError:
            no_annotation += 1
            continue
        node = generateNode(31)
        url = review_link
        try:
            ratingValue = str(review['reviewRating']['ratingValue'])
            bestRating = review['reviewRating']['bestRating']
            worstRating = review['reviewRating']['worstRating']
            reviewRating = "already included"
            # print('node:' + node)
            # print('url: '+ review_link)
            # print('reviewBody: ' + reviewBody)
            # print('worstRating: ' + worstRating)
            # print('bestRating: ' + bestRating)
            # print('ratingValue: ' + ratingValue)
            c.execute(f"INSERT OR IGNORE INTO {db_name} (NODE, URL, REVIEWBODY, RATING, REVIEWRATING, BESTRATING, WORSTRATING) VALUES (?,?,?,?,?,?,?);",(node, url, reviewBody, str(reviewRating), ratingValue, bestRating, worstRating))
            conn.commit()
            extracted_cnt += 1
        except KeyError:
            no_rating += 1
            continue
    except AttributeError:
        no_annotation += 1
        continue

logging.debug(f"Done {host} - Reviews extracted: " + str(extracted_cnt) + " out of " + str(review_cnt))
logging.debug("Already in: " + str(already_cnt))
logging.debug("No Annotations: " + str(no_annotation))
logging.debug("No Rating : " + str(no_rating))
logging.debug("No ReviewBody: " + str(no_text))
