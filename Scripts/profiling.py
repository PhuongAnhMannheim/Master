import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
import pandas as pd
import re
from nltk.corpus import stopwords
from Scripts import preprocessing as prep
from collections import Counter
from wordcloud import WordCloud
from urllib.parse import urlparse


def check_empty_text(df):
    print('Before deleting empty review texts: ', len(df))
    df = df[df['reviewText'] != '']
    print('After deleting empty review texts: ', len(df))
    return df


def checkmisrat(row):
    result = has_numbers(row['REVIEWRATING']) and has_numbers(row['BESTRATING']) and has_numbers(row['WORSTRATING'])
    return result


def create_word_count(df):
    try:
        df['word_count'] = df.text.apply(lambda x: len(str(x).split(" ")))
    except:
        df['word_count'] = df.REVIEWBODY.apply(lambda x: len(str(x).split(" ")))
    return df


def get_descr(df):
    print('######## DESCRIPTION')
    print(df.describe(include='all'))


def get_duplicates(df):
    df_dup = df[df.duplicated(subset=['text'], keep='last')]
    if 'label' in df:
        df_dup2 = df[df.duplicated(subset=['text', 'label'], keep='last')]
    else:
        df_dup2 = df[df.duplicated(subset=['text', 'REVIEWRATING'], keep='last')]
    print("Duplicate text:", len(df_dup))
    print("Duplicate text: {:.2%}".format(len(df_dup) / len(df)))
    print("Duplicate text and label:", len(df_dup2))
    print("Duplicate text and label from reviews without missing information: {:.2%}".format(len(df_dup2) / len(df)))


def get_longest_review(df):
    longest_t = df[df['word_count'] == max(df['word_count'])]
    print('The longest review text in our sample has {} words.'.format(max(df['word_count'])))
    print('Longest review text:' + '\n')
    print(longest_t.text, longest_t.label)


def get_missing_label(df):
    total = len(df)
    if 'label' in df:
        print('Missing rating information', len(df[df.label.isnull()]))
        print('Missing rating information as percentage: {:.2%}'.format(len(df[df.label.isnull()]) / total))
    else:
        print('Missing rating information', len(df[df.REVIEWRATING.isnull() | df.BESTRATING.isnull() | df.WORSTRATING.isnull()]))
        print('Missing rating information as percentage: {:.2%}'.format(len(df[df.REVIEWRATING.isnull() | df.BESTRATING.isnull() | df.WORSTRATING.isnull()]) / total))


def get_missing_label_implicit(df):
    total = len(df)
    df = df[df.text.notnull() & (df.text != '')
            & df.REVIEWRATING.notnull()
            & df.BESTRATING.notnull()
            & df.WORSTRATING.notnull()]
    df['mis_rat'] = df.apply(checkmisrat, axis=1)
    print('Implicitly missing rating data', len(df[df['mis_rat'] == False]))
    print('Implicitly missing rating data as percentage: {:.2%} '.format((len(df[df['mis_rat'] == False])) / total))
    return df


def get_missing_text(df):
    total = len(df)
    print('Missing/Empty review text:', len(df[df.text.isnull() | (df.text == '')]))
    print('Missing review text as percentage: {:.2%} '.format(len(df[df.text.isnull() | (df.text == '')]) / total))


def get_mostcommon(df, filename):
    corpus = pd.Series(' '.join(df['text']).split())
    corpus_counts = Counter(corpus)
    mostcommon = pd.DataFrame(corpus_counts.most_common(100), columns=['Word', 'Frequency'])
    print('######## Most Frequent Word Stems')
    print(mostcommon[0:50])
    most_common = mostcommon.set_index('Word').to_dict()['Frequency']  # dictionary
    wordcloud = WordCloud(max_words=100, width=800, height=800, background_color='white',
                          random_state=42).generate_from_frequencies(most_common)
    plt.figure(figsize=(8, 8), dpi=80)
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()
    plt.savefig(f"../Figures/wordcloud_{filename}.png", bbox_inches='tight', dpi=300)
    return mostcommon


def get_netloc(row):
    try:
        return urlparse(row['URL']).netloc
    except:
        print("expection: ", row['URL'])
    else:
        print("sad", row['URL'])


def get_num_perc(df):
    pattern = re.compile(r'([a-zA-Z]*[0-9])|(\S*[0-9]\S)|([0-9])')
    df['numerics_mix'] = df['text'].apply(lambda x: len([x for x in x.split() if pattern.findall(x)]))
    print('######## Numerics:')
    print('The number of numerics in development sample: {}'.format(sum(df.numerics_mix)))
    print('Numerics as percentage of all words in the corpus: {:.2%} '.format(sum(df.numerics_mix) / sum(df.word_count)))


def get_prep_summary(df, total):
    print('PREPROCESSING SUMMARY')
    print('The number of numerics: {}'.format(sum(df.numerics_mix)))
    print('Numerics as percentage: {:.2%} '.format(sum(df.numerics_mix) / total))
    print('The number of punctuation and non-ascii: {}'.format(sum(df.punct_non_ascii)))
    print('Punctuation and non-ascii as percentage: {:.2%} '.format(sum(df.punct_non_ascii) / total))
    print('The number of stop words: {}'.format(sum(df.stopwords)))
    print('Stop words as percentage: {:.2%} '.format(sum(df.stopwords)/total))


def get_review_count(df):
    print("######## Total: ")
    print("Amount of reviews: ", len(df))


def get_source_info(df):
    df['netloc'] = df.apply(get_netloc, axis=1)
    print('Total netloc distribution')
    print(df['netloc'].value_counts())
    print('extracted netloc distribution')
    print(df[~df.NODE.str.contains('_:znode')]['netloc'].value_counts())
    print('scraped netloc distribution')
    print(df[df.NODE.str.contains('_:znode')]['netloc'].value_counts())
    return df


