import sys
sys.path.append("..")
import pandas as pd
from Scripts import profiling as pf, cleaning as cl

df = pd.read_pickle('../Data/amazon_movie.pkl')
print('Data loaded')
print('######## Tail: ')
print(df.tail())

print('######## GENERAL INFORMATION')
pf.get_review_count(df)


print('######## COMPLETION CHECK')
print('Missing Text')
pf.get_missing_text(df)
print('Missing Label')
pf.get_missing_label(df)
print('Before deleting empty review texts: ', len(df))
df = df[df['text'] != '']
print('After deleting empty review texts: ', len(df))


print('######## DUPLICATION CHECK')
df = cl.remove_duplicates(df)
df = cl.remove_dup_text(df)


print('######## WORD COUNT')
pf.create_word_count(df)
pf.get_shortest_review(df)
pf.get_longest_review(df)

print('# Less than 10 words: ')
print(df[df.word_count<10]['label'].value_counts())
print('More than 1000 words: ')
print(df[df.word_count>1000]['label'].value_counts())

pf.show_word_length_dist(df, 'amazon_movie_pkl_textlength_raw_logarithmic', 'Amazon Movies and TV', True)


print('######## RATING DISTRIBUTION')
pf.show_rating_dist(df, 'amazon_movie_pkl_rating_dist', 'Amazon Movies and TV')
