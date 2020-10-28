from bs4 import BeautifulSoup
from requests import get
import random
import string
import sqlite3
import logging

# Input
reviewschview_file = 'already_links_in/reviewschview.txt'
current_reviews = set(line.strip() for line in open(reviewschview_file))

# Output
log_path = '../Logs/movieReviews.log'
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

# all moviereviews
soup = BeautifulSoup(get("http://reviewschview.com/movies/a-z/page/1").text, 'html.parser')
movie_container = soup.find_all("p", class_="movie-rating-count")
movie_count = 0
review_count = 0
for item in movie_container:
    review_link = item.a['href']
    if (review_link in current_reviews):
        pass
    else:
        movie_count += 1
        review_soup = BeautifulSoup(get(review_link).text, 'lxml')
        reviews = review_soup.find_all("li", itemprop="review")
        # print(reviews)
        try:
            for item in reviews:
                reviewBody = item.find("div", itemprop="reviewBody").text
                reviewRating = item.find("div", itemprop="reviewRating")
                worstRating_tag = reviewRating.find("meta", itemprop="worstRating")
                worstRating = worstRating_tag["content"]
                bestRating_tag = reviewRating.find("meta", itemprop="bestRating")
                bestRating = bestRating_tag["content"]
                ratingValue_tag = reviewRating.find("p", itemprop="ratingValue")
                ratingValue = ratingValue_tag.text
                # worstRating_tag = item.find("meta", itemprop="worstRating")
                # worstRating = worstRating_tag["content"]
                # bestRating_tag = item.find("meta", itemprop="bestRating")
                # bestRating = bestRating_tag["content"]
                # ratingValue_tag = item.find("p", itemprop="ratingValue")
                # ratingValue = ratingValue_tag.text
                node = generateNode(31)
                c.execute(f"INSERT OR IGNORE INTO {db_name} (NODE, URL, REVIEWBODY, RATING, REVIEWRATING, BESTRATING, WORSTRATING) VALUES (?,?,?,?,?,?,?);",(node,review_link,reviewBody,str(reviewRating),ratingValue,bestRating,worstRating))
                conn.commit()
                review_count += 1
        except Exception as e:
            logging.debug("Error: " + str(review_link) + str(reviewBody))
            raise(e)

logging.debug('open movies to get reviews from: ' + str(movie_count))
logging.debug('amount of reviews extracted: ' + str(review_count))



