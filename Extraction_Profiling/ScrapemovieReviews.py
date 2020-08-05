# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.2.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

from bs4 import BeautifulSoup
from requests import get
import json
import random
import string
import sqlite3
import logging
import re

# + {"pycharm": {"name": "#%%\n"}}
# Input / Output
db_path = '../Data/moviewreviews.db'

# Output
log_path = '../Logs/movieReviews.log'

logger = logging.getLogger()
fhandler = logging.FileHandler(filename=moviereviewLog_path, mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fhandler.setFormatter(formatter)
logger.addHandler(fhandler)
logger.setLevel(logging.DEBUG)

conn = sqlite3.connect(db_path)
c = conn.cursor()
# c.execute(("""
#        CREATE TABLE IF NOT EXISTS
#            test(
#                NODE TEXT,
#                URL TEXT,
#                REVIEWBODY TEXT,
#                RATING TEXT,
#                REVIEWRATING TEXT,
#                BESTRATING TEXT,
#                WORSTRATING TEXT,
#                PRIMARY KEY (NODE, URL))
#    """))

# + {"pycharm": {"name": "#%%\n"}}
def generateNode(length):
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    node = "_:znode" + result_str
    return node
    # print("Random alphanumeric String is:", result_str)
# generateNode(31)


# + {"pycharm": {"name": "#%%\n"}}
host = 'https://www.imdb.com'
# https://www.imdb.com/search/title/?title_type=tv_movie,tv_episode&release_date=2000-01-01,2020-12-31&user_rating=1.0,10.0&languages=en&start=1&ref_=adv_nxt
# # +50
# https://www.imdb.com/search/title/?title_type=tv_movie,tv_episode&release_date=2000-01-01,2020-12-31&user_rating=1.0,10.0&languages=en&start=51&ref_=adv_nxt
page_count = 0
movie_count = 0
review_count = 0
# umstellen auf 1001
for page in range (0,11):
    page_count= page*50+1
    # print(page_count)
    url = f'https://www.imdb.com/search/title/?title_type=tv_movie,tv_episode&release_date=2000-01-01,2020-12-31&user_rating=1.0,10.0&languages=en&start={page_count}&ref_=adv_nxt'
    response = get(url)
    html_soup = BeautifulSoup(response.text, 'html.parser')
    movie_containers = html_soup.find_all('div', class_ = 'lister-item mode-advanced')
    # print(type(movie_containers))
    # print(len(movie_containers))
    i = 0
    for movie in movie_containers:
        # link to site with all review previews for each movie
        link = 'https://www.imdb.com/' + movie_containers[i].a['href'] + 'reviews'
        # link = "https://www.imdb.com/review/rw3754733/"
        # print(link)
        movie_count += 1
        i += 1
        review_collection = BeautifulSoup(get(link).text, 'html.parser').body.find_all('div', class_='actions text-muted')
        for tiles in review_collection:
            permalinks = tiles.find_all('a', href=True, text='Permalink')
            for permalink in permalinks:
                review_link = host + permalink['href']
                # print(review_link)
                review_count += 1
                review_soup = BeautifulSoup(get(review_link).text, 'html.parser')
                try:
                    warning = review_soup.body.find_all(string=re.compile('.*{0}.*'.format('Warning: Spoilers')), recursive=True)
                except:
                    pass
                container = review_soup.find("script",type="application/ld+json")
                for item in container:
                    if item.__contains__('http://schema.org'):
                        text = str(item.extract())
                        oJson = json.loads(text)
                        # print(oJson)
                        if (warning):
                            # ("WARNING!")
                            reviewBodyContainer = review_soup.body.find_all('div', class_="text show-more__control")
                            for item in reviewBodyContainer:
                                reviewBody = item.text
                            # print(reviewBodyContainer)
                            # reviewBody = reviewBodyContainer[0].text
                        else:
                            reviewBody = str(oJson['reviewBody'])
                        node = generateNode(31)
                        reviewRating = str(oJson['reviewRating'])
                        worstRating = str(oJson['reviewRating']['worstRating'])
                        bestRating = str(oJson['reviewRating']['bestRating'])
                        ratingValue = str(oJson['reviewRating']['ratingValue'])
                        
            
                        # print('node:' + node)
                        # print('url: '+ review_link)
                        # print('reviewBody: ' + reviewBody)
                        # print('worstRating: ' + worstRating)
                        # print('bestRating: ' + bestRating)
                        # print('ratingValue: ' + ratingValue)
                            
                        # print("INSERT OR IGNORE INTO MOVIEREVIEWS (NODE, URL, REVIEWBODY, RATING, REVIEWRATING, BESTRATING, WORSTRATING) VALUES (?,?,?,?,?,?,?);""",(node,url,reviewBody,reviewRating,ratingValue,bestRating,worstRating))
                        c.execute("INSERT OR IGNORE INTO test (NODE, URL, REVIEWBODY, RATING, REVIEWRATING, BESTRATING, WORSTRATING) VALUES (?,?,?,?,?,?,?);",(node,url,reviewBody,reviewRating,ratingValue,bestRating,worstRating))
                        conn.commit()
logging.debug("number of reviews: " + str(review_count))

