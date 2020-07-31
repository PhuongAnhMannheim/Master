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
# Imports
import logging, sqlite3, re, gzip, pandas as pd

# Input:
movies_path = '../Data/schema_Movie.gz'
reviews_path= '../Data/schema_Review.gz'
inputlist = [movies_path,reviews_path]

# Output:
moviewreviewslog_path = '../Logs/movieReviews.log'
moviesreviewsdb_path = '../Data/input/moviereviews.db'

# enable Logging:
logger = logging.getLogger()
fhandler = logging.FileHandler(filename=moviewreviewslog_path, mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fhandler.setFormatter(formatter)
logger.addHandler(fhandler)
logger.setLevel(logging.DEBUG)

# DB
conn = sqlite3.connect(moviesreviewsdb_path)
c = conn.cursor()
c.execute("""
        CREATE TABLE IF NOT EXISTS
            moviereviews(
                NODE TEXT,
                URL TEXT,
                REVIEWBODY TEXT,
                RATING TEXT,
                REVIEWRATING TEXT,
                BESTRATING TEXT,
                WORSTRATING TEXT,
                PRIMARY KEY (NODE, URL))
    """)

# Pattern
taxo_pattern = re.compile("<http://schema.org/Review/description>|"\
                          "<http://schema.org/Review/reviewBody>|"\
                          "<http://schema.org/Review/reviewRating>|"\
                          "<http://schema.org/Rating/worstRating>|"\
                          "<http://schema.org/Rating/bestRating>|"\
                          "<http://schema.org/Rating/ratingValue>", re.IGNORECASE)
split_pattern = re.compile("^(_:.*)\s<(.*)>\s(.*)\s<(.*)>\s\.$", re.IGNORECASE)

# Search based on url of valid movie and tv reviews
url_lst = ['https://in.bookmyshow.com', 'https://thereviewmonk.com',
           'https://www.noopler.com', 'http://reviewschview.com',
           'https://www.flickfilosopher.com', 'https://www.rogerebert.com',
           'https://deepfocusreview.com', 'https://www.telegraph.co.uk',
           'https://nationalpost.com', 'https://www.imdb.com']
for input in inputlist:
    for url in url_lst:
        url_pattern = re.compile(url,re.IGNORECASE)
        with gzip.open(input,"rt") as f:
            i = 0
            detected = 0
            skipped = 0
            not_taxo = 0
            not_url = 0
            inserted = 0
            failed_updates = 0
            for line in f:
                i += 1
                if not url_pattern.search(line):
                    not_url += 1
                    continue
                if not taxo_pattern.search(line):
                    not_taxo
                    continue
                match = split_pattern.match(line)
                if match is None:
                    skipped += 1
                    continue
                detected += 1
                props = match.groups()
                subj = props[0]
                predicate = props[1]
                obj = props[2]
                source = props[3]
                c.execute("INSERT OR IGNORE INTO MOVIEREVIEWS (NODE, URL) VALUES (?,?);",(subj, source))
                update_query = "UPDATE MOVIEREVIEWS SET "
                params = [obj, subj, source]
                if predicate.lower() == "http://schema.org/Review/reviewBody".lower():
                    update_query += "REVIEWBODY = ? "
                if predicate.lower() == "http://schema.org/Review/description".lower():
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
                    logging.debug("failed to execute for params " + str(update_query) + str(props))
                    failed_updates += 1

logging.debug("detected " + str(detected) + ", inserted: " + str(inserted) +" lines out of " + str(i) + "; not in taxo: " + str(not_taxo))
logging.debug("Done processing the movie reviews file from Movie.gz and Review.gz after the database got deleted")




