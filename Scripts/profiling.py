import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go


def create_word_count(df):
    df['word_count'] = df.text.apply(lambda x: len(str(x).split(" ")))
    return df


def get_missing_text(df):
    return df[df.text.isnull()]


def get_missing_label(df):
    return df[df.label.isnull()]


def get_review_count(df):
    print("Amount of reviews: ", len(df))


def get_descr(df):
    print(df.describe(include='all'))


def get_longest_review(df):
    longest_t = df[df['word_count'] == max(df['word_count'])]
    print('The longest review text in our sample has {} words.'.format(max(df['word_count'])))
    print('Longest review text:' + '\n')
    print(longest_t.text, longest_t.label)


def get_shortest_review(df):
    shortest_t = df[df['word_count'] == min(df['word_count'])]
    print('The shortest review text in our sample has {} words.'.format(min(df['word_count'])))
    print('Review text with the shortest length of {} word appearing {} times.'.format(min(df['word_count']), len(shortest_t)))
    print(shortest_t.text, shortest_t.label)


def get_word_length_dist(df, dataname, log):
    plt.rcParams['figure.facecolor'] = 'white'
    plt.hist(df['word_count'].value_counts().sort_index(), range=(0, 6000), bins=100, log=log)
    plt.xlabel('Text length')
    plt.ylabel('Distribution')
    plt.title(f'Text lengths in words ({dataname})')
    df['word_count'].describe()


def show_word_length_dist(df, filename, dataname, log):
    # e.g. amazon_cell_textlength_raw_logarithmic, Amazon Movies & TV, true

    plt.rcParams['figure.facecolor'] = 'white'
    plt.hist(df['word_count'].value_counts().sort_index(), range=(0, 6000), bins=100, log=log)
    plt.xlabel('Text length')
    plt.ylabel('Distribution')
    plt.title(f'Text lengths in words ({dataname})')
    plt.savefig(f'../Figures/{filename}.png')
    df['word_count'].describe()


def show_rating_dist(df, filename, title):
    # e.g. amazon_cell_class_dist_raw
    print(df.label.value_counts())
    plt.rcParams['figure.facecolor'] = 'white'
    plt.xlabel('Class')
    plt.ylabel('Amount')
    plt.title(f'Rating distribution ({title})')
    plt.hist(df.label, bins=np.arange(0.5, 6), rwidth=0.5)
    plt.savefig(f'../Figures/{filename}.png')


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
        margin=dict(l=30, r=20, b=150, t=90)
    )
    fig = go.Figure(data=dplot, layout=layout)
    fig.show()


# def show_duplicate_texts(df):
#     print(df[df.text.duplicates()])
#     print(len)