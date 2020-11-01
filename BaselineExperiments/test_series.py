import sys
sys.path.append("..")
from Scripts import loading as dl

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.svm import SVC
from sklearn import metrics
from sklearn.metrics import plot_confusion_matrix, classification_report
import matplotlib.pyplot as plt


def run(domain, trial, schema_rev_link, amazon_rev_link, schema_rev_size, amazon_rev_size):
    df = dl.load_merged_data(schema_rev_link, amazon_rev_link, schema_rev_size, amazon_rev_size)

    text = df.text_prep
    target = df.label
    target = target.astype('int')

    seed = 7
    x_train, x_test, y_train, y_test = train_test_split(text, target, test_size=0.25, random_state=seed,
                                                        stratify=df.label)

    vect = TfidfVectorizer(binary=True, max_df=0.75, min_df=1, ngram_range=(1, 2))
    train_vectorized = vect.fit_transform(x_train)
    vocab = vect.get_feature_names()

    test_vectorized = vect.transform(x_test)

    vectorizer_fs = SelectKBest(score_func=chi2, k=4000)
    fs_train_vectorized = vectorizer_fs.fit_transform(train_vectorized, y_train)
    fs_test_vectorized = vectorizer_fs.transform(test_vectorized)

    clf = SVC(C=1.0, decision_function_shape='ovo', gamma='auto', kernel='linear')
    clf.fit(fs_train_vectorized, y_train)

    y_pred = clf.predict(fs_test_vectorized)

    print(f"######## RESULT: {domain}_{trial}_{schema_rev_size}_{amazon_rev_size}")
    print("vocabulary size: ", len(vocab))
    accuracy = str(metrics.accuracy_score(y_test, y_pred))
    precision = str(metrics.precision_score(y_test, y_pred, average="macro"))
    recall = str(metrics.recall_score(y_test, y_pred, average="macro"))
    f1 = str(metrics.f1_score(y_test, y_pred, average="macro"))
    print("Accuracy:" + accuracy)
    print("Precision:" + precision)
    print("Recall: " + recall)
    print("F1:" + f1)
    print(classification_report(y_test, y_pred, target_names=['class_1', 'class_2', 'class_3', 'class_4', 'class_5']))
    title = f"{domain}_{trial}_{schema_rev_size}_{amazon_rev_size}"
    disp = plot_confusion_matrix(clf, fs_test_vectorized, y_test,
                                 display_labels=[1.0, 2.0, 3.0, 4.0, 5.0],
                                 cmap=plt.cm.Blues)
    disp.ax_.set_title(title)
    plt.savefig(f'results/test_series_chi/{title}.png', dpi=200)

    title_norm = title + "_normalize"
    disp_norm = plot_confusion_matrix(clf, fs_test_vectorized, y_test,
                                      display_labels=[1.0, 2.0, 3.0, 4.0, 5.0],
                                      cmap=plt.cm.Blues,
                                      normalize='true')
    disp_norm.ax_.set_title(title_norm)
    plt.savefig(f'results/test_series_chi/{title_norm}.png', dpi=200)

    case_1 = 0
    case_2 = 0
    case_3 = 0
    case_4 = 0
    case_5 = 0
    case_6 = 0
    case_7 = 0
    case_8 = 0
    for (input_text, pred, label) in zip(x_test, y_pred, y_test):
        if pred == 3.0 and label in [1.0, 2.0, 4.0, 5.0]:
            case_1 += 1
        if pred in [1.0, 2.0, 4.0, 5.0] and label == 3.0:
            case_2 += 1
        if pred in [1.0, 2.0] and label in [4.0, 5.0]:
            case_3 += 1
        if pred in [4.0, 5.0] and label in [1.0, 2.0]:
            case_4 += 1
        if pred == 1.0 and label == 2.0:
            case_5 += 1
        if pred == 2.0 and label == 1.0:
            case_6 += 1
        if pred == 4.0 and label == 5.0:
            case_7 += 1
        if pred == 5.0 and label == 4.0:
            case_8 += 1
    print('case_1', 'case_2', 'case_3', 'case_4', 'case_5', 'case_6', 'case_7', 'case_8')
    print(case_1, case_2, case_3, case_4, case_5, case_6, case_7, case_8)
    print('')
    return f1


print('######### test series 1')
count_trial = '1'
domains = ['phone', 'movie']
for d in domains:
    limit = 1000
    schema_size = 0
    amazon_link = f'../Data/amazon_{d}.pkl'
    schema_link = f'../Data/schema_{d}.pkl'

    print(f"######## {d}, test series {count_trial}")
    results = {}

    while schema_size <= 1000:
        amazon_size = limit - schema_size
        result = run(d, count_trial, schema_link, amazon_link, schema_size, amazon_size)
        results[f"{d}_{count_trial}_{schema_size}_{amazon_size}"] = result

        schema_size = schema_size + 250
        amazon_size = limit - schema_size

    bigIndex = max([[results[key], key] for key in results])
    print(f'######## BEST RESULTS of trial{count_trial}_{d}')
    print(bigIndex)


print('######### test series 2')
count_trial = '2'
domains = ['phone', 'movie']
for d in domains:
    limit = 2000
    schema_size = 1000
    amazon_link = f'../Data/amazon_{d}.pkl'
    schema_link = f'../Data/schema_{d}.pkl'
    print(f"######## {d}, test series {count_trial}")
    results = {}

    while schema_size >= 0:
        amazon_size = limit - schema_size
        result = run(d, count_trial, schema_link, amazon_link, schema_size, amazon_size)
        results[f"{d}_{count_trial}_{schema_size}_{amazon_size}"] = result
        schema_size = schema_size - 200

    bigIndex = max([[results[key], key] for key in results])
    print(f'######## BEST RESULTS of trial{count_trial}_{d}')
    print(bigIndex)


print('######### test series 3')
count_trial = '3'

domains = ['phone', 'movie']
for d in domains:
    limit = 10000
    schema_size = 0
    amazon_link = f'../Data/amazon_{d}.pkl'
    schema_link = f'../Data/schema_{d}.pkl'
    print(f"######## {d}, test series {count_trial}")
    results = {}
    while schema_size <= 10000:
        amazon_size = limit - schema_size
        result = run(d, count_trial, schema_link, amazon_link, schema_size, amazon_size)
        results[f"{d}_{count_trial}_{schema_size}_{amazon_size}"] = result
        schema_size = schema_size + 100

    bigIndex = max([[results[key], key] for key in results])
    print(f'######## BEST RESULTS of trial{count_trial}_{d}')
    print(bigIndex)


print('######### test series 4')
count_trial = 4
limit = 1000
domains = ['phone', 'movie']
for d in domains:
    amazon_link = f'../Data/amazon_{d}.pkl'
    schema_link = f'../Data/schema_{d}.pkl'
    print(f"{d}, test series {count_trial}")
    while limit >= 500:
        result = run(d, count_trial, schema_link, amazon_link, limit, limit)
        results[f"{d}_{count_trial}_{schema_size}_{amazon_size}"] = result

        limit = limit - 100

    bigIndex = max([[results[key], key] for key in results])
    print(f'######## BEST RESULTS of trial{count_trial}_{d}')
    print(bigIndex)

    limit = 1000
print('finished!')
