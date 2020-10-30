# -*- coding: utf-8 -*-
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

# # Setting up the Environment
#

# +
# System libraries
import logging, os, sys

# Enable logging
logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO, stream=sys.stdout)

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
print("dependencies loaded")

# +
# Initialize environment
env = Environment(project="Semantic Analysis"  # Studio project you want to work on
                  # Only required in stand-alone workspace deployments
                  # studio_endpoint="STUDIO_ENDPOINT", # Studio endpoint url: e.g. http://10.2.3.45:8091
                  # studio_api_token="STUDIO_API_TOKEN"
                 ) 

# Initialize experiment
# -

# !wget http://data.dws.informatik.uni-mannheim.de/structureddata/2018-12/quads/classspecific/md/schema_Review.gz
print("schema_Review.gz")

conn = sqlite3.connect("reviews.db")
with conn: 
    conn.execute("""
        CREATE TABLE IF NOT EXISTS
            REVIEWS(
                NODE TEXT,
                URL TEXT,bTEXT,
                REVIEWBODY TEXT,
                REVIEWRATING TEXT,
                ITEMREVIEWED TEXT,
                REVIEWASPECT TEXT,
                REVIEWAUTHOR TEXT, 
                REVIEWDESCR TEXT, 
                PRIMARY KEY (NODE, URL))
    """)
cursor = conn.cursor()
print("create reviews.db successful")

# + {"code_folding": []}
# -> reviews.db -> converted to reviews_all.db
conn = sqlite3.connect("reviews.db")
cursor = conn.cursor()

taxo_pattern = re.compile("<http://schema.org/Review/reviewBody>|<http://schema.org/Review/ratingValue>|<http://schema.org/Review/itemReviewed>|<http://schema.org/Review/reviewAspect>|<http://schema.org/Review/author>|<http://schema.org/Review/description>", re.IGNORECASE)
split_pattern = re.compile("^(_:.*)\s(<http:\/\/schema\.org\/Review\/reviewBody>|<http:\/\/schema\.org\/Review\/ratingValue>|<http:\/\/schema\.org\/Review\/itemReviewed>|<http:\/\/schema\.org\/Review\/reviewAspect>|<http:\/\/schema\.org\/Review\/author>|<http:\/\/schema\.org\/Review\/description>)\s(.*)\s<(.*)>\s\.$", re.IGNORECASE)

with gzip.open("schema_Review.gz", "rt") as f:
    i = 0
    skipped_lines = 0
    inserted = 0
    not_taxo = 0
    failes_updates = 0
    # head = [next(f) for x in range(50)]
    # print(head)
    #for line in head: 
      # print(line)
    for line in iter(f.readline, ""):
      if i % 5000000 == 0:
        print(str(dt.now()) + ": processed " + str(i / 1000000) + "/6321 million lines so far")
      i += 1
      if not taxo_pattern.search(line):
        # print("not taxo")
        not_taxo += 1
        continue
      match = split_pattern.match(line)
      if match is None:
        skipped_lines += 1
        # print("not match" + str(line))  
        continue
      props = match.groups()
      with conn: 
        if len(props) != 4:
          print("properties with weird length: " + str(props))
          continue
        subject = props[0]
        predicate = props[1]
        obj = props[2]
        source = props[3]
        conn.execute("INSERT OR IGNORE INTO REVIEWS (NODE, URL) VALUES (?,?)",(subject, source))
        update_query = "UPDATE REVIEWS SET "
        params = [obj, subject, source]
        # print(params)
        if predicate.lower() == "<http://schema.org/Review/reviewBody>".lower():
          update_query += "REVIEWBODY = ?"
        if predicate.lower() == "<http://schema.org/Review/ratingValue>".lower():
          update_query += "REVIEWRATING = ?"
        if predicate.lower() == "<http://schema.org/Review/itemReviewed>".lower():
          update_query += "ITEMREVIEWED = ?"
        if predicate.lower() == "<http://schema.org/Review/reviewAspect>".lower():
          update_query += "REVIEWASPECT = ?"
        if predicate.lower() == "<http://schema.org/Review/author>".lower():
          update_query += "REVIEWAUTHOR = ?"
        if predicate.lower() == "<http://schema.org/Review/description>".lower():
          update_query += "REVIEWDESCR = ?"
        if predicate.lower() == "<http://schema.org/Review/datePublished".lower():
          update_query += "REVIEWDATE = ?"
        if predicate.lower() == "<http://schema.org/Review/reviewRating".lower():
          update_query += "REVIEWRATING = ?"  
        update_query += " WHERE NODE = ? AND URL = ?;"
        try:
          # print(update_query, params)
          conn.execute(update_query, params)
          # print(props)
          inserted += 1
        except:
          print("failed to execute for params " + str(props))
          failes_updates += 1

print("inserted " + str(inserted) + " lines and skipped " + str(skipped_lines) + " lines and not in chosen taxonomy " + str(not_taxo))
print("Done processing the review file")


# -

# noch einmal die Zelle von oben durchlaufen lassen, nur zum Zählen und nicht zum Schreiben in die Datenbank

# +
def total_rows(cursor, table_name, print_out=False):
    """ Returns the total number of rows in the database """
    cursor.execute('SELECT COUNT(*) FROM {}'.format(table_name))
    count = cursor.fetchall()
    if print_out:
        print('\nTotal rows: {}'.format(count[0][0]))
    return count[0][0]

total_rows(cursor, "REVIEWS")
