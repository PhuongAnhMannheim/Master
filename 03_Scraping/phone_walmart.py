from bs4 import BeautifulSoup
from requests import get
import random
import string
import sqlite3
import logging
import time
import json

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

extracted_cnt = 0

def generateNode(length):
    letters_and_digits = string.ascii_letters + string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(length)))
    node = "_:znode" + result_str
    return node

links = []
for page in range(1, 26):
    url = f'https://www.walmart.com/browse/cell-phones/phone-cases/1105910_133161_1997952?page={page}'
    soup = BeautifulSoup(get(url).text, 'lxml')
    product_overview = soup.find('script', id='searchContent', type='application/json')
    while product_overview is None:
        try:
            time.sleep(0.5)
            soup = BeautifulSoup(get(url).text, 'lxml')
            product_overview = soup.find('script', id='searchContent', type='application/json')
        except:
            pass
    data = json.loads(product_overview.contents[0])
    products = data["searchContent"]['preso']['items']
    for product in products:
        prod_id = product['productPageUrl'].split('/')[3]
        new_link = 'https://www.walmart.com/reviews/product/' + prod_id
        links.append(new_link)

for link in links:
    response = get(link, headers={'User-Agent': 'Custom'})
    soup = BeautifulSoup(response.text, 'lxml')
    paginator = soup.find('div', class_='paginator')
    try:
        pages = paginator.find_all('li')

        reviews = soup.find_all('div', class_='Grid ReviewList-content')
        for review in reviews:
            node = generateNode(31)
            url = link
            try:
                reviewBody = review.find('div', class_='review-text').text
                worstRating = review.find('meta', itemprop='worstRating')['content']
                bestRating = review.find('meta', itemprop='bestRating')['content']
                ratingValue = review.find('meta', itemprop='ratingValue')['content']
                reviewRating = ratingValue
            except:
                continue

            c.execute(f"INSERT OR IGNORE INTO {db_name} (NODE, URL, REVIEWBODY, RATING, REVIEWRATING, BESTRATING, WORSTRATING) VALUES (?,?,?,?,?,?,?);",(node, link, reviewBody, reviewRating, ratingValue, bestRating, worstRating))
            conn.commit()
            extracted_cnt += 1
        # do multipage product reviews
        if len(pages) > 1:
            last_li = None
            for last_li in pages:pass
            if last_li:
                last = int(last_li.getText())
            end = last + 1
            for page in range(2, end):
                ext_link = link + f'?page={page}'
                response = get(ext_link, headers={'User-Agent': 'Custom'})
                soup = BeautifulSoup(response.text, 'lxml')
                paginator = soup.find('div', class_='paginator')
                pages = paginator.find_all('li')

                reviews = soup.find_all('div', class_='Grid ReviewList-content')
                for review in reviews:
                    node = generateNode(31)
                    url = ext_link
                    try:
                        reviewBody = review.find('div', class_='review-text').text
                        worstRating = review.find('meta', itemprop='worstRating')['content']
                        bestRating = review.find('meta', itemprop='bestRating')['content']
                        ratingValue = review.find('meta', itemprop='ratingValue')['content']
                        reviewRating = ratingValue
                    except:
                        continue

                    c.execute(f"INSERT OR IGNORE INTO {db_name} (NODE, URL, REVIEWBODY, RATING, REVIEWRATING, BESTRATING, WORSTRATING) VALUES (?,?,?,?,?,?,?);",(node, link, reviewBody, reviewRating, ratingValue, bestRating, worstRating))
                    conn.commit()
                    extracted_cnt += 1
    except:
        print(link)

logging.debug("Done {host} - Reviews extracted: " + str(extracted_cnt))