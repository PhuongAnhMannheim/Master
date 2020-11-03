from bs4 import BeautifulSoup
from requests import get
import json
import random
import string
import sqlite3
import logging

log_path = '../logs/movieReviews.log'
db_path = '../Data/moviereviews.db'
db_name = 'moviereviews'
conn = sqlite3.connect(db_path)
c = conn.cursor()

logger = logging.getLogger()
fhandler = logging.FileHandler(filename=log_path, mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fhandler.setFormatter(formatter)
logger.addHandler(fhandler)
logger.setLevel(logging.DEBUG)


def generateNode(length):
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    node = "_:znode" + result_str
    return node


review_count = 0
no_annotation = 0
no_rating = 0

for page in range(1, 414):
    url = f'https://www.rollingstone.com/movies/movie-reviews/page/{page}/'
    soup = BeautifulSoup(get(url).text, 'lxml')
    movie_container = soup.find_all("a", class_="c-card__wrap")
    for link in movie_container:
        review_link = link.get('href')
        if not "movie-reviews" in review_link:
            pass
        else:
            review_soup = BeautifulSoup(get(review_link).text, 'lxml')
            review_html = review_soup.find(id="pmc-movie-review-snippet")
            if review_html is None:
                no_annotation += 1
            else:
                for item in review_html:
                    jsonExtract = str(item).split('\n')[2].replace(";", "")
                data = json.loads("".join(jsonExtract))

                reviewBody = data['description']
                ratingValue = str(data['reviewRating']['ratingValue'])
                bestRating = str(data['reviewRating']['bestRating'])
                worstRating = str(data['reviewRating']['worstRating'])
                reviewRating = "already included"

                node = generateNode(31)
                c.execute(
                    f"INSERT OR IGNORE INTO {db_name} (NODE, URL, REVIEWBODY, RATING, REVIEWRATING, BESTRATING, WORSTRATING) VALUES (?,?,?,?,?,?,?);",
                    (node, review_link, reviewBody, str(reviewRating), ratingValue, bestRating, worstRating))
                conn.commit()
                review_count += 1

logging.debug("Reviews extracted: " + str(review_count) + " , reviews without Review Annotation: " + str(no_annotation))
