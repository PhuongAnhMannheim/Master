import sys
sys.path.append("..")
from Scripts import loading as dl, profiling as pf, cleaning as cl, preprocessing as prep


input_link = '../Data/reviews_Movies_and_TV_5.json.gz'
df = dl.load_amazon_full(input_link)


print('######## FIRST GENERAL INSIGHT')
print(df.head())
pf.get_review_count(df)
pf.get_descr(df)


print('######## DATA COMPLETENESS')
pf.get_missing_text(df)
pf.get_missing_label(df)
df = cl.proceed_data_completion(df)


print('######## DUPLICATE DETECTION')
pf.get_duplicates(df)
df = cl.drop_duplicates(df)


print('######## LINGUISTIC AFFILIATION')
df = cl.remove_non_english(df)
# pf.show_lang_dist(df, 'amazon_movie_lang_non_eng_dist', 'non-English Language Distribution (Amazon Movies & TV)', 0)
# pf.show_lang_dist(df, 'amazon_movie_lang_all_dist', 'Language Distribution (Amazon Movies & TV)', 1)


print('######## OTHER HEURISTICS')
df = df[~df.text.str.contains(r'^&#((15|16|20)[0-9]{2,3});*')]
print('After removing from other cleaning heuristics: ', len(df))


print('######## PREPROCESSING')
print('######## Web Data Specific')
df = prep.remove_html(df)
df = prep.remove_hyperlinks(df)
df = prep.remove_between_square_brackets(df)
df = prep.remove_between_angle_brackets(df)
df = prep.unescape(df)
df = prep.remove_whitespaces(df)
df = prep.remove_lang_ind(df)

print('######## Text Harmonization')
df = prep.replace_contractions(df)
df = prep.remove_accented_chars(df)
df = prep.to_token(df)
total_token_count = pf.get_total_token_count(df)
print(total_token_count)
df = prep.transform_abbr(df)
df = prep.remove_numbers(df)
df = prep.remove_punct_and_nonascii(df)
df = prep.to_lower(df)
df = prep.remove_stopwords(df)
df = prep.get_pos(df)

print('######## Text Canonicalization')
df = prep.stem(df)

pf.get_prep_summary(df, total_token_count)

df = prep.detokenize(df)

print('######## DATA COMPLETION AFTER PREPROCESSING')
total_prep = len(df)
df_empty = df[df.text_prep=='']
print("Empty preprocessed text:", len(df_empty))
print("Duplicate preprocessed text: {:.2%}".format(len(df_empty) / total_prep))
df = df[df.text_prep!='']
print("After removing empty preprocessed texts: ", len(df))

print('######## DEDUPLICATION AFTER PREPROCESSING')
df_dup = df[df.duplicated(subset=['text_prep'], keep='last')]
print("Duplicate preprocessed text:", len(df_dup))
print("Duplicate preprocessed text: {:.2%}".format(len(df_dup) / total_prep))
df = df.drop_duplicates(subset=['text_prep'], keep='last')
print("After removing duplicate preprocessed texts: ", len(df))


# print('######### LAST CHECK')
# print(df.head())
# print(df.describe(include='all'))


print('######## STORING')
df = df[['text', 'label', 'text_prep', 'token_count', 'upper', 'pos']]
df.columns = ['text', 'label', 'text_prep', 'token_count', 'upper', 'pos']
df.to_pickle('../Data/amazon_movie1.pkl')
print('to pickle done')


