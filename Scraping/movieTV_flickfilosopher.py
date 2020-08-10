from bs4 import BeautifulSoup
from requests import get
import random
import string
import sqlite3
import logging

flickfilosopher_file = 'already_links_in/flickfilosopher.txt'
current_reviews = set(line.strip() for line in open(flickfilosopher_file))

db_path = '../Data/moviewreviews.db'
db_name = 'moviereviews'
log_path = '../Logs/movieReviews.log'
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute(("""
       CREATE TABLE IF NOT EXISTS
           test(
               NODE TEXT,
               URL TEXT,
               REVIEWBODY TEXT,
               RATING TEXT,
               REVIEWRATING TEXT,
               BESTRATING TEXT,
               WORSTRATING TEXT,
               PRIMARY KEY (NODE, URL))
   """))

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

page2 = "https://www.flickfilosopher.com/all-reviews-n-z"
url_lst = ['https://www.flickfilosopher.com/all-reviews-a-m', 'https://www.flickfilosopher.com/all-reviews-n-z']
for url in url_lst:
    soup = BeautifulSoup(get(url).text, 'html.parser')
    movie_container = soup.find_all("div", class_="entry post clearfix")
    for link in movie_container[0].find_all("a"):
        review_link = link.get('href')
        if review_link is not None:
            if review_link.endswith('html'):
                if review_link in current_reviews:
                    pass
                else:
                    review_soup = BeautifulSoup(get(review_link).text, 'lxml')
                    review_html = review_soup.find("div", itemtype="http://schema.org/Review")
                    reviewBody = ""
                    if review_html is None:
                        no_annotation += 1
                    else:
                        try:
                            reviewBody_html = review_html.find_all("div", class_="reviewtext")
                            reviewRating = review_soup.find("div", itemtype="http://schema.org/Rating")
                            for item in reviewBody_html:
                                reviewBody += item.p.text
                            worstRating_tag = reviewRating.find("meta", itemprop="worstRating")
                            bestRating_tag = reviewRating.find("meta", itemprop="bestRating")
                            ratingValue_tag = reviewRating.find("meta", itemprop="ratingValue")
                            if worstRating_tag is None:
                                worstRating = reviewRating.find("div", itemprop="worstRating")["content"]
                                bestRating = reviewRating.find("div", itemprop="bestRating")["content"]
                                ratingValue = reviewRating.find("div", itemprop="ratingValue")["content"]
                            else:
                                worstRating = worstRating_tag["content"]
                                bestRating = bestRating_tag["content"]
                                ratingValue = ratingValue_tag["content"]
                            if ratingValue == "":
                                no_rating += 1
                            else:
                                node = generateNode(31)
                                c.execute(
                                    f"INSERT OR IGNORE INTO {db_name} (NODE, URL, REVIEWBODY, RATING, REVIEWRATING, BESTRATING, WORSTRATING) VALUES (?,?,?,?,?,?,?);",
                                    (node, review_link, reviewBody, str(reviewRating), ratingValue, bestRating,
                                     worstRating))
                                conn.commit()
                                review_count += 1
                        except Exception as e:
                            raise (e)
                            logging.debug("Error: " + str(review_link))


logging.debug("amount of reviews extracted: " + str(review_count) + ", amount of entries without review annotations: " + str(no_annotation) + " amount of entries without rating: " + str(no_rating))
