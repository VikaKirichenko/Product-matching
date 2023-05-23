import ast
import pickle
import re
import string

import lightgbm as lgb
import nltk
import numpy
import pandas as pd
import torch
import torch.nn.functional as F
import xgboost as xgb
from pymorphy2 import MorphAnalyzer
from sklearn.metrics import jaccard_score
from sklearn.metrics.pairwise import cosine_similarity
from torch.utils.data import DataLoader
from transformers import BertTokenizer

from config import cols, device, get_data_from_db
from feature_builder import FeatureBuilder, MatchClassifier, PairsDataset

# from utils import preprocess_columns
# from similarities import calculate_sim

# nltk.download('punkt')
# nltk.download('stopwords')

TOK_TOK_TOKENIZER = nltk.tokenize.ToktokTokenizer()
# MORPH = MorphAnalyzer() 
STOPWORDS = nltk.corpus.stopwords.words('russian')
PUNCTS = string.punctuation + '\n\xa0«»\t—...'

BATCH_SIZE = 16
MAX_LEN = 100


model_name = 'bert-base-multilingual-uncased'
tokenizer = BertTokenizer.from_pretrained(model_name)

device = torch.device('cpu')
bert_model = MatchClassifier(2)
# bert_model = bert_model.to(device)
# bert_model.load_state_dict(torch.load('models/best_model_state.bin',map_location=device))


with open('models/best_model_lego.pickle', 'rb') as f:
    best_model = pickle.load(f)
    lego_model = best_model['model']

with open('models/best_model.pickle', 'rb') as f:
    best_model = pickle.load(f)
    smartpones_model = best_model['model']

with open('models/best_model_tv.pickle', 'rb') as f:
    best_model = pickle.load(f)
    tv_model = best_model['model']

with open('models/best_model_books.pickle', 'rb') as f:
    best_model = pickle.load(f)
    books_model = best_model['model']

models = {'smartphones': smartpones_model,
          'tv':tv_model,
          'books':books_model,
          'lego':lego_model}
        

# with open('models/bert_model.pickle', 'rb') as f:
#     bert_model = pickle.load(f)


with open('models/vectorizers_lego.pickle', 'rb') as f:
    lego_vectorizers = pickle.load(f)

with open('models/vectorizers_books.pickle', 'rb') as f:
    books_vectorizers = pickle.load(f)

with open('models/vectorizers_tv.pickle', 'rb') as f:
    tv_vectorizers = pickle.load(f)

with open('models/count_vectorizers.pickle', 'rb') as f:
    smartpones_vectorizers = pickle.load(f)

vectorizers = {'smartphones': smartpones_vectorizers,
          'tv':tv_vectorizers,
          'books':books_vectorizers,
          'lego':lego_vectorizers}

model = ""
count_vectorizers = ""


def damerau_levenshtein_distance(s1, s2):
    d = {}
    lenstr1 = len(s1)
    lenstr2 = len(s2)
    for i in range(-1, lenstr1+1):
        d[(i, -1)] = i+1
    for j in range(-1, lenstr2+1):
        d[(-1, j)] = j+1

    for i in range(lenstr1):
        for j in range(lenstr2):
            if s1[i] == s2[j]:
                cost = 0
            else:
                cost = 1
            d[(i, j)] = min(
                d[(i-1, j)] + 1,  # deletion
                d[(i, j-1)] + 1,  # insertion
                d[(i-1, j-1)] + cost,  # substitution
            )
            if i and j and s1[i] == s2[j-1] and s1[i-1] == s2[j]:
                d[(i, j)] = min(d[(i, j)], d[i-2, j-2] + cost)  # transposition

    return d[lenstr1-1, lenstr2-1]


