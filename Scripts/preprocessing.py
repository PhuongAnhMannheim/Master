from bs4 import BeautifulSoup
import re
import unidecode
import contractions
import html
import nltk
import pandas as pd
from collections import Counter
from nltk.tokenize.treebank import TreebankWordDetokenizer
import nltk
# nltk.download()
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
# from textblob import TextBlob
from Scripts import profiling as pf


stop = stopwords.words('english')
stops = [e for e in stop if e not in ('but', 'no', 'not', 'very')]
web_dict = {'t2morrow': 'tomorrow',
        'w/': 'with',
        'w/o': 'with no',
        'gr8t': 'great',
        'lol': 'laughing out loud',
        'btw': 'by the way',
        'lmk': 'let me know',
        'tbh': 'to be honest',
        'imho': 'in my humble opinion',
        'irl': 'in real life',
        'tldr': 'too long did not write',
        'asap': 'as soon as possible',
        'thx': 'thanks',
        'aka': 'also known as',
        'b/c': 'because',
        'c&p': 'copy and paste',
        'cu': 'see you',
        'diy': 'do it yourself',
        'eod': 'end of discusion',
        'faq': 'frequently asked questions',
        'hth': 'hope this helps',
        'idk': 'i do not know',
        'imo': 'in my opinion',
        'n/a': 'not available',
        'omg': 'oh my god',
        'wtf': 'what the fuck',
        'wth': 'what the hell',
        'fiy': 'for your information',
        'fb': 'facebook',
        'hifw': 'how i feel when',
        'tfw': 'the feeling when',
        'jk' : 'just kidding',
        'omdb': 'over my dead body',
        'pov': 'point of view',
        'ftw': 'for the win',
        'ynk': 'you never know',
        'srsly': 'seriously',
        'nsfl': 'not save for life',
        'ppl': 'people',
        'luv': 'love',
        'luvin': 'loving',
        'luvin': 'loving',
        'couldnet': 'could not',
        'dont': 'do not'
}


def check_upper(df):
    df['upper'] = df['text_prep'].apply(lambda x: [word for word in x if (word.isupper() and word != 'I')])
    all_upper = []
    count = 0
    for row in df['upper']:
        count += len(row)
        all_upper.extend(row)
    corpus_counts = Counter(all_upper)
    most_common = pd.DataFrame(corpus_counts.most_common(100), columns=['Word', 'Frequency'])
    print('Amount of All Capitals words:', count)
    print(most_common[0:50])


def detokenize(df):
    df['text_prep'] = df.text_prep.apply(lambda x: TreebankWordDetokenizer().detokenize(x))
    return df


def remove_html(df):
    df['text_prep'] = df.text.apply(lambda x: BeautifulSoup(x, "html.parser").get_text())
    print('removed html tags')
    return df


def strip_html(t):
    soup = BeautifulSoup(t, "html.parser")
    return soup.get_text()


def remove_between_square_brackets(df):
    # return re.sub(r'\[[^]]*\]', '', t)
    df['text_prep'] = df.text_prep.apply(lambda x: re.sub(r'\[[^]]*\]', '', x))
    print('removed content between square brackets')
    return df

def remove_between_angle_brackets(df):
    # return re.sub(r'<[^>]+>', '', t)
    df['text_prep'] = df.text_prep.apply(lambda x: re.sub(r'<[^>]+>', '', x))
    print('removed content between angle brackets')
    return df


def remove_accented_chars(df):
    # return unidecode.unidecode(t)
    df['text_prep'] = df.text_prep.apply(lambda x: unidecode.unidecode(x))
    print('removed accented characters')
    return df

def replace_contractions(df):
    # return contractions.fix(t)
    # df['text_prep'] = df.text_prep.apply(lambda x: nltk.word_tokenize(contractions.fix(TreebankWordDetokenizer().detokenize(x))))
    df['text_prep'] = df.text_prep.apply(lambda x: contractions.fix(x))
    print('contractions expansion done')
    return df