def get_shortest_review(df):
    shortest_t = df[df['word_count'] == min(df['word_count'])]
    print('The shortest review text in our sample has {} words.'.format(min(df['word_count'])))
    print('Review text with the shortest length of {} word appearing {} times.'.format(min(df['word_count']), len(shortest_t)))
    print(shortest_t.text, shortest_t.label)


def get_token_count(df):
    df['token_count'] = df.text_prep.apply(lambda x: len(x))
    token_count = sum(df.token_count)
    print('Token Count: ', token_count)


def get_total_token_count(df):
    df['token_count'] = df.text_prep.apply(lambda x: len(x))
    return sum(df.token_count)


def get_word_length_dist(df, dataname, log):
    plt.rcParams['figure.facecolor'] = 'white'
    plt.hist(df['word_count'].value_counts().sort_index(), range=(0, 6000), bins=100, log=log)
    plt.xlabel('Text length')
    plt.ylabel('Distribution')
    plt.title(f'Text lengths in words ({dataname})')
    df['word_count'].describe()


def get_unique_wordstem_count(df):
    df['text'] = [prep.stem(line) for line in df['text']]
    corpus = pd.Series(' '.join(df['text']).split())
    print("Amount of unique word stems for all classes: ", len(corpus.unique()))  # 75030


def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)


def show_lang_dist(df, filename, title, eng):
    fig = plt.figure()
    ax = fig.add_axes([0,0,1,1])
    if eng == 0:
        x = df[df.LANGUAGE != 'en']['LANGUAGE'].value_counts().index
        y = df[df.LANGUAGE != 'en']['LANGUAGE'].value_counts()
    else:
        x = df['LANGUAGE'].value_counts().index
        y = df['LANGUAGE'].value_counts()
    ax.bar(x, y)
    plt.xlabel('Language')
    plt.ylabel('Number of reviews')
    plt.title(f'{title}')
    plt.rcParams.update({"figure.facecolor": "white"})
    fig.savefig(f"../Figures/{filename}.png", bbox_inches='tight', dpi=300)
    plt.show()


def show_rating_dist(df, filename, title):
    # e.g. amazon_cell_class_dist_raw
    print('######### Ratings')
    print('Description of Ratings:')
    print(df.label.value_counts())
    print(df.label.value_counts(normalize=True))
    plt.rcParams['figure.facecolor'] = 'white'
    plt.xlabel('Class')
    plt.ylabel('Amount')
    plt.title(f'Rating distribution ({title})')
    # plt.tight_layout()
    plt.hist(df.label, bins=np.arange(0.5, 6.0), rwidth=0.5)
    plt.savefig(f'../Figures/{filename}.png', dpi=300)
    plt.show()


def show_word_length_dist(df, filename, dataname, log):
    # e.g. amazon_cell_textlength_raw_logarithmic, Amazon Movies & TV, true

    plt.rcParams['figure.facecolor'] = 'white'
    plt.hist(df['word_count'].value_counts().sort_index(), range=(0, 6000), bins=100, log=log)
    plt.xlabel('Text length')
    plt.ylabel('Distribution')
    plt.title(f'Text lengths in words ({dataname})')
    plt.savefig(f'../Figures/{filename}.png', dpi=300)
    print('Description of word length:')
    print(df['word_count'].describe())
    plt.show()


def show_word_length_per_label(df):
    dplot = []
    categories = [1.0, 2.0, 3.0, 4.0, 5.0]
    for i in range(5):
        trace = go.Box(
            y=df[(df['label'] == categories[i])]['word_count'],
            name=categories[i]
        )
        dplot.append(trace)

    layout = go.Layout(
        height=900,
        width=1200,
        title="Review Text - Length Distribution by Label",
        margin=dict(l=50, r=20, b=150, t=90),
        font=dict(
            size = 18
        )
    )
    fig = go.Figure(data=dplot, layout=layout)
    fig.show()


def show_amounts_unique_tokens(df):
    corpus = pd.Series(' '.join(df['reviewText']).split())
    corpus_1 = pd.Series(' '.join(df[df['overall'] == 1.0]['reviewText']).split())
    corpus_2 = pd.Series(' '.join(df[df['overall'] == 2.0]['reviewText']).split())
    corpus_3 = pd.Series(' '.join(df[df['overall'] == 3.0]['reviewText']).split())
    corpus_4 = pd.Series(' '.join(df[df['overall'] == 4.0]['reviewText']).split())
    corpus_5 = pd.Series(' '.join(df[df['overall'] == 5.0]['reviewText']).split())
    print("Amount of unique tokens for all classes: ", len(corpus.unique()))  # 75030
    print("Amount of unique tokens for class 1: ", len(corpus_1.unique()))  # 17881
    print("Amount of unique tokens for class 2: ", len(corpus_2.unique()))  # 18153
    print("Amount of unique tokens for class 3: ", len(corpus_3.unique()))  # 24682
    print("Amount of unique tokens for class 4: ", len(corpus_4.unique()))  # 35431
    print("Amount of unique tokens for class 5: ", len(corpus_5.unique()))  # 52175


def get_stop_perc(df):
    stop = stopwords.words('english')
    stop = [e for e in stop if e not in ('but', 'no', 'not')]
    df['stopwords'] = df['text'].apply(lambda x: len([x for x in x.split() if x in stop]))
    print('######## Stop words:')
    print('The number of stop words in development sample: {}'.format(sum(df.stopwords)))
    print('Stop words as percentage of all words in the corpus: {:.2%} '.format(sum(df.stopwords)/sum(df.word_count)))


