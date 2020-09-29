#%%
from bs4 import BeautifulSoup
from requests import get
import random
import string
import sqlite3
import logging

# Input
current_file = '../03_Scraping/already_links_in/techadvisor.txt'
current_reviews = set(line.strip() for line in open(current_file))

#  Output
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

def generateNode(length):
    letters_and_digits = string.ascii_letters +  string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    node = "_:znode" + result_str
    return node

links = []
for page in range(1, 13):
    url = f'https://www.techadvisor.co.uk/review/wearable-tech/?p={page}/'
    soup = BeautifulSoup(get(url).text, 'lxml')
    reviews = soup.find_all('li', class_='media')
    for review in reviews:
        links.append(review.a['href'])
for page in range(1, 69):
    url = f'https://www.techadvisor.co.uk/review/smartphones/?p={page}/'
    soup = BeautifulSoup(get(url).text, 'lxml')
    reviews = soup.find_all('li', class_='media')
    for review in reviews:
        links.append(review.a['href'])

host = "https://www.techadvisor.co.uk/"
review_count = 0
no_annotation = 0
no_rating = 0
already_count = 0
problem_count = 0
extract_count = 0

for review_link in links:
    review_count += 1
    if review_link in current_reviews:
        already_count += 1
        continue
    else:
        response = get(review_link)
        soup = BeautifulSoup(response.text, 'lxml')
        review = soup.find('section', id='articleBody')
        node = generateNode(31)
        url = review_link
        reviewText = review.find('div', itemprop='reviewBody')
        if reviewText.find('section') is None:
            pass
        else:
            reviewText.find('section').decompose()
        reviewBody = reviewText.text.strip()
        try:
            ratingValue = review.find('meta', itemprop='ratingValue')['content']
            bestRating = review.find('meta', itemprop='bestRating')['content']
            worstRating = review.find('meta', itemprop='worstRating')['content']
            reviewRating = ''
            c.execute(
                f"INSERT OR IGNORE INTO {db_name} (NODE, URL, REVIEWBODY, RATING, REVIEWRATING, BESTRATING, WORSTRATING) VALUES (?,?,?,?,?,?,?);",
                (node, review_link, reviewBody, str(reviewRating), ratingValue, bestRating, worstRating))
            conn.commit()
            extract_count += 1
        except:
            no_rating += 1
logging.debug(f"Done {host} - Reviews extracted: " + str(extract_count) + " out of " + str(review_count))
logging.debug("without Rating: " + str(no_rating) + ", problems: " + str(problem_count))
logging.debug("Already in: " + str(already_count))