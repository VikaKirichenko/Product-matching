import pandas as pd
import pickle
from utils import preprocess_columns
from similarities import calculate_sim


def predict_match(model,count_vectorizers,product1, product2):
    # предобработать все значения и закодировать, сделать 5 признаков близости и предсказать match
    product1 = preprocess_columns(product1)
    product2 = preprocess_columns(product2)
    pair_cooc = {
        'price_1':product1['price'],
        'price_2':product2['price'],
        'brand_1':product1['brand'],
        'brand_2':product2['brand'],
    }
    model_dict = {}
    print(product1['title'])
    print(product2['title'])
    feature_combinations = ['title','brand','description','specification_values']
    for feature_combination in feature_combinations:
        left_vector = count_vectorizers[feature_combination].transform([product1[feature_combination]])
        right_vector = count_vectorizers[feature_combination].transform([product2[feature_combination]])
        pair_cooc[feature_combination + '_wordocc_1'] = [x for x in left_vector][0]
        pair_cooc[feature_combination + '_wordocc_2'] = [x for x in right_vector][0]
    feature_combinations = ['title','brand','description','specification_values','price']
    for feature_combination in feature_combinations:
        model_dict[feature_combination + ('_sim' if feature_combination not in  ['price','brand'] else '_dist')] = [calculate_sim(pair_cooc,feature_combination)]
    model_df = pd.DataFrame(model_dict)
    preds = model.predict(model_df)
    return preds[0]

def load_model():
    with open('models/interm_data/best_model.pickle', 'rb') as f:
        best_model = pickle.load(f)
        model = best_model['model']
        return model
    
def load_count_vectorizers():
    with open('models/interm_data/count_vectorizers.pickle', 'rb') as f:
        count_vectorizers = pickle.load(f)
        return count_vectorizers
    
def get_random_product(random_state):
    df_all = pd.read_csv('data/all_wb_dns_smartphones.csv')
    prod = df_all.sample(1, random_state = random_state)
    product = {
        'id':prod['id'].tolist()[0],
        'title':prod['title'].tolist()[0],
        'brand':prod['brand'].tolist()[0],
        'description':prod['description'].tolist()[0],
        'specifications':prod['specifications'].tolist()[0],
        'price':prod['price'].tolist()[0],
        'marketplace':prod['marketplace'].tolist()[0],
    }
    return product


def make_pairs(products_to_pair,product):

    products_to_pair = products_to_pair.rename(columns={'id':'id_1','marketplace':'markeplace_1',"title_prev": "title_prev_1","title": "title_1", "brand": "brand_1",'price':'price_1','description':'description_1','specification_values':'specification_values_1'})
    products_to_pair['title_prev_2'] = product['title_prev']
    products_to_pair['id_2'] = product['id']
    products_to_pair['title_2'] = product['title']
    products_to_pair['brand_2'] = product['brand']
    products_to_pair['price_2'] = product['price']
    products_to_pair['description_2'] = product['description']
    products_to_pair['specification_values_2'] = product['specification_values']
    products_to_pair['marketplace_2'] = product['marketplace']

    return products_to_pair

def get_products_to_match():
    df_all = pd.read_csv('data/all_wb_dns_smartphones.csv')
    return df_all

def predict_matches(model,count_vectorizers,product, products_to_match):
    # предобработать все значения и закодировать,
    # сделать пары товаров
    # сделать 5 признаков близости и предсказать match
    # вывести только те товары, с которыми предсказался match
    # products_to_match - dict
    product = preprocess_columns(product)
    products_to_match = products_to_match.fillna("")
    products_to_match = products_to_match.apply(lambda row: preprocess_columns(row), axis=1)

    df_pairs = make_pairs(products_to_match,product)
    # print(df_pairs.columns)

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
        model_df[feature_combination + ('_sim' if feature_combination not in  ['price','brand'] else '_dist')] = df_pairs.apply(lambda row: calculate_sim(row,feature_combination), axis=1)
    preds = model.predict(model_df)
    df_pairs['match'] = preds

    return df_pairs[df_pairs['match'] == 1] #[['title_1','specification_values_1','title_2','specification_values_2','match']]

def main():
    model = load_model()
    count_vectorizers = load_count_vectorizers()

    product1 = get_random_product(random_state = 1)
    print(product1['id'],product1['title'],product1['marketplace'])
    product2 = get_random_product(random_state = 2)
    print(product2['id'],product2['title'],product2['marketplace'])

    print('not match' if predict_match(model,count_vectorizers,product1,product2) == 0 else 'match')

def main2():
    model = load_model()
    count_vectorizers = load_count_vectorizers()

    product = get_random_product(random_state = 1)
    print(product['id'],product['title'],product['marketplace'])

    products_to_match = get_products_to_match()

    matched_pairs = predict_matches(model,count_vectorizers,product,products_to_match)

    matched_pairs.to_csv('data/matched_pairs.csv',index = False)

if __name__ == '__main__':
    # if want to predict only for one pair
    main()
    # if want to predict matches for random product
    main2()