def calculate_sim(row, feature_combination, category):
    if category != 'smartphones':
        if feature_combination in ['title']:
            return jaccard_score(row[feature_combination+'_wordocc_1'], row[feature_combination+'_wordocc_2'], average='weighted')
        elif feature_combination in ['description', 'specification_values','brand']:
            similarities = cosine_similarity(
                row[feature_combination + '_wordocc_1'],
                row[feature_combination + '_wordocc_2'])
            return similarities[0][0]
        elif feature_combination == 'price':
            return abs(float(row[feature_combination+'_1']) - float(row[feature_combination+'_2']))/max(float(row[feature_combination+'_1']), float(row[feature_combination+'_2']))
    else:
        if feature_combination in ['title']:
            return jaccard_score(row[feature_combination+'_wordocc_1'], row[feature_combination+'_wordocc_2'], average='weighted')
        elif feature_combination == 'brand':
            return damerau_levenshtein_distance(row['brand_1'], row['brand_2'])
        elif feature_combination in ['description', 'specification_values']:
            similarities = cosine_similarity(
                row[feature_combination + '_wordocc_1'],
                row[feature_combination + '_wordocc_2'])
            return similarities[0][0]
        elif feature_combination == 'price':
            return abs(float(row[feature_combination+'_1']) - float(row[feature_combination+'_2']))/max(float(row[feature_combination+'_1']), float(row[feature_combination+'_2']))


    
def get_random_product(category,random_state = None):
    if category == 'smartphones':
        df_all = pd.read_csv('data/all_wb_dns_smartphones.csv')
    elif category == 'books':
        df_all = pd.read_csv('data/all_books.csv')
    elif category == 'tv':
        df_all = pd.read_csv('data/all_tv.csv')
    elif category == 'lego':
        df_all = pd.read_csv('data/all_lego.csv')
    prod = df_all.sample(1, random_state = random_state)
    prod = prod.fillna('')
    product = {
        'id':prod['id'].tolist()[0], 
        'title':prod['title'].tolist()[0],
        'brand':prod['brand'].tolist()[0],
        'description':prod['description'].tolist()[0],
        'specifications':prod['specifications'].tolist()[0],
        'price':prod['price'].tolist()[0],
        'marketplace':prod['marketplace'].tolist()[0],
        'url':prod['url'].tolist()[0],
        'category': category
    }
    return product


def get_products_to_match(category):
    global model
    global count_vectorizers
    model = models[category]
    count_vectorizers = vectorizers[category]
    if category == 'smartphones':
        df_all = pd.read_csv('data/preprocessed_products.csv')
    elif category == 'books':
        df_all = pd.read_csv('data/preprocessed_books.csv')
    elif category == 'tv':
        df_all = pd.read_csv('data/preprocessed_tv.csv')
    elif category == 'lego':
        df_all = pd.read_csv('data/preprocessed_lego.csv')
    return df_all


def make_pairs(products_to_pair,product):

    products_to_pair = products_to_pair.rename(columns={'id':'id_1','marketplace':'markeplace_1',"title": "title_prev_1","title": "title_1", "brand": "brand_1",'price':'price_1','description':'description_1','specification_values':'specification_values_1'})
    products_to_pair['title_prev_2'] = product['title']
    products_to_pair['id_2'] = product['id']
    products_to_pair['title_2'] = [product['title']] * products_to_pair.shape[0]
    products_to_pair['brand_2'] = product['brand']
    products_to_pair['price_2'] = product['price']
    products_to_pair['description_2'] = [product['description']]  * products_to_pair.shape[0]
    try:
        products_to_pair['specification_values_2'] = [product['specification_values']]  * products_to_pair.shape[0]
    except:
        print("don't have specs")
    products_to_pair['marketplace_2'] = product['marketplace']

    return products_to_pair

def process_spec1(spec):
    all_info = {}
    if isinstance(spec,str):
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
    # if spec.isinstance(str):
    #     specs = [tokenize_lemmatize_text(i) for i in ast.literal_eval(spec).values() if i != ""]
    #     spec = ', '.join([i for i in specs if i != ""])
    # else:
    specs = [tokenize_lemmatize_text(i) for i in spec.values() if i != ""]
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
    if product.get('id')!=-1:
        product['specification_values'] = process_spec(product['specifications'])
    else:
        product['specification_values'] = tokenize_lemmatize_text(product['specifications'])

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


