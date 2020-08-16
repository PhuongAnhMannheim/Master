from sklearn.linear_model import LogisticRegression
import gzip, pandas as pd, random, logging
import numpy as np
from sklearn import model_selection, preprocessing, metrics
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
import json

logger = logging.getLogger()
fhandler = logging.FileHandler(filename='../Logs/movielogRegression.log', mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fhandler.setFormatter(formatter)
logger.addHandler(fhandler)
logger.setLevel(logging.DEBUG)

data = []
with gzip.open('../Data/reviews_Movies_and_TV_5.json.gz') as f:
    for l in f:
        data.append(json.loads(l.strip()))
data = random.sample(data, 200000)

df = pd.DataFrame.from_dict(data)

target = df['overall']
text = df['reviewText']

train_size = 0.5
test_size = 0.5

# Split dataset into training set and test set
X_train, X_test, y_train, y_test = train_test_split(text, target, test_size = test_size, random_state=109)

# label encode the target variable
encoder = preprocessing.LabelEncoder()
y_train = encoder.fit_transform(y_train)
y_test = encoder.fit_transform(y_test)
logging.debug("label encoding done")

# Feature Extraction: n-grams with TF-IDF
tfidf_vect_ngram = TfidfVectorizer(analyzer='word', token_pattern=r'\w{1,}', ngram_range=(2,3), max_features=5000)
tfidf_vect_ngram.fit(text)
logging.debug("feature extractiion: n-grams + TF-IDF done")

xtrain_tfidf_ngram =  tfidf_vect_ngram.transform(X_train)
xtest_tfidf_ngram =  tfidf_vect_ngram.transform(X_test)
logging.debug("transformation into tfidf vectors done")

m = LogisticRegression(C=0.1, dual=False)
m.fit(xtrain_tfidf_ngram, y_train)
y_pred = m.predict(xtest_tfidf_ngram)
logging.debug("model building, training and prediction done")

# Model Accuracy, how often is the classifier correct?
logging.debug("train: " + str(train_size) + "/ test: " + str(test_size))
accuracy = str(metrics.accuracy_score(y_test, y_pred))
precision = str(metrics.precision_score(y_test, y_pred, average="macro"))
f1 = str(metrics.f1_score(y_test, y_pred, average="macro"))
logging.debug("Accuracy:" + accuracy)
logging.debug("Precision:" + precision)
logging.debug("F1:" + f1)
