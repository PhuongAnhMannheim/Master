import pandas as pd
import random
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
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
    df_all = df_all[[0, 1]]
    df_all.columns = ['text', 'label']
    print(f'{per_class} reviews per class from {link} loaded')
    return df_all


df = load_sampled(amazon_link, 5000)
df.head()
target = df.label
text = df.text_prep

X_train, X_test, y_train, y_test = train_test_split(text, target, test_size=0.3, random_state=None)

count = CountVectorizer()
param_grid = [{
    'vect__max_df': [0.5, 0.75, 0.8, 0.9, 1.0],
    'vect__min_df': [1, 2, 3, 5, 10],
    'vect__binary': [True, False]
}, {
    'vect': [TfidfVectorizer()],
    'vect__max_df': [0.5, 0.75, 0.8, 0.9, 1.0],
    'vect__min_df': [1, 2, 3, 5, 10],

}]

ml_features = Pipeline([('vect', count),
                        ('clf', ???)])

gs_ml_features = GridSearchCV(ml_features, param_grid, scoring='f1_macro',
                              cv=5, verbose=1, n_jobs=-1)
gs_ml_features.fit(X_train, y_train)
print('all results:')
print(gs_ml_features.cv_results_)
print('best parameters')
print(gs_ml_features.best_params_)
print('best score')
print(gs_ml_features.best_score_)


