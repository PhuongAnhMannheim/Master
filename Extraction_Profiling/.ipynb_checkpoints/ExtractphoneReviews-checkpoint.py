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

import logging, os, sys
import sqlite3
import gzip
import re
from langdetect import detect
import pandas as pd
from urllib.parse import urlparse
import tldextract

# + {"pycharm": {"name": "#%%\n"}}
# Input
review_input_path = '../Data/schema_Review.gz'
sites_input_path = '../Data/phones_new.txt'

# Output
phonereviewLog_path = '../Logs/phoneReviews.log'
output_path = '../Data/phonereviews.db'

logger = logging.getLogger()
fhandler = logging.FileHandler(filename=phonereviewLog_path, mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fhandler.setFormatter(formatter)
logger.addHandler(fhandler)
logger.setLevel(logging.DEBUG)

# + {"pycharm": {"name": "#%%\n"}}
conn = sqlite3.connect(output_path)
c = conn.cursor()
c.execute("""
        CREATE TABLE IF NOT EXISTS
            phonereviews(
                NODE TEXT,
                URL TEXT,
                REVIEWBODY TEXT,
                RATING TEXT,
                REVIEWRATING TEXT,
                BESTRATING TEXT,
                WORSTRATING TEXT,
                PRIMARY KEY (NODE, URL))
    """)

# + {"pycharm": {"name": "#%%\n"}}
with open(sites_input_path) as f:
    domainList = f.readlines()
# print(domainList)

# + {"pycharm": {"name": "#%%\n"}}
taxo_pattern = re.compile("<http://schema.org/Review/description>|"\
                          "<http://schema.org/Review/reviewBody>|"\
                          "<http://schema.org/Review/reviewRating>|"\
                          "<http://schema.org/Rating/worstRating>|"\
                          "<http://schema.org/Rating/bestRating>|"\
                          "<http://schema.org/Rating/ratingValue>", re.IGNORECASE)
split_pattern = re.compile("^(_:.*)\s<(.*)>\s(.*)\s<(.*)>\s\.$", re.IGNORECASE)
phone_lst = ['smartphone', 'phone',
             'phone case', 'phone cable', 'phone charger', 'phone mount',
             'cell phone']


# + {"pycharm": {"name": "#%%\n"}}
def detectLang(text):
    try:
        lang = detect(text)
        if lang == "en":
            return True
    except:
        return False
    else:
        return False

# detectLang("Super. It was great")
detectLang("Excelente9Chromecast \u00C3\u00A9 o aplicativo do Google para instalar e utilizar os recursos de streaming remoto do Chromecast, um aparelho com fun\u00C3\u00A7\u00C3\u00A3o semelhante ao Airplay do Apple TV.\nDispon\u00C3\u00ADvel para venda no Brasil, o Chromecast permite ver conte\u00C3\u00BAdos multim\u00C3\u00ADdia e p\u00C3\u00A1ginas da web em qualquer televis\u00C3\u00A3o da casa. Por exemplo, funciona com servi\u00C3\u00A7os de streaming web como YouTube, Netflix e Pandora.An\u00C3\u00BAnciosam.cmd.push(function() { sam.display('review-app-page-desktop'); });\nMas lembre-se que o aplicativo s\u00C3\u00B3 funciona se voc\u00C3\u00AA possuir um aparelho Chromecast.\n")

# + {"pycharm": {"name": "#%%\n"}}
for item in phone_lst:
    item_pattern = re.compile(item,re.IGNORECASE)
    with gzip.open(review_input_path,"rt") as f:
        i = 0
        detected = 0
        skipped = 0
        not_taxo = 0
        not_phone = 0
        inserted = 0
        failed_updates = 0
        no_key_in_url = 0
        # head = [next(f) for x in range(150000)]
        # for line in head:
        for line in iter(f.readline, ""):
            i += 1
            if not taxo_pattern.search(line):
                not_taxo += 1
                continue
            match = split_pattern.match(line)
            if match is None:
                skipped += 1
                continue
            props = match.groups()
            subj = props[0]
            predicate = props[1]
            obj = props[2]
            source = props[3]
            if item_pattern.search(source) or (any(url in source for url in domainList) or item_pattern.search(obj)):
                c.execute("INSERT OR IGNORE INTO PHONEREVIEWS (NODE, URL) VALUES (?,?);",(subj, source))
                update_query = "UPDATE PHONEREVIEWS SET "
                params = [obj, subj, source]
                if predicate.lower() == "http://schema.org/Review/reviewBody".lower() and detectLang(obj):
                    update_query += "REVIEWBODY = ? "
                if predicate.lower() == "http://schema.org/Review/description".lower() and detectLang(obj):
                    update_query += "REVIEWBODY = ? "
                if predicate.lower() == "http://schema.org/Review/reviewRating".lower():
                    update_query += "RATING = ? "
                if predicate.lower() == "http://schema.org/Rating/ratingValue".lower():
                    update_query += "REVIEWRATING = ? "
                if predicate.lower() == "http://schema.org/Rating/bestRating".lower():
                    update_query += "BESTRATING = ? "
                if predicate.lower() == "http://schema.org/Rating/worstRating".lower():
                    update_query += "WORSTRATING = ? "
                update_query += "WHERE NODE = ? AND URL = ?;"
                try:
                    c.execute(update_query, params)
                    conn.commit()
                    inserted += 1
                except:
                    # logging.debug("failed to execute for params " + str(update_query) + str(props))
                    failed_updates += 1

logging.debug("detected " + str(detected) + ", inserted: " + str(inserted) +" lines out of " + str(i) + "; not in taxo: " + str(not_taxo))
logging.debug("Done getting Review entries with Reviewbodies, descriptions or websites at the Object having phone or related words")

# + {"pycharm": {"name": "#%%\n"}}
merge_query = "UPDATE phonereviews "\
              "SET REVIEWRATING = (SELECT T.REVIEWRATING FROM phonereviews AS T "\
              "WHERE phonereviews.RATING = T.NODE AND phonereviews.URL = T.URL), "\
              "BESTRATING = (SELECT T.BESTRATING FROM phonereviews AS T "\
              "WHERE phonereviews.RATING = T.NODE AND phonereviews.URL = T.URL), "\
              "WORSTRATING = (SELECT T.WORSTRATING FROM phonereviews AS T "\
              "WHERE phonereviews.RATING = T.NODE AND phonereviews.URL = T.URL) "\
              "WHERE RATING IN (SELECT NODE FROM phonereviews);"

c.execute(merge_query)
conn.commit()

# + {"pycharm": {"name": "#%%\n"}}
df = pd.read_sql_query("SELECT * from phonereviews", conn)
df = df[df.REVIEWBODY.notnull()&df.REVIEWRATING.notnull()]
df = df.drop_duplicates(subset='REVIEWBODY', keep='first')
logging.debug(df.describe)

