from sklearn.linear_model import LogisticRegression
import gzip, pandas as pd, random, logging
# import numpy as np
from sklearn import model_selection, preprocessing, metrics
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from imblearn.over_sampling import RandomOverSampler
import json
from collections import Counter


# Input
input_file = '../Data/reviews_Cell_Phones_and_Accessories_5.json.gz'
log = '../Logs/cellphonebase1_bal.log'

method = "LogisticRegression"
feature = "CountVectorizer(uni, bi, tri)"
balance = "RandomOverSampler"
preprocess = "unpreprocessed"

logger = logging.getLogger()
fhandler = logging.FileHandler(filename=log, mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fhandler.setFormatter(formatter)
logger.addHandler(fhandler)
logger.setLevel(logging.DEBUG)

data = []
with gzip.open(input_file) as f:
    for l in f:
        data.append(json.loads(l.strip()))

df = pd.DataFrame.from_dict(data)

target = df['overall']
text = df['reviewText']

logging.debug(f"RUN: Baseline, Cellphone, {feature}, {method}, {balance}, {preprocess}")

# Feature 01_extraction: n-grams with TF-IDF
# tfidf_vect_ngram = TfidfVectorizer(analyzer='word', token_pattern=r'\w{1,}', ngram_range=(2, 3), max_features=5000)
# tfidf_vect_ngram.fit(text)
# logging.debug("feature extractiion: n-grams + TF-IDF done")
# xtrain_tfidf_ngram = tfidf_vect_ngram.transform(X_train)
# xtest_tfidf_ngram = tfidf_vect_ngram.transform(X_test)
# logging.debug("transformation into tfidf vectors done")

cv = CountVectorizer(ngram_range=(1, 3))
cv.fit(text)
text_count = cv.transform(text)
logging.debug(f"feature extraction: {feature} done")

ros = RandomOverSampler(random_state=None)
text_count_res, target_res = ros.fit_resample(text_count, target)
logging.debug(f"Balancing: {balance} done")

m = LogisticRegression(C=0.1, dual=False)
logging.debug(f"classifier creation: {method} done")

list_test = [0.1, 0.2, 0.3, 0.4, 0.5]
for i in list_test:
    test_size = i
    train_size = 1 - i
    logging.debug("test size: " + str(test_size))
    logging.debug("train size: " + str(train_size))
    # Split dataset into training set and test set
    X_train, X_test, y_train, y_test = train_test_split(text_count_res, target_res, test_size = test_size, random_state=109)

    logging.debug('Training target statistics: {}'.format(Counter(y_train), sorted(y_train)))
    logging.debug('Testing target statistics: {}'.format(Counter(y_test), sorted(y_test)))

    m.fit(X_train, y_train)
    y_pred = m.predict(X_test)
    logging.debug("model building, training and prediction done")

    # Model Accuracy, how often is the classifier correct?
    logging.debug("train: " + str(train_size) + "/ test: " + str(test_size))
    accuracy = str(metrics.accuracy_score(y_test, y_pred))
    precision = str(metrics.precision_score(y_test, y_pred, average="macro"))
    f1 = str(metrics.f1_score(y_test, y_pred, average="macro"))
    logging.debug("Accuracy:" + accuracy)
    logging.debug("Precision:" + precision)
    logging.debug("F1:" + f1)
