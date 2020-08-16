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
fhandler = logging.FileHandler(filename='cellphonebase#2.log', mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fhandler.setFormatter(formatter)
logger.addHandler(fhandler)
logger.setLevel(logging.DEBUG)

# +
import gzip
import pandas as pd
import numpy as np
import json

from sklearn import model_selection, preprocessing, metrics, svm
from sklearn.svm import LinearSVC, SVC
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer

# +
data = []
with gzip.open('reviews_Cell_Phones_and_Accessories_5.json.gz') as f: 
    for l in f: 
        data.append(json.loads(l.strip()))
        
print(len(data))

df = pd.DataFrame.from_dict(data)
print(len(df))

target = df['overall']
text = df['reviewText']
# -

list_test = [0.1, 0.2, 0.3, 0.4, 0.5]
for i in list_test:
    # Split dataset into training set and test set
    test_size = i
    train_size = 1 - i
    logging.debug(test_size)
    logging.debug(train_size)
    X_train, X_test, y_train, y_test = train_test_split(text, target, test_size=i,random_state=109) 

    # label encode the target variable
    encoder = preprocessing.LabelEncoder()
    y_train = encoder.fit_transform(y_train)
    y_test = encoder.fit_transform(y_test)
    logging.debug("label encoding done")

    # Feature Extraction: Bag of Words with TF-IDF
    tfidf_vect_ngram = TfidfVectorizer(analyzer='word', token_pattern=r'\w{1,}', ngram_range=(2,3), max_features=5000)
    tfidf_vect_ngram.fit(text)
    logging.debug("feature extractiion: n-grams + TF-IDF done")

    # transform the training and validation data using tfidf vectorizer object
    xtrain_tfidf_ngram =  tfidf_vect_ngram.transform(X_train)
    xtest_tfidf_ngram =  tfidf_vect_ngram.transform(X_test)
    logging.debug("transformation into tfidf vectors done")

    #Create a Classifier
    clf = svm.SVC(kernel='linear')
    # Train the model using the training sets
    clf.fit(xtrain_tfidf_ngram, y_train)
    #Predict the response for test dataset
    y_pred = clf.predict(xtest_tfidf_ngram)
    logging.debug("model building, training and prediction done")

    # Model Accuracy, how often is the classifier correct?
    logging.debug("train: "+ str(train_size) + "/ test: " + str(test_size))
    accuracy = str(metrics.accuracy_score(y_test, y_pred))
    precision = str(metrics.precision_score(y_test, y_pred, average="macro"))
    f1 = str(metrics.f1_score(y_test, y_pred, average="macro"))
    logging.debug("Accuracy:" +  accuracy)
    logging.debug("Precision:" +  precision)
    logging.debug("F1:" + f1)

