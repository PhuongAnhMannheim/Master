from bs4 import BeautifulSoup
from requests import get
import random
import string
import sqlite3
import logging

# Input
current_file = 'already_links_in/coolsmartphone.txt'
current_reviews = set(line.strip() for line in open(current_file))

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

host = "https://www.coolsmartphone.com"
review_count = 0
no_annotation = 0
already_in = 0
extracted_count = 0

def generateNode(length):
    letters_and_digits = string.ascii_letters +  string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    node = "_:znode" + result_str
    return node

for page in range(1, 44):
    url = f'https://www.coolsmartphone.com/category/reviews/page/{page}/'
    response = get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    articles = soup.find_all('article', class_='latestPost excerpt')
    for article in articles:
        review_link = article.a['href']
        review_count += 1
        if review_link in current_reviews:
            already_in += 1
            pass
        else:
            response = get(review_link)
            soup = BeautifulSoup(response.text, 'lxml')
            review = soup.find_all('div', itemtype='http://schema.org/Review')
            if len(review) == 0:
                no_annotation += 1
                pass
            else:
                node = generateNode(31)
                url = review_link
                reviewBody = soup.find_all("div", itemprop="reviewBody")[0].text
                reviewRating = ""
                ratingValue = soup.find_all("span", itemprop="ratingValue")[0].text
                worstRating = soup.find_all("meta", itemprop="worstRating")[0]['content']
                bestRating = soup.find_all("meta", itemprop="bestRating")[0]['content']
                c.execute(f"INSERT OR IGNORE INTO {db_name} (NODE, URL, REVIEWBODY, RATING, REVIEWRATING, BESTRATING, WORSTRATING) VALUES (?,?,?,?,?,?,?);", (node, review_link, reviewBody, str(reviewRating), ratingValue, bestRating, worstRating))
                conn.commit()
                extracted_count += 1

logging.debug(f"Done {host} - Reviews extracted: " + str(review_count) + " out of " + str(extracted_count))
logging.debug("without Annotation: " + str(no_annotation))
logging.debug("already in: " + str(already_in))
