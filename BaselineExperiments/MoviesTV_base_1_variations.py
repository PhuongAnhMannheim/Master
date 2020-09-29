import logging, gzip, json, pandas as pd, re, random
from sklearn import model_selection, preprocessing, metrics
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from collections import Counter
from imblearn.under_sampling import RandomUnderSampler
from imblearn.over_sampling import RandomOverSampler, SMOTE, ADASYN, SVMSMOTE
from sklearn.metrics import plot_confusion_matrix
import matplotlib.pyplot as plt

input_file = '../Data/reviews_Movies_and_TV_5.json.gz'
log = '../Logs/moviesbase1.log'

method = "MultinomialNB"
feature = "CountVectorizer(uni, bi, tri)"
balance = "RandomUnderSampler"
preprocess = "unpreprocessed"

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

data = random.sample(data, 200000)
df = pd.DataFrame.from_dict(data)
target = df['overall']
text = df['reviewText']

logging.debug(f"RUN: Baseline, Movies, {feature}, {method}, {balance}, {preprocess}")

# Feature 01_Extraction: Bag of Words with TF-IDF
# tfidf_vect = TfidfVectorizer(analyzer='word', token_pattern=r'\w{1,}')
# tfidf_vect.fit(text)
# logging.debug("feature extractiion: BoW + TF-IDF done")
cv = CountVectorizer(ngram_range=(1, 3))
cv.fit(text)
text_count = cv.transform(text)
logging.debug(f"feature extraction: {feature} done")

# Balancing
rus = RandomUnderSampler(random_state=None)
text_count_res, target_res = rus.fit_resample(text_count, target)
logging.debug(f"Balancing: {balance} done")

# Create a Binomial Classifier
nb = MultinomialNB()
logging.debug(f"classifier creation: {method} done")

list_test = [0.1, 0.2, 0.3, 0.4, 0.5]
for i in list_test:
    # Split dataset into training set and test set
    test_size = i
    train_size = 1 - i
    logging.debug(test_size)
    logging.debug(train_size)
    X_train, X_test, y_train, y_test = train_test_split(text_count_res, target_res, test_size=i,random_state=109)

    logging.debug('Training target statistics: {}'.format(Counter(y_train), sorted(y_train)))
    logging.debug('Testing target statistics: {}'.format(Counter(y_test), sorted(y_test)))

    # Train the model using the training sets
    nb.fit(X_train, y_train)
    #Predict the response for test dataset
    y_pred = nb.predict(X_test)
    logging.debug("model building, training and prediction done")

    # Model Accuracy, how often is the classifier correct?
    logging.debug("train: "+ str(train_size) + "/ test: " + str(test_size))
    accuracy = str(metrics.accuracy_score(y_test, y_pred))
    precision = str(metrics.precision_score(y_test, y_pred, average="macro"))
    f1 = str(metrics.f1_score(y_test, y_pred, average="macro"))
    logging.debug("Accuracy:" +  accuracy)
    logging.debug("Precision:" +  precision)
    logging.debug("F1:" + f1)
    logging.debug(pd.crosstab(y_test, y_pred))

    # Visualization of Confusion Matrix and saving
    plt.rcParams['figure.facecolor'] = 'white'
    title = f"Confusion matrix - Baseline({method}, {feature}, {balance}, {preprocess}, {train_size}_{test_size})"
    disp = plot_confusion_matrix(nb, X_test, y_test,
                                 display_labels=[1.0, 2.0, 3.0, 4.0, 5.0],
                                 cmap=plt.cm.Blues)
    disp.ax_.set_title(title)
    plt.savefig(f'Results/type1_Movie/{title}.png', bbox_inches='tight')

    title_norm = title + "_normalize"
    disp_norm = plot_confusion_matrix(nb, X_test, y_test,
                                      display_labels=[1.0, 2.0, 3.0, 4.0, 5.0],
                                      cmap=plt.cm.Blues,
                                      normalize='true')
    disp_norm.ax_.set_title(title_norm)
    plt.savefig(f'Results/type1_Movie/{title_norm}.png', bbox_inches='tight')

    # TODO: own vocabulary based on the most frequent words
    # def mytokenizer(text):
    #     return text.split()
    #
    #
    # from sklearn.feature_extraction.text import CountVectorizer
    #
    # corpus = ['www.google.com www.google.com', 'www.google.com www.facebook.com', 'www.google.com', 'www.facebook.com']
    # vocab = {'www.google.com': 0, 'www.facebook.com': 1}
    # vectorizer = CountVectorizer(vocabulary=vocab, tokenizer=mytokenizer)
    # X = vectorizer.fit_transform(corpus)
    # print(vectorizer.get_feature_names())
    # print(X.toarray())