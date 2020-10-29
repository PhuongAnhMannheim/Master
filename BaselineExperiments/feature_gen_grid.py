
import pandas as pd
import random
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.svm import SVC, SVR
from sklearn.pipeline import Pipeline

amazon_link = '../Data/amazon_phone.pkl'

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
    df_all = df_all[[2, 1]]
    df_all.columns = ['text_prep', 'label']
    print(f'{per_class} reviews per class from {link} loaded')
    return df_all


df = load_sampled(amazon_link, 5000)
target = df.label
text = df.text_prep

X_train, X_test, y_train, y_test = train_test_split(text, target, test_size=0.3, random_state=None)

tfidf = TfidfVectorizer()

param_grid = [{
    'vect__max_df': [0.5, 0.75, 0.8, 0.9, 1.0],
    'vect__min_df': [1, 2, 3, 5, 10, 20],
    'vect__binary': [True, False]
}, {
    'vect': [CountVectorizer(),],
    'vect__max_df': [0.5, 0.75, 0.8, 0.9, 1.0],
    'vect__min_df': [1, 2, 3, 5, 10],

}]
cv = StratifiedKFold(n_splits = 5, shuffle=False, random_state=123)
print('######## RUN SVC')
svc_features = Pipeline([('vect', tfidf),
                        ('clf', SVC(C=1.0, decision_function_shape='ovo', gamma='auto', kernel='linear', random_state=123))])
gs_svc_features = GridSearchCV(svc_features, param_grid, scoring='f1_macro', cv=cv, verbose=3, n_jobs=-1)
gs_svc_features.fit(X_train, y_train)
print('best parameters')
print(gs_svc_features.best_params_)
print('best score')
print(gs_svc_features.best_score_)
print(pd.concat([pd.DataFrame(gs_svc_features.cv_results_["params"]),pd.DataFrame(gs_svc_features.cv_results_["mean_test_score"], columns=["f1_macro"])],axis=1))


print('######## RUN LOGISTIC REGRESSION')
lr_features = Pipeline([('vect', tfidf),
                        ('clf', LogisticRegression(C=10.0, multi_class='multinomial', penalty='l2', solver='saga', random_state=123))])

gs_lr_features = GridSearchCV(lr_features, param_grid, scoring='f1_macro', cv=cv, verbose=3, n_jobs=-1)
gs_lr_features.fit(X_train, y_train)
print('best parameters')
print(gs_lr_features.best_params_)
print('best score')
print(gs_lr_features.best_score_)
print(pd.concat([pd.DataFrame(gs_lr_features.cv_results_["params"]),pd.DataFrame(gs_lr_features.cv_results_["mean_test_score"], columns=["f1_macro"])],axis=1))


print('######## RUN SGDClassifier')
sgd_features = Pipeline([('vect', tfidf),
                        ('clf', SGDClassifier(alpha=0.0001, max_iter=500, penalty='l2', random_state=123, loss='hinge'))])

gs_sgd_features = GridSearchCV(sgd_features, param_grid, scoring='f1_macro', cv=cv, verbose=3, n_jobs=-1)
gs_sgd_features.fit(X_train, y_train)
print('best parameters')
print(gs_sgd_features.best_params_)
print('best score')
print(gs_sgd_features.best_score_)
print(pd.concat([pd.DataFrame(gs_sgd_features.cv_results_["params"]),pd.DataFrame(gs_sgd_features.cv_results_["mean_test_score"], columns=["f1_macro"])],axis=1))


print('######## RUN Multinomial Bayes with prior')
nb_features = Pipeline([('vect', tfidf),
                        ('clf', MultinomialNB(alpha=1.0, fit_prior=False))])

gs_nb_features = GridSearchCV(nb_features, param_grid, scoring='f1_macro', cv=cv, verbose=3, n_jobs=-1)
gs_nb_features.fit(X_train, y_train)
print('best parameters')
print(gs_nb_features.best_params_)
print('best score')
print(gs_nb_features.best_score_)
print(pd.concat([pd.DataFrame(gs_nb_features.cv_results_["params"]),pd.DataFrame(gs_nb_features.cv_results_["mean_test_score"], columns=["f1_macro"])],axis=1))


print('######## RUN Multinomial Bayes without prior')
nb_features = Pipeline([('vect', tfidf),
                        ('clf', MultinomialNB(alpha=1.0, fit_prior=False))])

gs_nb_features = GridSearchCV(nb_features, param_grid, scoring='f1_macro', cv=cv, verbose=3, n_jobs=-1)
gs_nb_features.fit(X_train, y_train)
print('best parameters')
print(gs_nb_features.best_params_)
print('best score')
print(gs_nb_features.best_score_)
print(pd.concat([pd.DataFrame(gs_nb_features.cv_results_["params"]),pd.DataFrame(gs_nb_features.cv_results_["mean_test_score"], columns=["f1_macro"])],axis=1))


print('######## RUN Multinomial Bayes without prior')
nb_features = Pipeline([('vect', tfidf),
                        ('clf', MultinomialNB(alpha=1.0, fit_prior=False))])

gs_nb_features = GridSearchCV(nb_features, param_grid, scoring='f1_macro', cv=cv, verbose=3, n_jobs=-1)
gs_nb_features.fit(X_train, y_train)
print('best parameters')
print(gs_nb_features.best_params_)
print('best score')
print(gs_nb_features.best_score_)
print(pd.concat([pd.DataFrame(gs_nb_features.cv_results_["params"]),pd.DataFrame(gs_nb_features.cv_results_["mean_test_score"], columns=["f1_macro"])],axis=1))


print('######## RUN SVR')
nb_features = Pipeline([('vect', tfidf),
                        ('clf', SVR(C=10.0, gamma='scale', kernel='rbf', ))])

gs_nb_features = GridSearchCV(nb_features, param_grid, scoring='neg_mean_squared_error', cv=cv, verbose=3, n_jobs=-1)
gs_nb_features.fit(X_train, y_train)
print('best parameters')
print(gs_nb_features.best_params_)
print('best score')
print(gs_nb_features.best_score_)
print(pd.concat([pd.DataFrame(gs_nb_features.cv_results_["params"]),pd.DataFrame(gs_nb_features.cv_results_["mean_test_score"], columns=["f1_macro"])],axis=1))

