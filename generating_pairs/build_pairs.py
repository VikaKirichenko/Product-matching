import pandas as pd
import nltk
import umap
import hdbscan
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
from preprocess_utils import preprocess_columns

nltk.download('stopwords')
stop_words = nltk.corpus.stopwords.words('russian')

word_tokenizer = nltk.WordPunctTokenizer()
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")


def collect_pairs(product, df, pairs):
    '''
    функция для сбора пар для продукта
    product: продукт, с коготрым генерируются пары
    df: DataFrame, в котором хранится информация о товарах для составления пар
    pairs: уже существующие пары
    На выходе получаем уже расширенные сгенерированные пары
    '''
    new_pairs = []
    for idx,row in df.iterrows():
        pair = {
            'id_1': product['id'],
            'title_1': product['title'],
            'id_2': row['id'],
            'title_2':row['title']
        }
        new_pairs.append(pair)
    pairs.extend(new_pairs)
    return pairs

def get_pairs_for_product(product, products, all_pairs):
    '''
    функция для генерации пар для одного товара
    '''
    products = products.drop(products[products['id'] == product['id']].index)
    # необходимо со всеми товарами в кластере посчитать близость по title, price, (title + первые 5 слов description?)
    
    titles = products['title'].tolist()
    # закодировать titles в sentence_embeddings
    main_prod_embeddings = model.encode(product['title'])
    row_prod_embeddings = model.encode(titles)

    prices = products['price'].tolist()

    similarities = cosine_similarity(
        [main_prod_embeddings],
        row_prod_embeddings 
    )
    price_sim = [1 - abs(float(product['price']) - float(price))/max(float(product['price']),float(price)) for price in prices]

    products['price_sim'] = price_sim
    products['title_sim'] = similarities[0]
    
    # отсортировать сначала по title_sim, потом по price_sim
    products = products.sort_values(by=['title_sim', 'price_sim'], ascending=False)
    # print(products[:10])
    pairs = []
    # get top 2
    top_prod = products.head(2)
    pairs = collect_pairs(product, top_prod, pairs)

    # get random from middle  1 (in 50% of all)
    start = int(products.shape[0] * 0.25)
    end =  int(products.shape[0] * 0.75)
    middle_random_prod = products[start:end].sample(n=1)
    pairs = collect_pairs(product, middle_random_prod, pairs)

    # get lowest 2
    lowest_prod = products.tail(2)
    pairs = collect_pairs(product, lowest_prod, pairs)

    # get random 2
    random_prod = products.sample(n=2)
    pairs = collect_pairs(product, random_prod, pairs)

    df_pairs = pd.DataFrame(pairs)
    # print(df_pairs)

    all_pairs = pd.concat([all_pairs, df_pairs])
    all_pairs = all_pairs.drop_duplicates()
    return all_pairs

def cluster_products(df_all):
    '''
    функция для кластеризации продуктов
    '''
    titles = df_all['title'].tolist()
    
    sentence_embeddings = model.encode(titles)
    # уменьшение размерности
    umap_embeddings = umap.UMAP(n_neighbors=15, 
                            n_components=5, 
                            metric='cosine').fit_transform(sentence_embeddings)

    # кластеризация
    cluster = hdbscan.HDBSCAN(min_cluster_size=15,min_samples=1,
                          metric='euclidean',                      
                          cluster_selection_method='eom').fit(umap_embeddings)
    # сохранение топиков
    df_all['cluster_id'] = cluster.labels_
    docs_per_topic = df_all.groupby(['cluster_id'], as_index = False).agg({'title': ' '.join})
    docs_df = df_all[['id','cluster_id','title','brand','price']]

    return docs_df


def get_random_products_per_cluster(products):
    '''
    функция для получения списка рандомных товаров внутри кластера
    '''
    n = 2 if products.shape[0] < 30 else 3 if products.shape[0] < 40 else 4 if products.shape[0] < 50 else 5
    # генерация рандомных товаров внутри кластера
    random_products = []
    # подсчет уникальных названий товаров
    n_unique_numbers = len(products['title'].unique())
    # если сгенирированный n > чем уникальных значений, то урезаем, иначе будет очень много похожих пар
    if n > n_unique_numbers:
        n = n_unique_numbers
    # print(n,'random products')
    count = 0
    # до тех пор пока не сгенерировалось нужное кол-во товаров, генерируем
    while len(random_products) < n:
        count += 1
        # выбираем рандомный товар
        product = products.sample(n = 1)
        product = {
            'id':product['id'].tolist()[0],
            'title':product['title'].tolist()[0],
            'brand':product['brand'].tolist()[0],
            'price':product['price'].tolist()[0]
        }
        # добавляем первый товар
        if len(random_products) == 0:
            random_products.append(product)
            products = products.drop(products[products['id'] == product['id']].index)
            continue
        # смотрим на близость по названию в случае, если уже есть добавленные товары
        sim = 0
        prev_prod_embeddings = model.encode(random_products[-1]['title'])
        prod_embeddings = model.encode(product['title'])
        sim = cosine_similarity([prev_prod_embeddings] ,[prod_embeddings])
        # исходя из того, какая итерация, treshold, для того, чтобы даже в кластере, где практчески только одинаковые названия, нашлись близкие
        treshold = 0.95 if count < 10 else 0.97
        if sim >= treshold:
            sim = 1
            continue

        random_products.append(product)
        # убираем из products добавленный товар, чтобы не попался еще раз
        products = products.drop(products[products['id'] == product['id']].index)

    return random_products


def get_pairs(df):
    '''
    функция для генерации пар
    '''
    docs_df = cluster_products(df)
    n_cat = len(df['cluster_id'].unique())
    print(n_cat)
    all_pairs = pd.DataFrame(columns = ['id_1','title_1','id_2','title_2'])
    for i in range(n_cat):
        print(f'category {i}')
        products = docs_df[docs_df['cluster_id'] == i]
        products_copy = products.copy()
        if products.shape[0] < 6 or products.shape[0] > 150:
            continue
        
        random_products = get_random_products_per_cluster(products)

        for product in tqdm(random_products):
            all_pairs = get_pairs_for_product(product, products, all_pairs)

    all_pairs = all_pairs.drop_duplicates(subset=['id_1','title_1','title_2'])
    all_pairs.to_csv('data/all_pairs_smartphones2.csv')
    return all_pairs


if __name__ == '__main__':
    df_all = pd.read_csv('data/all_wb_dns_smartphones.csv')
    df_all = df_all.drop(columns = ['Unnamed: 0'])
    df_all = preprocess_columns(df_all)
    df_all = df_all.drop_duplicates(subset=['title','brand','price','description'])
    all_pairs = get_pairs(df_all)
    