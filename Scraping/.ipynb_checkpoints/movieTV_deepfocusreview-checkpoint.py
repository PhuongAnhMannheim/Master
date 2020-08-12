
from bs4 import BeautifulSoup
from requests import get
import random
import string
import sqlite3
import logging

# Input/ Output
db_path = '../Data/moviewreviews.db'
db_name = 'moviereviews'
log_path = '../Logs/movieReviews.log'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Input
current_file = 'already_links_in/deepfocusreview.txt'
current_reviews = set(line.strip() for line in open(current_file))

logger = logging.getLogger()
fhandler = logging.FileHandler(filename=log_path, mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fhandler.setFormatter(formatter)
logger.addHandler(fhandler)
logger.setLevel(logging.DEBUG)

host = "https://deepfocusreview.com/"
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

for character in string.ascii_lowercase + '0':
    url = f'https://deepfocusreview.com/reviews/?id={character}'
    response = get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    for entry in soup.find_all('ol', id='reviewalpha-list'):
        for link in entry.find_all('li'):
            review_link = link.a['href']
            if review_link in current_reviews:
                already_count += 1
                pass
            else:
                response = get(review_link)
                if response.status_code != 200:
                    problem_count += 1
                else:
                    review_soup = BeautifulSoup(response.text, 'lxml')
                    node = generateNode(31)
                    url = review_link
                    reviewBody = ""
                    for i in review_soup.find_all('div', itemprop='reviewBody'):
                        for j in i.find_all('p'):
                            reviewBody = reviewBody + j.getText()

                    ratingValue = review_soup.find('meta', itemprop='ratingValue')['content']
                    worstRating = review_soup.find('meta', itemprop='worstRating')['content']
                    bestRating = review_soup.find('meta', itemprop='bestRating')['content']
                    reviewRating = "already included"
                    c.execute(f"INSERT OR IGNORE INTO {db_name} (NODE, URL, REVIEWBODY, RATING, REVIEWRATING, BESTRATING, WORSTRATING) VALUES (?,?,?,?,?,?,?);",(node,review_link,reviewBody,str(reviewRating),ratingValue,bestRating,worstRating))
                    conn.commit()
                    review_count += 1

logging.debug(f"Done {host} - Reviews extracted: " + str(review_count) + ", without Rating: " + str(no_rating) + ", problems: " + str(problem_count))
logging.debug('already in the db: ' + str(already_count))
