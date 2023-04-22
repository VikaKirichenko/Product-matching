import ast
import re
import string

import nltk
from pymorphy2 import MorphAnalyzer

nltk.download('punkt')
nltk.download('stopwords')

TOK_TOK_TOKENIZER = nltk.tokenize.ToktokTokenizer()
# MORPH = MorphAnalyzer() 
STOPWORDS = nltk.corpus.stopwords.words('russian')
PUNCTS = string.punctuation + '\n\xa0«»\t—...'

def process_spec1(spec):
    all_info = {}
    spec = ast.literal_eval(spec)
    for block in spec:
        for item in spec[block]:
            if len(item) > 1:
                key = item[0].lower()
                val = item[1].lower()
                all_info[key] = val

    myKeys = list(all_info.keys())
    myKeys.sort()
    sorted_dict = {i: all_info[i] for i in myKeys}

    return sorted_dict

def process_spec2(spec):
    specs = [tokenize_lemmatize_text(i) for i in ast.literal_eval(spec).values() if i != ""]
    spec = ', '.join([i for i in specs if i != ""])
    return spec

def process_spec(spec):
    spec = process_spec1(spec)
    return process_spec2(spec)

def preprocess_columns(product):
    product['title_prev'] = product['title']
    product['title'] = tokenize_lemmatize_text(product['title'])
    product['brand'] = tokenize_lemmatize_text(product['brand'])
    product['description'] = tokenize_lemmatize_text(product['description'])
    product['specification_values'] = process_spec(product['specifications'])

    if product['title'] == "":
        product['title'] = " ".join(product['description'].split()[:5])
    return product


def remove_noise(tokens):
    new_tokens = [word.replace(',','.') for word in tokens if
            (word not in string.punctuation and
             word not in STOPWORDS)]
    new_tokens = [re.sub(r'[.\(\)]','',word) if word[-1] in ".()" else word for word in new_tokens]
    return new_tokens

def tokenize_text(text, tokenizer):
    text_lower = text.lower().replace("/"," ").replace("+"," ").replace('смартфон',"") # .replace('гб','gb').strip()  # convert words in a text to lower case
    text_lower = re.sub(r'(гб\w*)',"gb",text_lower).strip()
    
    text_lower = re.sub(r'(\d+)(\s?)(gb)','\g<1>\g<3> ',text_lower)
    text_lower = re.sub(r'\s+'," ",text_lower)
    tokens = tokenizer.tokenize(text_lower)  # splits the text into tokens (words)

    # remove punct and stop words from tokens
    return remove_noise(tokens)

def lemmatize_text(tokens):
    MORPH = MorphAnalyzer() 
    tokens = [MORPH.parse(x)[0].normal_form for x in tokens]  # apply lemmatization to each word in a text
    text = ' '.join(tokens)  # unite all lemmatized words into a new text
    return text

def tokenize_lemmatize_text(text, tokenizer=TOK_TOK_TOKENIZER):
    '''to working with df use applymap for whole column df.applymap(tokenize_lemmatize_text)'''
    tokens = tokenize_text(text, tokenizer)
    text = lemmatize_text(tokens)
    return text

