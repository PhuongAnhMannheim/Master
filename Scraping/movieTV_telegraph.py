from bs4 import BeautifulSoup
from requests import get
import random
import string
import sqlite3
import logging

# Input
already_file = 'already_links_in/telegraph.txt'
current_reviews = set(line.strip() for line in open(already_file))

# output
db_path = '../Data/test.db'
db_name = 'test'
log_path = '../Logs/test.log'
conn = sqlite3.connect(db_path)
c = conn.cursor()

logger = logging.getLogger()
fhandler = logging.FileHandler(filename=log_path, mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fhandler.setFormatter(formatter)
logger.addHandler(fhandler)
logger.setLevel(logging.DEBUG)

already_count = 0
no_annotation = 0
review_count = 0

def generateNode(length):
    letters_and_digits = string.ascii_letters +  string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    node = "_:znode" + result_str
    return node

host = 'https://www.telegraph.co.uk/'
for page in range (1,34):
    url = f'https://www.telegraph.co.uk/films/reviews/page-{page}/'
    soup = BeautifulSoup(get(url).text, 'lxml')
    movie_container = soup.find_all("div", class_="card__content")
    for link in movie_container:
        review_link = host + link.a['href']
        if (review_link in current_reviews):
            already_count += 1
            pass
        else:
            review_soup = BeautifulSoup(get(review_link).text, 'lxml')
            reviewBody = ""
            has_annotation = review_soup.find('main', itemtype='https://schema.org/Review')
            if has_annotation is None:
                no_annotation += 1
                continue
            else:
                review = has_annotation.find('article', itemprop='reviewBody')
                body = review.find_all('p')
                for item in body:
                    reviewBody += reviewBody + item.text
                reviewRating = "already included"
                ratingValue = has_annotation.find('span', itemprop='reviewRating').find('span', class_='entity-property-numeric-score').text
                worstRating = "1"
                bestRating = "5"
                node = generateNode(31)
                c.execute(f"INSERT OR IGNORE INTO {db_name} (NODE, URL, REVIEWBODY, RATING, REVIEWRATING, BESTRATING, WORSTRATING) VALUES (?,?,?,?,?,?,?);",(node,review_link,reviewBody,str(reviewRating),ratingValue,bestRating,worstRating))
                conn.commit()
            review_count += 1

logging.debug("Reviews extracted: " + str(review_count))
logging.debug("Reviews without Review Annotation: " + str(no_annotation))
logging.debug("Already included: " + str(already_count))
