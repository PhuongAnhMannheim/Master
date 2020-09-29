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
    data = []
    with gzip.open(input_link) as file:
        for line in file:
            data.append(json.loads(line.strip()))

    df = pd.DataFrame.from_dict(data)
    df = df[['reviewText', 'overall']]
    df.columns = ['text', 'label']
    return df


def load_merged_data(schema_link, amazon_link, schema_per_class, amazon_per_class):
    schema_df = pd.read_pickle(schema_link)
    schema_df_1 = schema_df[schema_df['label'] == 1.0].values.tolist()
    schema_df_2 = schema_df[schema_df['label'] == 2.0].values.tolist()
    schema_df_3 = schema_df[schema_df['label'] == 3.0].values.tolist()
    schema_df_4 = schema_df[schema_df['label'] == 4.0].values.tolist()
    schema_df_5 = schema_df[schema_df['label'] == 5.0].values.tolist()

    try:
        random.seed(123)
        df1 = random.sample(schema_df_1, schema_per_class)
    except ValueError:
        random.seed(123)
        df1 = random.choices(schema_df_1, k=schema_per_class)
    try:
        random.seed(123)
        df2 = random.sample(schema_df_2, schema_per_class)
    except ValueError:
        random.seed(123)
        df2 = random.choices(schema_df_2, k=schema_per_class)
    try:
        random.seed(123)
        df3 = random.sample(schema_df_3, schema_per_class)
    except ValueError:
        random.seed(123)
        df3 = random.choices(schema_df_3, k=schema_per_class)
    try:
        random.seed(123)
        df4 = random.sample(schema_df_4, schema_per_class)
    except ValueError:
        random.seed(123)
        df4 = random.choices(schema_df_4, k=schema_per_class)
    try:
        random.seed(123)
        df5 = random.sample(schema_df_5, schema_per_class)
    except ValueError:
        random.seed(123)
        df5 = random.choices(schema_df_5, k=schema_per_class)
    df11 = pd.DataFrame(df1)
    df12 = pd.DataFrame(df2)
    df13 = pd.DataFrame(df3)
    df14 = pd.DataFrame(df4)
    df15 = pd.DataFrame(df5)
    schema = pd.concat([df11, df12, df13, df14, df15])
    ama_df = pd.read_pickle(amazon_link)
    ama_df_1 = ama_df[ama_df['label'] == 1.0].values.tolist()
    ama_df_2 = ama_df[ama_df['label'] == 2.0].values.tolist()
    ama_df_3 = ama_df[ama_df['label'] == 3.0].values.tolist()
    ama_df_4 = ama_df[ama_df['label'] == 4.0].values.tolist()
    ama_df_5 = ama_df[ama_df['label'] == 5.0].values.tolist()

    try:
        random.seed(123)
        adf1 = random.sample(ama_df_1, amazon_per_class)
    except ValueError:
        random.seed(123)
        adf1 = random.choices(ama_df_1, k=amazon_per_class)
    try:
        random.seed(123)
        adf2 = random.sample(ama_df_2, amazon_per_class)
    except ValueError:
        random.seed(123)
        adf2 = random.choices(ama_df_2, k=amazon_per_class)
    try:
        random.seed(123)
        adf3 = random.sample(ama_df_3, amazon_per_class)
    except ValueError:
        random.seed(123)
        adf3 = random.choices(ama_df_3, k=amazon_per_class)
    try:
        random.seed(123)
        adf4 = random.sample(ama_df_4, amazon_per_class)
    except ValueError:
        random.seed(123)
        adf4 = random.choices(ama_df_4, k=amazon_per_class)
    try:
        random.seed(123)
        adf5 = random.sample(ama_df_5, amazon_per_class)
    except ValueError:
        random.seed(123)
        adf5 = random.choices(ama_df_5, k=amazon_per_class)
    adf11 = pd.DataFrame(adf1)
    adf12 = pd.DataFrame(adf2)
    adf13 = pd.DataFrame(adf3)
    adf14 = pd.DataFrame(adf4)
    adf15 = pd.DataFrame(adf5)
    amazon = pd.concat([adf11, adf12, adf13, adf14, adf15])
    df_all = pd.concat([schema, amazon], ignore_index=True)
    df_all = df_all[[0,1]]
    df_all.columns = ['text', 'label']
    return df_all


def load_sampled_amazon(amazon_link, amazon_per_class):
    ama_df = pd.read_pickle(amazon_link)
    ama_df_1 = ama_df[ama_df['label'] == 1.0].values.tolist()
    ama_df_2 = ama_df[ama_df['label'] == 2.0].values.tolist()
    ama_df_3 = ama_df[ama_df['label'] == 3.0].values.tolist()
    ama_df_4 = ama_df[ama_df['label'] == 4.0].values.tolist()
    ama_df_5 = ama_df[ama_df['label'] == 5.0].values.tolist()

    try:
        random.seed(123)
        adf1 = random.sample(ama_df_1, amazon_per_class)
    except ValueError:
        random.seed(123)
        adf1 = random.choices(ama_df_1, k=amazon_per_class)
    try:
        random.seed(123)
        adf2 = random.sample(ama_df_2, amazon_per_class)
    except ValueError:
        random.seed(123)
        adf2 = random.choices(ama_df_2, k=amazon_per_class)
    try:
        random.seed(123)
        adf3 = random.sample(ama_df_3, amazon_per_class)
    except ValueError:
        random.seed(123)
        adf3 = random.choices(ama_df_3, k=amazon_per_class)
    try:
        random.seed(123)
        adf4 = random.sample(ama_df_4, amazon_per_class)
    except ValueError:
        random.seed(123)
        adf4 = random.choices(ama_df_4, k=amazon_per_class)
    try:
        random.seed(123)
        adf5 = random.sample(ama_df_5, amazon_per_class)
    except ValueError:
        random.seed(123)
        adf5 = random.choices(ama_df_5, k=amazon_per_class)
    adf11 = pd.DataFrame(adf1)
    adf12 = pd.DataFrame(adf2)
    adf13 = pd.DataFrame(adf3)
    adf14 = pd.DataFrame(adf4)
    adf15 = pd.DataFrame(adf5)
    amazon = pd.concat([adf11, adf12, adf13, adf14, adf15], ignore_index=True)
    df_all = amazon[[0, 1]]
    df_all.columns = ['text', 'label']
    return df_all


