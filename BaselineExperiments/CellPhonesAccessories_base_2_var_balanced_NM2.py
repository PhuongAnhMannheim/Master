import logging, gzip, pandas as pd, numpy as np, json
from sklearn import model_selection, preprocessing, metrics, svm
from sklearn.svm import LinearSVC, SVC
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from collections import Counter
from imblearn.under_sampling import NearMiss

# Input
input_file = '../Data/reviews_Cell_Phones_and_Accessories_5.json.gz'
log_file = '../Logs/cellphonebase2_bal.log'

# Enable logging
logger = logging.getLogger()
fhandler = logging.FileHandler(filename=log_file, mode='a')
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

logging.debug("RUN: NearMiss version 2 with balanced training only")
list_test = [0.1, 0.2, 0.3, 0.4, 0.5]
for i in list_test:
    # Split dataset into training set and test set
    test_size = i
    train_size = 1 - i
    X_train, X_test, y_train, y_test = train_test_split(text, target, test_size=i,random_state=109) 

    # label encode the target variable
    encoder = preprocessing.LabelEncoder()
    y_train = encoder.fit_transform(y_train)
    y_test = encoder.fit_transform(y_test)
    logging.debug("label encoding done")

    # Feature 01_Extraction: Bag of Words with TF-IDF
    tfidf_vect_ngram = TfidfVectorizer(analyzer='word', token_pattern=r'\w{1,}', ngram_range=(2,3), max_features=5000)
    tfidf_vect_ngram.fit(text)
    logging.debug("feature extractiion: n-grams + TF-IDF done")

    # transform the training and validation data using tfidf vectorizer object
    xtrain_tfidf_ngram = tfidf_vect_ngram.transform(X_train)
    xtest_tfidf_ngram = tfidf_vect_ngram.transform(X_test)
    logging.debug("transformation into tfidf vectors done")

    # NearMiss 2
    nm2 = NearMiss(version=2)
    X_train_resampled, y_train_resampled = nm2.fit_resample(xtrain_tfidf_ngram, y_train)
    logging.debug("Training set:")
    logging.debug(sorted(Counter(y_train_resampled).items()))
    # X_test_resampled, y_test_resampled = nm2.fit_resample(xtest_tfidf_ngram, y_test)
    logging.debug("Test set:")
    logging.debug(sorted(Counter(y_test).items()))

    #Create a Classifier
    clf = SVC(kernel='linear')
    # Train the model using the training sets
    clf.fit(X_train_resampled, y_train_resampled)
    #Predict the response for test dataset
    y_pred = clf.predict(xtest_tfidf_ngram)
    # logging.debug("model building, training and prediction done")
    # logging.debug('Training target statistics: {}'.format(Counter(y_train_resampled)))
    # logging.debug('Testing target statistics: {}'.format(Counter(y_test)))

    # Model Accuracy, how often is the classifier correct?
    logging.debug("train: " + str(train_size) + "/ test: " + str(test_size))
    accuracy = str(metrics.accuracy_score(y_test, y_pred))
    precision = str(metrics.precision_score(y_test, y_pred, average="macro"))
    f1 = str(metrics.f1_score(y_test, y_pred, average="macro"))
    logging.debug("Accuracy:" + accuracy)
    logging.debug("Precision:" + precision)
    logging.debug("F1:" + f1)
    logging.debug(pd.crosstab(y_test, y_pred))
