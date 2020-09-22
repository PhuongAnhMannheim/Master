from bs4 import BeautifulSoup
import re
import unidecode
import contractions
import html
import nltk
from nltk.tokenize.treebank import TreebankWordDetokenizer
from nltk.corpus import stopwords
from textblob import TextBlob

stops = stopwords.words('english')
stops = [e for e in stops if e not in ('but', 'no', 'not')]


def strip_html(t):
    soup = BeautifulSoup(t, "html.parser")
    return soup.get_text()


def remove_between_square_brackets(t):
    return re.sub(r'\[[^]]*\]', '', t)


def remove_between_angle_brackets(t):
    return re.sub(r'<[^>]+>', '', t)


def remove_accented_chars(t):
    return unidecode.unidecode(t)


def replace_contractions(t):
    return contractions.fix(t)


def remove_numbers(t):
    return re.sub(r'([a-zA-Z]*[0-9])|(\S*[0-9]\S)|([0-9])', '', t)


def remove_hyperlinks(t):
    return re.sub(r'http\S+', '', t)


def unescape(t):
    return html.unescape(t)


def remove_punctuation(t):
    return re.sub(r'([^\w!)])\1{1,}|(_{2,})|([^\w\s])', ' ', t)


def remove_extra_whitespaces(t):
    return re.sub(r'[\s]{2,}', ' ', t)


# experiment what is better 1. lowercase all 2. only lowercase if all caps
def to_lowercase(t):
    words = nltk.word_tokenize(t)
    new_words = []
    # for word in words:
    #     if word.isupper():
    #         new_words.append(word)
    #     else:
    #         new_word = word.lower()
    #         new_words.append(new_word)
    for word in words:
        new_word = word.lower()
        new_words.append(new_word)
    new_review = TreebankWordDetokenizer().detokenize(new_words)
    return new_review


def remove_stopwords(t):
    words = nltk.word_tokenize(t)
    new_words = []
    for word in words:
        if word not in stops:
            new_words.append(word)
    new_review = TreebankWordDetokenizer().detokenize(new_words)
    return new_review


def lemmatize_with_pos(sentence):
    sent = TextBlob(sentence)
    tag_dict = {"J": 'a',
                "N": 'n',
                "V": 'v',
                "R": 'r'}
    words_and_tags = [(w, tag_dict.get(pos[0], 'n')) for w, pos in sent.tags]
    lemmatized_list = [wd.lemmatize(tag) for wd, tag in words_and_tags]
    return " ".join(lemmatized_list)


def preprocess_reviews(reviews):
    # De-noise
    # - remove unnecessary space and <br>, HTML tags
    reviews = [strip_html(line) for line in reviews]
    reviews = [remove_between_square_brackets(line) for line in reviews]
    reviews = [remove_between_angle_brackets(line) for line in reviews]

    # remove weblinks
    reviews = [remove_hyperlinks(line) for line in reviews]

    # - spacing after .,-
    # reviews = [re.sub(r'(?<=[.,-])(?=[^\s])', r' ', line) for line in reviews]

    # - standardising of lettering, e.g. cafe instead of café
    reviews = [unidecode.unidecode(line) for line in reviews]
    reviews = [unescape(line) for line in reviews]

    # Expand contractions
    reviews = [replace_contractions(line) for line in reviews]

    # remove numbers and connected number units,
    reviews = [remove_numbers(line) for line in reviews]

    # remove multiple special characters expect !
    reviews = [remove_punctuation(line) for line in reviews]

    # lowercase, except all caps
    reviews = [to_lowercase(line) for line in reviews]

    reviews = [lemmatize_with_pos(line) for line in reviews]

    # stopword removal
    reviews = [remove_stopwords(line) for line in reviews]

    # remove multiple white spaces
    reviews = [remove_extra_whitespaces(line) for line in reviews]
    return reviews