def remove_numbers(df):
    # return re.sub(r'([a-zA-Z]*[0-9])|(\S*[0-9]\S)|([0-9])', '', t)
    # df['text_prep'] = df.text_prep.apply(lambda x: re.sub(r'([a-zA-Z]*[0-9])|(\S*[0-9]\S)|([0-9])', '', x))
    df['text_prep'] = df.text_prep.apply(lambda x: nltk.word_tokenize(re.sub(r'[0-9]', ' ', TreebankWordDetokenizer().detokenize(x))))
    pattern = re.compile(r'([a-zA-Z]*[0-9])|(\S*[0-9]\S)|([0-9])')
    df['numerics_mix'] = df['text'].apply(lambda x: len([x for x in nltk.word_tokenize(x) if pattern.findall(x)]))
    print('number removal done')
    pf.get_token_count(df)
    return df


def remove_hyperlinks(df):
    # return re.sub(r'http\S+', '', t)
    df['text_prep'] = df.text_prep.apply(lambda x: re.sub(r'http\S+|www.\S+', '', x))
    print('removed hyperlinks')
    return df


def unescape(df):
    # return html.unescape(t)
    df['text_prep'] = df.text_prep.apply(lambda x: html.unescape(x))
    print('html unescape done')
    return df


def remove_lang_ind(df):
    df['text_prep'] = df.text_prep.apply(lambda x: re.sub(r'(@.{2})\-.{2}|(@.{2})', '', x))
    print('language indicator removal done')
    return df


def remove_punctuation(t):
    return re.sub(r'([^\w!)])\1{1,}|(_{2,})|([^\w\s])', ' ', t)


def remove_whitespaces(df):
    df['text_prep'] = df['text_prep'].apply(lambda x: x.replace('\n', ' '))
    print('white space removal done')
    return df

def to_lowercase(t):
    words = nltk.word_tokenize(t)
    new_words = []
    for word in words:
        new_word = word.lower()
        new_words.append(new_word)
    new_review = TreebankWordDetokenizer().detokenize(new_words)
    return new_review


def to_lower(df):
    print('######## LOWERCASING STATISTICS')
    check_upper(df)
    df['text_prep'] = df['text_prep'].apply(lambda x: [word.lower() for word in x])
    print('lowercasing done')
    return df


def get_pos(df):
    # df['pos'] = df.text_prep.apply(lambda x: nltk.pos_tag(x))
    df['pos'] = nltk.pos_tag_sents(df.text_prep)
    print('pos tagging done')
    return df


def to_token(df):
    df['text_prep'] = df['text_prep'].apply(nltk.word_tokenize)
    print('tokenization done')
    return df


def transform_abbr(df):
    for text_prep in df['text_prep']:
        for i, word in enumerate(text_prep):
            if word in web_dict.keys():
                text_prep[i] = web_dict[word]
    print('abbreviation transformation done')
    return df


def remove_stopwords(df):
    df['text_prep'] = df['text_prep'].apply(lambda x: [word for word in x if word not in stops])
    df['stopwords'] = df['text'].apply(lambda x: len([x for x in nltk.word_tokenize(x) if x in stops]))
    print('stopword removal done')
    pf.get_token_count(df)
    return df


# def lemmatize_with_pos(t):
#     sent = TextBlob(t)
#     tag_dict = {"J": 'a',
#                 "N": 'n',
#                 "V": 'v',
#                 "R": 'r'}
#     words_and_tags = [(w, tag_dict.get(pos[0], 'n')) for w, pos in sent.tags]
#     lemmatized_list = [wd.lemmatize(tag) for wd, tag in words_and_tags]
#     return " ".join(lemmatized_list)


def stem(df):
    # words = nltk.word_tokenize(t)
    # new_words = []
    ps = PorterStemmer()
    # for word in words:
    #     new_words.append(ps.stem(word))
    # new_review = TreebankWordDetokenizer().detokenize(new_words)
    # return new_review
    df['text_prep'] = df['text_prep'].apply(lambda x: [ps.stem(token)for token in x])
    print('port stemming done')
    return df


def remove_punct_and_nonascii(df):
    # t = t.replace('[^a-zA-Z0-9', ' ')
    # return t
    df['text_prep'] = df.text_prep.apply(lambda x: nltk.word_tokenize(re.sub('[^a-zA-Z0-9]', ' ', TreebankWordDetokenizer().detokenize(x))))
    pattern = re.compile(r'[^a-zA-Z0-9]')
    df['punct_non_ascii'] = df['text'].apply(lambda x: len([x for x in nltk.word_tokenize(x) if pattern.findall(x)]))
    print('punctuation and non-ascii removal done')
    pf.get_token_count(df)
    return df

