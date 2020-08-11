from bs4 import BeautifulSoup
from requests import get
import random
import string
import sqlite3
import logging

# Input/ Output
db_path = '../Data/test.db'
db_name = 'test'
log_path = '../Logs/test1.log'
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Input
current_file = 'already_links_in/thereviewmonk.txt'
current_reviews = set(line.strip() for line in open(current_file))

logger = logging.getLogger()
fhandler = logging.FileHandler(filename=log_path, mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fhandler.setFormatter(formatter)
logger.addHandler(fhandler)
logger.setLevel(logging.DEBUG)

#%%

host = "https://thereviewmonk.com/"
review_count = 0
problem_count = 0

def generateNode(length):
    letters_and_digits = string.ascii_letters +  string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    node = "_:znode" + result_str
    return node

for i in current_reviews:
    review_link = i
    response = get(review_link, headers={'User-Agent': 'Custom'})
    if response.status_code != 200:
        problem_count += 1
        print(review_link)
    else:
        review_soup = BeautifulSoup(response.text, 'lxml')
        for a in review_soup.find_all('div', itemtype='http://schema.org/Review'):
            node = generateNode(31)
            url = review_link
            reviewBody = a.find_all('p', itemprop='reviewBody')[0].text
            ratingValue = str(a.find_all('meta', itemprop='ratingValue')[0]['content'])
            bestRating = str(10)
            worstRating = str(0)
            reviewRating = "already included"
            c.execute(f"INSERT OR IGNORE INTO {db_name} (NODE, URL, REVIEWBODY, RATING, REVIEWRATING, BESTRATING, WORSTRATING) VALUES (?,?,?,?,?,?,?);",(node,review_link,reviewBody,str(reviewRating),ratingValue,bestRating,worstRating))
            conn.commit()
            review_count += 1

logging.debug(f"Done {host} - Reviews extracted: " + str(review_count) + " , problems: " + str(problem_count))
