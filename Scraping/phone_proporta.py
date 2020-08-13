from bs4 import BeautifulSoup
from requests import get
import random
import string
import sqlite3
import logging
from requests_toolbelt import utils

# Output
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

host = "https://www.proporta.com"
review_count = 0
no_annotation = 0
no_rating = 0
already_count = 0
extracted_count = 0

def generateNode(length):
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    node = "_:znode" + result_str
    return node

links = []
for page in range(1, 23):
    url = f'https://www.proporta.com/devices?p={page}/'
    response = get(url, headers={'User-Agent': 'Custom'})
    soup = BeautifulSoup(response.text, 'lxml')
    lefts = soup.find_all('li', class_='item first')
    for left in lefts:
        links.append(left.a['href'] + '#allReviews')
    rights = soup.find_all('li', class_='item last')
    for right in rights:
        links.append(right.a['href'] + '#allReviews')
for page in range(1, 5):
    url = f'https://www.proporta.com/accessories?p={page}/'
    response = get(url, headers={'User-Agent': 'Custom'})
    soup = BeautifulSoup(response.text, 'lxml')
    lefts = soup.find_all('li', class_='item first')
    for left in lefts:
        links.append(left.a['href'] + '#allReviews')
    rights = soup.find_all('li', class_='item last')
    for right in rights:
        links.append(right.a['href'] + '#allReviews')

for review_link in links:
    response = get(review_link, headers={'User-Agent': 'Custom'})
    soup = BeautifulSoup(response.text, 'lxml')
    reviews = soup.find('ol', id='reviewContainer')
    if reviews is None:
        no_annotation += 1
        continue
    else:
        # for review in reviews.find_all('li', itemtype='http://schema.org/Review'):
        for review in reviews:
            try:
                node = generateNode(31)
                url = review_link
                reviewBody = review.find('p', itemprop='reviewBody').text.split('\n')[0]
                ratingValue = review.find('span', itemprop='ratingValue').text
                bestRating = review.find('span', itemprop='bestRating').text
                worstRating = review.find('meta', itemprop='worstRating').text
                reviewRating = review.find('div', itemprop='reviewRating').text

                c.execute(f"INSERT OR IGNORE INTO {db_name} (NODE, URL, REVIEWBODY, RATING, REVIEWRATING, BESTRATING, WORSTRATING) VALUES (?,?,?,?,?,?,?);",(node, review_link, reviewBody, reviewRating, ratingValue, bestRating, worstRating))
                conn.commit()
                extracted_count += 1
            except:
                pass

logging.debug(f"Done {host} - Reviews extracted: " + str(review_count))
logging.debug("without Annotation: " + str(no_annotation))
