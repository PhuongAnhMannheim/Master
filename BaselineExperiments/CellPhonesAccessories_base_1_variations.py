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
fhandler = logging.FileHandler(filename='cellphonebase1.log', mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fhandler.setFormatter(formatter)
logger.addHandler(fhandler)
logger.setLevel(logging.DEBUG)

# +
import gzip
import pandas as pd
import numpy as np
import json

from sklearn import model_selection, preprocessing, metrics
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

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
    tfidf_vect = TfidfVectorizer(analyzer='word', token_pattern=r'\w{1,}')
    tfidf_vect.fit(text)
    logging.debug("feature extractiion: BoW + TF-IDF done")

    # transform the training and validation data using tfidf vectorizer object
    xtrain_tfidf =  tfidf_vect.transform(X_train)
    xtest_tfidf =  tfidf_vect.transform(X_test)
    logging.debug("transformation into tfidf vectors done")

    #Create a Binomial Classifier
    nb = MultinomialNB()
    # Train the model using the training sets
    nb.fit(xtrain_tfidf, y_train)
    #Predict the response for test dataset
    y_pred = nb.predict(xtest_tfidf)
    logging.debug("model building, training and prediction done")

    # Model Accuracy, how often is the classifier correct?
    logging.debug("train: "+ str(train_size) + "/ test: " + str(test_size))
    accuracy = str(metrics.accuracy_score(y_test, y_pred))
    precision = str(metrics.precision_score(y_test, y_pred, average="macro"))
    f1 = str(metrics.f1_score(y_test, y_pred, average="macro"))
    logging.debug("Accuracy:" +  accuracy)
    logging.debug("Precision:" +  precision)
    logging.debug("F1:" + f1)

