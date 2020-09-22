import logging, gzip, json, pandas as pd
from sklearn import model_selection, preprocessing, metrics
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.svm import LinearSVC, SVC
from collections import Counter
from imblearn.under_sampling import RandomUnderSampler
from imblearn.over_sampling import RandomOverSampler, SMOTE, ADASYN, SVMSMOTE
from sklearn.metrics import plot_confusion_matrix
import matplotlib.pyplot as plt

# Input
input_file = '../Data/reviews_Cell_Phones_and_Accessories_5.json.gz'
log_file = '../Logs/cellphonebase2_bal.log'

method = "SVC"
feature = "CountVectorizer(uni, bi, tri)"
balance = "RandomOverSampler"
preprocess = "unpreprocessed"

# Enable logging
logger = logging.getLogger()
fhandler = logging.FileHandler(filename=log_file, mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fhandler.setFormatter(formatter)
logger.addHandler(fhandler)
logger.setLevel(logging.DEBUG)

data = []
with gzip.open(input_file) as f:
    for line in f:
        data.append(json.loads(line.strip()))

df = pd.DataFrame.from_dict(data)
target = df['overall']
text = df['reviewText']

logging.debug(f"RUN: Baseline, Cellphone, {feature}, {method}, {balance}, {preprocess}")

# Feature Extraction: Bag of Words with TF-IDF
# tfidf_vect = TfidfVectorizer(analyzer='word', token_pattern=r'\w{1,}')
# tfidf_vect.fit(text)
# text_tfidf = tfidf_vect.transform(text)
# logging.debug("feature extractiion: BoW + TF-IDF done")
cv = CountVectorizer(ngram_range=(1, 3))
cv.fit(text)
text_count = cv.transform(text)
logging.debug(f"feature extraction: {feature} done")

# RandomUnderSampler
# rus = RandomUnderSampler(random_state=0)
rus = RandomUnderSampler(random_state=None)
text_count_res, target_res = rus.fit_resample(text_count, target)
logging.debug(f"Balancing: {balance} done")


# Create a Binomial Classifier
clf = SVC(kernel='linear')
logging.debug(f"classifier creation: {method} done")

list_test = [0.1, 0.2, 0.3, 0.4, 0.5]
for i in list_test:
    # Split dataset into training set and test set
    test_size = i
    train_size = 1 - i
    X_train, X_test, y_train, y_test = train_test_split(text_count_res, target_res, test_size=i, random_state=109)

    logging.debug('Training target statistics: {}'.format(Counter(y_train), sorted(y_train)))
    logging.debug('Testing target statistics: {}'.format(Counter(y_test), sorted(y_test)))

    # Train the model using the balanced training sets
    clf.fit(X_train, y_train)
    # Predict the response for test dataset
    y_pred = clf.predict(X_test)
    # logging.debug("model building, training and prediction done")
    # logging.debug('Training target statistics: {}'.format(Counter(y_train_resampled)))
    # logging.debug('Testing target statistics: {}'.format(Counter(y_test)))

    # Classify and report the results
    # logging.debug(classification_report_imbalanced(y_test, pipeline.predict(xtest_tfidf)))

    # Model Accuracy, how often is the classifier correct?
    logging.debug("train: " + str(train_size) + "/ test: " + str(test_size))
    accuracy = str(metrics.accuracy_score(y_test, y_pred))
    precision = str(metrics.precision_score(y_test, y_pred, average="macro"))
    f1 = str(metrics.f1_score(y_test, y_pred, average="macro"))
    logging.debug("Accuracy:" + accuracy)
    logging.debug("Precision:" + precision)
    logging.debug("F1:" + f1)
    logging.debug(pd.crosstab(y_test, y_pred))

    # Visualization of Confusion Matrix and saving
    plt.rcParams['figure.facecolor'] = 'white'
    title = f"Confusion matrix - Baseline({method}, {feature}, {balance}, {preprocess}, {train_size}_{test_size})"
    disp = plot_confusion_matrix(clf, X_test, y_test,
                                 display_labels=[1.0, 2.0, 3.0, 4.0, 5.0],
                                 cmap=plt.cm.Blues)
    disp.ax_.set_title(title)
    plt.savefig(f'Results/SVM_Cellphone/{title}.png', bbox_inches='tight')

    title_norm = title + "_normalize"
    disp_norm = plot_confusion_matrix(clf, X_test, y_test,
                                      display_labels=[1.0, 2.0, 3.0, 4.0, 5.0],
                                      cmap=plt.cm.Blues,
                                      normalize='true')
    disp_norm.ax_.set_title(title_norm)
    plt.savefig(f'Results/SVM_Cellphone/{title_norm}.png', bbox_inches='tight')