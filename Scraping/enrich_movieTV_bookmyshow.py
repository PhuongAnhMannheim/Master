from bs4 import BeautifulSoup
# import requests
from requests import get
import json
import random
import string
import sqlite3
import logging
import pandas as pd

# Input/ Output
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

# Input
df = pd.read_sql_query("SELECT * from " + str(db_name), conn)
df.dropna()
df_new = df[df.REVIEWBODY.notnull() & df.URL.str.contains('in.bookmyshow')]
df_new.describe()
df_new.drop(['RATING', 'REVIEWRATING', 'BESTRATING', 'WORSTRATING'], axis = 1)

for index, row in df_new.iterrows():
    node = row['NODE']
    url = row['URL']
    body = row['REVIEWBODY'].split("\"")[1]
    response = get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    for a in soup.find_all('div', itemprop='review'):
        review = a.find_all('meta', itemprop='description')
        if len(review) == 0:
            pass
        else:
            content = review[0]['content']
            if content == body:
                ratingValue = a.find('span', itemprop='ratingValue')['content']
                update_qry = f'UPDATE {db_name} SET REVIEWRATING = {ratingValue} WHERE NODE = ? AND URL = ? ;'
                c.execute(update_qry, [node,url])
                conn.commit()

logging.debug("Done in.bookmyshow: Enriched the entries with their ratingValues")