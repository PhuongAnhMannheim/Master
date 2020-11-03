from Scripts import loading as dl
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.svm import SVC, SVR

amazon_link = '../Data/amazon_phone.pkl'


df = dl.load_sampled(amazon_link, 5000)
target = df.label
text = df.text_prep

X_train, X_test, y_train, y_test = train_test_split(text, target, test_size=0.3, random_state=123)


tfidf = TfidfVectorizer()
param_grid = [{'vect__ngram_range': [(1, 3)],
               'clf__penalty': ['l1', 'l2'],
               'clf__C': [0.1, 1.0, 10.0],
               'clf__solver': ['newton-cg', 'sag', 'saga', 'lbfgs'],
               'clf__multi_class': ['ovr', 'multinomial']
               }]
lr_tfidf = Pipeline([('vect', tfidf),
                     ('clf', LogisticRegression(random_state=123))])
gs_lr_tfidf = GridSearchCV(lr_tfidf, param_grid, scoring='f1_macro', cv=5, verbose=1, n_jobs=-1)
gs_lr_tfidf.fit(X_train, y_train)
print('LogisticRegression')
print(gs_lr_tfidf.best_params_)
print(gs_lr_tfidf.best_score_)


param_grid = [{'vect__ngram_range': [(1, 3)],
               'clf__alpha': [0.1, 1.0, 10.0],
               'clf__fit_prior': [True, False]
               }]
nb_tfidf = Pipeline([('vect', tfidf),
                     ('clf', MultinomialNB())])
gs_nb_tfidf = GridSearchCV(nb_tfidf, param_grid, scoring='f1_macro', cv=5, verbose=1, n_jobs=-1)
gs_nb_tfidf.fit(X_train, y_train)
print('MultinomialNB')
print(gs_nb_tfidf.best_params_)
print(gs_nb_tfidf.best_score_)


param_grid = [{'vect__ngram_range': [(1, 3)],
               'clf__kernel': ['linear', 'poly', 'rbf', 'sigmoid'],
               'clf__C': [0.1, 1.0, 10.0],
               'clf__gamma': ['auto', 'scale']
               }]
svr_tfidf = Pipeline([('vect', tfidf),
                     ('clf', SVR())])
gs_svr_tfidf = GridSearchCV(svr_tfidf, param_grid, scoring='neg_mean_squared_error', cv=5, verbose=1, n_jobs=-1)
gs_svr_tfidf.fit(X_train, y_train)
print('SVR')
print(gs_svr_tfidf.best_params_)
print(gs_svr_tfidf.best_score_)


param_grid = [{'vect__ngram_range': [(1, 3)],
               'clf__kernel': ['linear', 'poly', 'rbf', 'sigmoid'],
               'clf__C': [0.1, 1.0, 10.0],
               'clf__gamma': ['auto', 'scale'],
               'clf__decision_function_shape': ['ovo', 'ovr']
               }]
svc_tfidf = Pipeline([('vect', tfidf),
                     ('clf', SVC())])
gs_svc_tfidf = GridSearchCV(svc_tfidf, param_grid, scoring='f1_macro', cv=5, verbose=1, n_jobs=-1)
gs_svc_tfidf.fit(X_train, y_train)
print('SVC')
print(gs_svc_tfidf.best_params_)
print(gs_svc_tfidf.best_score_)


param_grid = [{'vect__ngram_range': [(1, 3)],
               'clf__penalty': ['l1', 'l2'],
               'clf__alpha': [0.1, 0.01, 0.001, 0.0001],
               'clf__max_iter': [500, 1000, 10000]
               }]
sdg_tfidf = Pipeline([('vect', tfidf),
                     ('clf', SGDClassifier(loss='hinge', random_state=123))])
gs_sdg_tfidf = GridSearchCV(sdg_tfidf, param_grid, scoring='f1_macro', cv=5, verbose=1, n_jobs=-1)
gs_sdg_tfidf.fit(X_train, y_train)
print('SGDClassifier')
print(gs_sdg_tfidf.best_params_)
print(gs_sdg_tfidf.best_score_)

