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

# +
# System libraries
import logging, os, sys

# Enable logging
logger = logging.getLogger()
fhandler = logging.FileHandler(filename='extractionLog.log', mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fhandler.setFormatter(formatter)
logger.addHandler(fhandler)
logger.setLevel(logging.DEBUG)

#logging.basicConfig(level=logging.DEBUG)

# Intialize tqdm to always use the notebook progress bar
import tqdm
tqdm.tqdm = tqdm.tqdm_notebook

# Third-party libraries
import numpy as np
import pandas as pd

# Studio libraries
from studio_client import Environment

import os
import re
import json
import gzip
import tensorflow as tf
import sqlite3
from datetime import datetime as dt

logging.debug('dependencies loaded')

# -

conn = sqlite3.connect("reviews2.db")
with conn: 
    conn.execute("""
        CREATE TABLE IF NOT EXISTS
            REVIEWS(
                NODE TEXT,
                URL TEXT,bTEXT,
                REVIEWBODY TEXT,
                REVIEWRATING TEXT,
                ITEMREVIEWED TEXT,
                PRIMARY KEY (NODE, URL))
    """)
cursor = conn.cursor()
logging.debug('create reviews2.db successful')

# +
conn = sqlite3.connect("reviews2.db")
cursor = conn.cursor()

taxo_pattern = re.compile("<http://schema.org/Review/reviewBody>|<http://schema.org/Review/ratingValue>|<http://schema.org/Review/itemReviewed>", re.IGNORECASE)
split_pattern = re.compile("^(_:.*)\s(<http:\/\/schema\.org\/Review\/reviewBody>|<http:\/\/schema\.org\/Review\/ratingValue>|<http:\/\/schema\.org\/Review\/itemReviewed>)\s(.*)\s<(.*)>\s\.$", re.IGNORECASE)

with gzip.open("../schema_Review.gz", "rt") as f:
    i = 0
    skipped_lines = 0
    inserted = 0
    not_taxo = 0
    failes_updates = 0
    
    #head = [next(f) for x in range(50)]
    #for line in head:
    for line in iter(f.readline, ""):
      if i % 5000000 == 0:
        #print(str(dt.now()) + ": processed " + str(i / 1000000) + "/657 million lines so far")
        out0 = (str(dt.now()) + ": processed " + str(i / 1000000) + "/657 million lines so far, inserted " + str(inserted) + " lines and skipped " + str(skipped_lines))
        logging.debug(out0)
      i += 1
      if not taxo_pattern.search(line):
        not_taxo += 1
        continue
      match = split_pattern.match(line)
      if match is None:
        skipped_lines += 1
        continue
      props = match.groups()
      with conn: 
        if len(props) != 4:
          print("properties with weird length: " + str(props))
          logging.info('properties with weird length: ' + str(props))
          continue
        subject = props[0]
        predicate = props[1]
        obj = props[2]
        source = props[3]
        conn.execute("INSERT OR IGNORE INTO REVIEWS (NODE, URL) VALUES (?,?)",(subject, source))
        update_query = "UPDATE REVIEWS SET "
        params = [obj, subject, source]
        if predicate.lower() == "<http://schema.org/Review/reviewBody>".lower():
          update_query += "REVIEWBODY = ?"
        if predicate.lower() == "<http://schema.org/Review/ratingValue>".lower():
          update_query += "REVIEWRATING = ?"
        if predicate.lower() == "<http://schema.org/Review/itemReviewed>".lower():
          update_query += "ITEMREVIEWED = ?"
        if predicate.lower() == "<http://schema.org/Review/reviewAspect>".lower():
          update_query += "REVIEWASPECT = ?"
        update_query += " WHERE NODE = ? AND URL = ?;"
        try:
          conn.execute(update_query, params)
          inserted += 1
        except:
          print("failed to execute for params " + str(props))
          failes_updates += 1

out1 = ("inserted " + str(inserted) + " lines and skipped " + str(skipped_lines) + " lines and not in chosen taxonomy " + str(not_taxo))
out2 = ("Done processing the review file")

logging.debug(out1)
logging.debug(out2)
