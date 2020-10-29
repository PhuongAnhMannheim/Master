
import pandas as pd
import random
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.svm import SVC, SVR

amazon_link = '../Data/amazon_movie.pkl'

# ToDo: reference to module
# from Scripts import loading as dl
# df = dl.load_sampled(amazon_link, 5000)
def load_sampled(link, per_class):
    df = pd.read_pickle(link)
    df_1 = df[df['label'] == 1.0].values.tolist()
    df_2 = df[df['label'] == 2.0].values.tolist()
    df_3 = df[df['label'] == 3.0].values.tolist()
    df_4 = df[df['label'] == 4.0].values.tolist()
    df_5 = df[df['label'] == 5.0].values.tolist()

    try:
        random.seed(123)
        adf1 = random.sample(df_1, per_class)
    except ValueError:
        random.seed(123)
        adf1 = random.choices(df_1, k=per_class)
    try:
        random.seed(123)
        adf2 = random.sample(df_2, per_class)
    except ValueError:
        random.seed(123)
        adf2 = random.choices(df_2, k=per_class)
    try:
        random.seed(123)
        adf3 = random.sample(df_3, per_class)
    except ValueError:
        random.seed(123)
        adf3 = random.choices(df_3, k=per_class)
    try:
        random.seed(123)
        adf4 = random.sample(df_4, per_class)
    except ValueError:
        random.seed(123)
        adf4 = random.choices(df_4, k=per_class)
    try:
        random.seed(123)
        adf5 = random.sample(df_5, per_class)
    except ValueError:
        random.seed(123)
        adf5 = random.choices(df_5, k=per_class)
    adf11 = pd.DataFrame(adf1)
    adf12 = pd.DataFrame(adf2)
    adf13 = pd.DataFrame(adf3)
    adf14 = pd.DataFrame(adf4)
    adf15 = pd.DataFrame(adf5)
    df_all = pd.concat([adf11, adf12, adf13, adf14, adf15], ignore_index=True)
    df_all = df_all[[0, 1]]
    df_all.columns = ['text', 'label']
    print(f'{per_class} reviews per class from {link} loaded')
    return df_all


df = load_sampled(amazon_link, 5000)
df.head()
target = df.label
text = df.text_prep

X_train, X_test, y_train, y_test = train_test_split(text, target, test_size=0.3, random_state=123)


tfidf = TfidfVectorizer()
param_grid = [{'vect__ngram_range': [(1, 1)],
               'clf__penalty': ['l1', 'l2'],
               'clf__C': [0.1, 1.0, 10.0],
               'clf__multi_class': ['ovr', 'multinomial']
               }]
lr_tfidf = Pipeline([('vect', tfidf),
                     ('clf', LogisticRegression(random_state=123))])
gs_lr_tfidf = GridSearchCV(lr_tfidf, param_grid, scoring='f1_macro', cv=5, verbose=1, n_jobs=-1)
gs_lr_tfidf.fit(X_train, y_train)
print('LogisticRegression')
print(gs_lr_tfidf.best_params_)
print(gs_lr_tfidf.best_score_)


param_grid = [{'vect__ngram_range': [(1, 1)],
               'clf__alpha': [0.1, 1.0, 10.0],
               'clf__fit_prior': [True, False]
               }]
nb_tfidf = Pipeline([('vect', tfidf),
                     ('clf', MultinomialNB())])
gs_nb_tfidf = GridSearchCV(lr_tfidf, param_grid, scoring='f1_macro', cv=5, verbose=1, n_jobs=-1)
gs_nb_tfidf.fit(X_train, y_train)
print('MultinomialNB')
print(gs_nb_tfidf.best_params_)
print(gs_nb_tfidf.best_score_)


param_grid = [{'vect__ngram_range': [(1, 1)],
               'clf__kernel': ['linear', 'poly', 'rbf', 'sigmoid'],
               'clf__C': [0.1, 1.0, 10.0],
               'clf__gamma': ['auto', 'scale']
               }]
svr_tfidf = Pipeline([('vect', tfidf),
                     ('clf', SVR())])
gs_svr_tfidf = GridSearchCV(lr_tfidf, param_grid, scoring='f1_macro', cv=5, verbose=1, n_jobs=-1)
gs_svr_tfidf.fit(X_train, y_train)
print('SVR')
print(gs_svr_tfidf.best_params_)
print(gs_svr_tfidf.best_score_)


param_grid = [{'vect__ngram_range': [(1, 1)],
               'clf__kernel': ['linear', 'poly', 'rbf', 'sigmoid'],
               'clf__C': [0.1, 1.0, 10.0],
               'clf__gamma': ['auto', 'scale'],
               'clf__decision_function': ['ovo', 'ovr']
               }]
svc_tfidf = Pipeline([('vect', tfidf),
                     ('clf', SVC())])
gs_svc_tfidf = GridSearchCV(lr_tfidf, param_grid, scoring='f1_macro', cv=5, verbose=1, n_jobs=-1)
gs_svc_tfidf.fit(X_train, y_train)
print('SVC')
print(gs_svc_tfidf.best_params_)
print(gs_svc_tfidf.best_score_)


param_grid = [{'vect__ngram_range': [(1, 1)],
               'clf__penalty': ['l1', 'l2'],
               'clf__alpha': [0.1, 0.01, 0.001, 0.0001],
               'clf__max_iter': [500, 1000, 10000]
               }]
sdg_tfidf = Pipeline([('vect', tfidf),
                     ('clf', SGDClassifier(loss='hinge', random_state=123))])
gs_sdg_tfidf = GridSearchCV(lr_tfidf, param_grid, scoring='f1_macro', cv=5, verbose=1, n_jobs=-1)
gs_sdg_tfidf.fit(X_train, y_train)
print('SGDClassifier')
print(gs_sdg_tfidf.best_params_)
print(gs_sdg_tfidf.best_score_)

