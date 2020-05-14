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
fhandler = logging.FileHandler(filename='movieReviewWebsites.log', mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fhandler.setFormatter(formatter)
logger.addHandler(fhandler)
logger.setLevel(logging.DEBUG)
# -

import gzip
import re
import pandas as pd
from langdetect import detect

# +
taxo_pattern = re.compile("<http://schema.org/Review>|<http://schema.org/Movie/review>", re.IGNORECASE)
split_pattern = re.compile("^(_:.*)\s<(.*|http:\/\/schema\.org\/Movie\/review)>\s(<http:\/\/schema\.org\/Review>|.*)\s<(.*)>\s\.$", re.IGNORECASE)

with gzip.open("schema_Movie.gz","rt") as f:
    i = 0
    detected = 0
    skipped = 0
    not_taxo = 0
    inserted = 0

    #head = [next(f) for x in range(5000)]
    #print(head)
    #for line in head:
    for line in iter(f.readline, ""):
        i += 1
        if not taxo_pattern.search(line):
            not_taxo += 1
            continue
        #print("line: ", line)
        match = split_pattern.match(line)
        if match is None: 
            skipped += 1
            continue
        detected += 1
        props = match.groups()
        subject = props[0]
        predicate = props[1]
        obj = props[2]
        source = props[3]
        #print("source: ", source)
        with open('moviereview_sites.txt','a') as file:
            file.write(source + "\n")
            inserted += 1
                
logging.debug("detected " + str(detected) + ", inserted: " + str(inserted) +" lines out of " + str(i) + "; not in taxo: " + str(not_taxo))
logging.debug("Done processing the product/categories file")
