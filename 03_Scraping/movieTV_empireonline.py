from bs4 import BeautifulSoup
from requests import get
import json
import random
import string
import sqlite3
import logging

# no list to check whether already included

db_path = '../Data/moviewreviews.db'
db_name = 'moviereviews'
log_path = '../Logs/movieReviews.log'
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

host = "https://www.empireonline.com"
review_count = 0
no_annotation = 0
fail_lst = []

for page in range (1,419):
    url = f'https://www.empireonline.com/movies/reviews/{page}/'
    soup = BeautifulSoup(get(url).text, "lxml")
    movie_container = soup.find_all("div", class_="image-content")
    for link in movie_container:
        review_link = host + link.a['href']
        response = get(review_link, headers={'User-Agent': 'Custom'})
        if not response.status_code == 200:
            fail_lst.append(review_link)
        else:
            try:
                review_soup = BeautifulSoup(response.text, 'lxml')
                data = json.loads("".join(review_soup.find("script", {"type": "application/ld+json"}).contents),strict=False)
                if not data['@type'] == "review":
                    no_annotation += 1
                    pass
                else:
                    reviewBody = data['description'].replace('\n', '')
                    worstRating = data['reviewRating']['worstRating']
                    bestRating = data['reviewRating']['bestRating']
                    ratingValue = data['reviewRating']['ratingValue']
                    reviewRating = "already included"
                    node = generateNode(31)
                    c.execute(f"INSERT OR IGNORE INTO {db_name} (NODE, URL, REVIEWBODY, RATING, REVIEWRATING, BESTRATING, WORSTRATING) VALUES (?,?,?,?,?,?,?);", (node, review_link, reviewBody, str(reviewRating), ratingValue, bestRating, worstRating))
                    conn.commit()
                    review_count += 1
            except Exception as e:
                logging.debug("Error: " + str(review_link))
                logging.debug(str(review_soup))
                raise (e)

logging.debug(("Done with the first round. Reviews extracted: " + str(review_count)))

while len(fail_lst)>0:
    for i in fail_lst:
        review_link = i
        response = get(review_link)
        if not response.status_code == 200:
            pass
        else:
            try:
                review_soup = BeautifulSoup(response.text, 'lxml')
                data = json.loads("".join(review_soup.find("script", {"type": "application/ld+json"}).contents),strict=False)
                if not data['@type'] == "review":
                    no_annotation += 1
                    pass
                else:
                    reviewBody = data['description'].replace('\n','')
                    worstRating = data['reviewRating']['worstRating']
                    bestRating = data['reviewRating']['bestRating']
                    ratingValue = data['reviewRating']['ratingValue']
                    reviewRating = "already included"
                    node = generateNode(31)
                    c.execute(f"INSERT OR IGNORE INTO {db_name} (NODE, URL, REVIEWBODY, RATING, REVIEWRATING, BESTRATING, WORSTRATING) VALUES (?,?,?,?,?,?,?);", (node, review_link, reviewBody, str(reviewRating), ratingValue, bestRating, worstRating))
                    conn.commit()
                    review_count += 1
                    fail_lst.remove(review_link)
            except Exception as e:
                logging.debug("Error: " + str(review_link))
                logging.debug(str(review_soup))
                raise(e)

logging.debug("Reviews extracted: " + str(review_count) + " , reviews without Review Annotation: " + str(no_annotation))

