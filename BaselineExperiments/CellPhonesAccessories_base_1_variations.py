import logging, gzip, json, pandas as pd
from sklearn import model_selection, preprocessing, metrics
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from collections import Counter

# Input
input_file = '../Data/reviews_Cell_Phones_and_Accessories_5.json.gz'
log = '../Logs/cellphonebase1.log'

# Enable logging
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

logging.debug("RUN: CountVectorizer, MultinomialNB on imbalanced Data set")
list_test = [0.1, 0.2, 0.3, 0.4, 0.5]
for i in list_test:
    # Split dataset into training set and test set
    test_size = i
    train_size = 1 - i
    logging.debug(test_size)
    logging.debug(train_size)
    X_train, X_test, y_train, y_test = train_test_split(text, target, test_size=i,random_state=109)

    # # Feature Extraction: Bag of Words with TF-IDF
    # tfidf_vect = TfidfVectorizer(analyzer='word', token_pattern=r'\w{1,}')
    # tfidf_vect.fit(text)
    # logging.debug("feature extractiion: BoW + TF-IDF done")

    # Feature Extraction: CountVectorizer
    cv = CountVectorizer()
    cv.fit(text)
    logging.debug("feature extractiion: CountVectorizer done")

    # transform the training and validation data using tfidf vectorizer object
    xtrain_count = cv.transform(X_train)
    xtest_count = cv.transform(X_test)
    logging.debug("transformation into count vectors done")

    logging.debug("Training set:")
    logging.debug(sorted(Counter(y_train).items()))

    #Create a Binomial Classifier
    nb = MultinomialNB()
    # Train the model using the training sets
    nb.fit(xtrain_count, y_train)
    #Predict the response for test dataset
    y_pred = nb.predict(xtest_count)
    logging.debug("model building, training and prediction done")
    logging.debug("model building, training and prediction done")
    logging.debug('Training target statistics: {}'.format(Counter(y_train)))
    logging.debug('Testing target statistics: {}'.format(Counter(y_test)))
    # Model Accuracy, how often is the classifier correct?
    logging.debug("train: " + str(train_size) + "/ test: " + str(test_size))
    accuracy = str(metrics.accuracy_score(y_test, y_pred))
    precision = str(metrics.precision_score(y_test, y_pred, average="macro"))
    f1 = str(metrics.f1_score(y_test, y_pred, average="macro"))
    logging.debug("Accuracy:" + accuracy)
    logging.debug("Precision:" + precision)
    logging.debug("F1:" + f1)

