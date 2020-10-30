import pandas as pd
import random
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC, SVR
from sklearn.pipeline import Pipeline
from sklearn.feature_selection import SelectKBest, chi2, f_classif, f_regression, mutual_info_classif, mutual_info_regression


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

kbest = SelectKBest(f_classif)
param_grid = [{
    'kbest__k': [100, 200, 300, 400, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000]
}, {
    'kbest': [SelectKBest(f_regression)],
    'kbest__k': [100, 200, 300, 400, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000]
}, {
    'kbest': [SelectKBest(chi2)],
    'kbest__k': [100, 200, 300, 400, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000]
}, {
    'kbest': [SelectKBest(mutual_info_classif)],
    'kbest__k': [100, 200, 300, 400, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000]
}, {
    'kbest': [SelectKBest(mutual_info_regression)],
    'kbest__k': [100, 200, 300, 400, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000]
    }
]

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=123)


print('######## RUN SVC')
svc_pipeline = Pipeline([('vect',  TfidfVectorizer(binary=True, max_df=0.75, min_df=1, ngram_range=(1, 3))),
                         ('kbest', kbest),
                        ('clf', SVC(C=1.0, decision_function_shape='ovo', gamma='auto', kernel='linear', random_state=123))])
gs_svc_pipeline = GridSearchCV(svc_pipeline, param_grid, scoring='f1_macro', cv=cv, verbose=3, n_jobs=-1)
gs_svc_pipeline.fit(X_train, y_train)
print('best parameters')
print(gs_svc_pipeline.best_params_)
print('best score')
print(gs_svc_pipeline.best_score_)
print(pd.concat([pd.DataFrame(gs_svc_pipeline.cv_results_["params"]),pd.DataFrame(gs_svc_pipeline.cv_results_["mean_test_score"], columns=["f1_macro"])],axis=1))

