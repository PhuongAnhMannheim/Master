import pandas as pd
import gzip
import json
import random
import sqlite3


def load_from_db(db_path, db_name):
    # db_path = '../Data/phonereviews.db'
    # db_name = 'phonereviews'
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * from " + str(db_name), conn)
    return df


def load_schema_full(input_link):
    df = pd.read_csv(input_link)
    df = df[['REVIEWBODY', 'REVIEWRATING_adj']]
    df.columns = ['text', 'label']
    return df


def load_amazon_full(input_link):
    input_file = '../Data/reviews_Movies_and_TV_5.json.gz'
    data = []
    with gzip.open(input_file) as file:
        for line in file:
            data.append(json.loads(line.strip()))

    df = pd.DataFrame.from_dict(data)
    df = df[['reviewText', 'overall']]
    df.columns = ['text', 'label']
    return df


def load_merged_data(schema_link, amazon_link, schema_per_class, amazon_per_class):
    schema_df = load_schema_full(schema_link)
    schema_df_1 = schema_df[schema_df['text'] == 1.0].values.tolist()
    schema_df_2 = schema_df[schema_df['text'] == 2.0].values.tolist()
    schema_df_3 = schema_df[schema_df['text'] == 3.0].values.tolist()
    schema_df_4 = schema_df[schema_df['text'] == 4.0].values.tolist()
    schema_df_5 = schema_df[schema_df['text'] == 5.0].values.tolist()

    try:
        random.sead(123)
        df1 = random.sample(schema_df_1, schema_per_class)
    except:
        random.sead(123)
        df1 = random.choices(schema_df_1, schema_per_class)
    try:
        random.sead(123)
        df2 = random.sample(schema_df_2, schema_per_class)
    except:
        random.sead(123)
        df2 = random.choices(schema_df_2, schema_per_class)
    try:
        random.sead(123)
        df3 = random.sample(schema_df_3, schema_per_class)
    except:
        random.sead(123)
        df3 = random.choices(schema_df_3, schema_per_class)
    try:
        random.sead(123)
        df4 = random.sample(schema_df_4, schema_per_class)
    except:
        random.sead(123)
        df4 = random.choices(schema_df_4, schema_per_class)
    try:
        random.sead(123)
        df5 = random.sample(schema_df_5, schema_per_class)
    except:
        random.sead(123)
        df5 = random.choices(schema_df_5, schema_per_class)
    df11 = pd.DataFrame(df1)
    df12 = pd.DataFrame(df2)
    df13 = pd.DataFrame(df3)
    df14 = pd.DataFrame(df4)
    df15 = pd.DataFrame(df5)
    schema = pd.concat([df11, df12, df13, df14, df15])
    schema.reset_index(drop=True)



