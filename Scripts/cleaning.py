from langdetect import detect


def detect_lang(row):
    try:
        return detect(row['text'])
    except:
        print("exception:", row['text'])
    else:
        print("sad:", row['text'])


def drop_duplicates(df):
    if 'label' in df:
        df = df.drop_duplicates(subset=['text','label'], keep='last')
    else:
        df = df.drop_duplicates(subset=['text', 'REVIEWRATING'], keep='last')
    df = df.drop_duplicates(subset=['text'], keep='last')
    print("After removing duplicate entries and texts: ", len(df))
    return df


def proceed_data_completion(df):
    df.dropna()
    if 'label' in df:
        df = df[df.text.notnull() & (df.text != '') & df.label.notnull()]
    else:
        df = df[df.text.notnull() & (df.text != '')
                & df.REVIEWRATING.notnull()
                & df.BESTRATING.notnull()
                & df.WORSTRATING.notnull()]
        df = df[df['mis_rat'] == True]
    print("After removing implictly missing rating information: ", len(df))
    return df


def remove_duplicates(df):
    print('Before deleting duplicate entries: ', len(df))
    df.drop_duplicates(inplace=False)
    print('After deleting duplicate entries: ', len(df))
    return df


def remove_dup_text(df):
    print('Before deleting duplicate review texts: ', len(df))
    df = df.drop_duplicates(subset=['text'])
    print('After deleting duplicate review texts: ', len(df))
    return df


def remove_empty_text(df):
    print('Before deleting empty review texts: ', len(df))
    df = df[df['reviewText'] != '']
    print('After deleting empty review texts: ', len(df))
    return df


def remove_non_english(df):
    df['LANGUAGE'] = df.apply(detect_lang, axis=1)
    print(df['LANGUAGE'].value_counts())
    df = df[df['LANGUAGE'] == "en"]
    print("After removing non-english text:", len(df))
    return df