def _cut_features(row):
    for i in [1,2]:
        row[f'title_{i}'] = row[f'title_{i}'].lower()
        row[f'description_{i}'] = row[f'description_{i}'].lower()
        row[f'brand_{i}'] = row[f'brand_{i}'].lower()
        row[f'title_{i}'] = ' '.join(row[f'title_{i}'].split(' ')[:20])
        row[f'brand_{i}'] = ' '.join(row[f'brand_{i}'].split(' ')[:5])
        row[f'description_{i}'] = ' '.join(row[f'description_{i}'].split(' ')[:20])
    return row

def get_predictions(model, data_loader):
#   model = model.eval()
  predictions = []
  print('preds start')

  with torch.no_grad():
    print('torch start')
    for d in data_loader:
      print('d start')

      input_ids = d["input_ids"]#.to(device)
      attention_mask = d["attention_mask"]#.to(device)

      outputs = model(
        input_ids=input_ids,
        attention_mask=attention_mask
      )
      _, preds = torch.max(outputs, dim=1)

      predictions.extend(preds)

  predictions = torch.stack(predictions)#.cpu()
  return predictions



def create_data_loader(X,y, tokenizer, max_len, batch_size):
  ds = PairsDataset(
    pairs=numpy.asarray(X),
    labels=numpy.asarray(y),
    tokenizer=tokenizer,
    max_len=max_len
  )

  return DataLoader(
    ds,
    batch_size=batch_size,
    num_workers=4
  )



def predict_matches_bert(product):
    if product['category']=='smartphones':
        products_to_match = get_products_to_match()
    else:
        products_to_match = get_data_from_db('SELECT * FROM products WHERE category = (%s);', (product['category'],))
        products_to_match = pd.DataFrame(products_to_match, columns = cols)

    products_to_match = products_to_match[products_to_match['id']!=product['id']]
    print(products_to_match.shape)

    df_pairs = make_pairs(products_to_match,product)
    df_pairs = df_pairs.fillna("")
    df_pairs = df_pairs.apply(_cut_features, axis=1)
    print(df_pairs.shape)

    # bert tokenizer
    fb = FeatureBuilder(['title','brand','description']) #,'brand','description','specification_values'
    pairs_processed = fb.get_X(df_pairs)
    data_loader = create_data_loader(pairs_processed,[-1]*len(pairs_processed), tokenizer, MAX_LEN, BATCH_SIZE)
    print(len(pairs_processed))

    # bert_model
    preds = get_predictions(bert_model,data_loader)
    df_pairs['match'] = preds
    print(df_pairs.shape)

    return df_pairs[df_pairs['match'] == 1]



def predict_products(product, products_to_match):
    # предобработать все значения и закодировать,
    # сделать пары товаров
    # сделать 5 признаков близости и предсказать match
    # вывести только те товары, с которыми предсказался match
    # products_to_match - dict
    product = preprocess_columns(product)

    products_to_match = products_to_match[products_to_match['id']!=product['id']]

    df_pairs = make_pairs(products_to_match,product)
    df_pairs = df_pairs.fillna("")


    feature_combinations = ['title','brand','description','specification_values']
    for feature_combination in feature_combinations:
        left_matrix = count_vectorizers[feature_combination].transform(df_pairs[feature_combination + '_1'])
        right_matrix = count_vectorizers[feature_combination].transform(df_pairs[feature_combination + '_2'])
        df_pairs[feature_combination + '_wordocc_1'] = [x for x in left_matrix]
        df_pairs[feature_combination + '_wordocc_2'] = [x for x in right_matrix]


    model_df = pd.DataFrame()
    feature_combinations = ['title','brand','description','specification_values','price']
    for feature_combination in feature_combinations:
        print(feature_combination)
        if product['category'] == 'smartphones':
            model_df[feature_combination + ('_sim' if feature_combination not in  ['price','brand'] else '_dist')] = df_pairs.apply(lambda row: calculate_sim(row,feature_combination, product['category']), axis=1)
        else:
            model_df[feature_combination + ('_sim' if feature_combination not in  ['price'] else '_dist')] = df_pairs.apply(lambda row: calculate_sim(row,feature_combination, product['category']), axis=1)
    preds = model.predict(model_df)
    df_pairs['match'] = preds

    return df_pairs[df_pairs['match'] == 1]



