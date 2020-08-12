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
log_path = '../Logs/phoneReviews.log'
conn = sqlite3.connect(db_path)
c = conn.cursor()

logger = logging.getLogger()
fhandler = logging.FileHandler(filename=log_path, mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fhandler.setFormatter(formatter)
logger.addHandler(fhandler)
logger.setLevel(logging.DEBUG)

host = "https://www.cnet.com"
review_count = 0
no_annotation = 0
no_rating = 0
already_count = 0
problem_count = 0

def generateNode(length):
    letters_and_digits = string.ascii_letters +  string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    node = "_:znode" + result_str
    return node

links = []
for page in range(1, 204):
    url = f'https://www.cnet.com/topics/phones/products/{page}/'
    response = get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    left_products = soup.find_all('section', class_='col-3 searchItem product left')
    products = soup.find_all('section', class_='col-3 searchItem product')
    for prod in products:
        links.append(prod.a['href'])
    for prod in left_products:
        links.append(prod.a['href'])

for link in links:
    review_link = host + link
    response = get(review_link)
    soup = BeautifulSoup(response.text, 'lxml')
    try:
        data = json.loads("".join(soup.find("script", {"type": "application/ld+json"}).contents),strict=False)
        try:
            reviewBody = data['review']['reviewBody']
            try:
                node = generateNode(31)
                url = review_link
                ratingValue = data['review']['reviewRating']['ratingValue']
                bestRating = data['review']['reviewRating']['bestRating']
                worstRating = data['review']['reviewRating']['worstRating']
                reviewRating = "already included"
                review_count += 1

                c.execute(f"INSERT OR IGNORE INTO {db_name} (NODE, URL, REVIEWBODY, RATING, REVIEWRATING, BESTRATING, WORSTRATING) VALUES (?,?,?,?,?,?,?);",
                    (node, review_link, reviewBody, str(reviewRating), ratingValue, bestRating, worstRating))
                conn.commit()
            except:
                no_rating += 1
                continue
        except:
            no_annotation += 1
            continue
    except:
        no_annotation += 1
        continue

logging.debug(f"Done {host} - Reviews extracted: " + str(review_count) + ", without Rating: " + str(no_rating))
