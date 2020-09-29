# not working
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

# def remove_empty_label(df):
#
