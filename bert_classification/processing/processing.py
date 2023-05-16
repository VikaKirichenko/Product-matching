import ast
import re
import string

import nltk
from feature_builder import FeatureBuilder
from pymorphy2 import MorphAnalyzer

nltk.download('punkt')
nltk.download('stopwords')

WORD_PUNCT_TOKENIZER = nltk.tokenize.WordPunctTokenizer()
TOK_TOK_TOKENIZER = nltk.tokenize.ToktokTokenizer()
MORPH = MorphAnalyzer() 
STOPWORDS = nltk.corpus.stopwords.words('russian')
PUNCTS = string.punctuation + '\n\xa0«»\t—...'

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
    text_lemmatized = [MORPH.parse(x)[0].normal_form for x in tokens]  # apply lemmatization to each word in a text
    text = ' '.join(text_lemmatized)  # unite all lemmatized words into a new text
    return text

def tokenize_lemmatize_text(text, tokenizer=TOK_TOK_TOKENIZER):
    '''to working with df use applymap for whole column df.applymap(tokenize_lemmatize_text)'''
    tokens = tokenize_text(text, tokenizer)
    text = lemmatize_text(tokens)
    return text

def preprocess_columns(df_result, reduce_desc = False, spec_keys = False):
    df_result = df_result.fillna("")
    for i in range(1,3):
        df_result[f'title_{i}'] = df_result[f'title_{i}'].apply(tokenize_lemmatize_text)
        df_result[f'brand_{i}'] = df_result[f'brand_{i}'].apply(tokenize_lemmatize_text)
        df_result[f'description_{i}'] = df_result[f'description_{i}'].apply(tokenize_lemmatize_text)
        df_result[f'title_{i}'].mask(df_result[f'title_{i}'] == '', df_result[f'description_{i}'].apply(lambda x: " ".join(x.split()[:5])), inplace=True)
        if reduce_desc:
            df_result[f'description_{i}'] = df_result[f'description_{i}'].apply(lambda x: ' '.join(x.split()[:5]))
        if spec_keys:
            df_result[f'specification_values_{i}'] = df_result[f'specifications_{i}'].apply(lambda x:', '.join([key+" "+ tokenize_lemmatize_text(val) for key, val in ast.literal_eval(str(x)).items() if val!=""]))
        else:
            df_result[f'specification_values_{i}'] = df_result[f'specifications_{i}'].apply(lambda x: [tokenize_lemmatize_text(i) for i in ast.literal_eval(str(x)).values() if i != ""])
            df_result[f'specification_values_{i}'] = df_result[f'specification_values_{i}'].apply(lambda x: ', '.join([i for i in x if i != ""]))

    return df_result

def _cut_features(row):
    for i in [1,2]:
        row[f'title_{i}'] = row[f'title_{i}'].lower()
        row[f'description_{i}'] = row[f'description_{i}'].lower()
        row[f'brand_{i}'] = row[f'brand_{i}'].lower()
        row[f'title_{i}'] = ' '.join(row[f'title_{i}'].split(' ')[:20])
        row[f'brand_{i}'] = ' '.join(row[f'brand_{i}'].split(' ')[:5])
        row[f'description_{i}'] = ' '.join(row[f'description_{i}'].split(' ')[:20])
        # row[f'specification_values_{i}'] = ' '.join(row[f'specification_values_{i}'].split(' ')[:100])
    return row

def simple_processing(df,cols = ['title','brand','description']):
    df = df.fillna('')
    df = df[df['match_type']!=4]
    df['match_type'] = df['match_type'].apply(lambda x: 0 if x == 3 or x == 2 else 1)
    dataset = df.apply(_cut_features, axis=1)
    fb = FeatureBuilder(cols) 
    X = fb.get_X(dataset)
    y = fb.get_y(dataset)

    return X, y



