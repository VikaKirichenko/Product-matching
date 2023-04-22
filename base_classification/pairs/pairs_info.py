import pandas as pd

from config import get_db_connection
from utils import process_spec1


def get_pairs_from_db(table_name):
    conn = get_db_connection()
    cur = conn.cursor()
    query = 'SELECT pair_id, id_1, id_2,match_type FROM '+ table_name +';'
    cur.execute(query)
    products = cur.fetchall()
    cur.close()
    conn.close()

    df = pd.DataFrame(products, columns = ['pair_id','id_1','id_2','match_type'])
    return df

def get_all_pairs(table_names):
    df_all_pairs = pd.DataFrame()
    for table_name in table_names:
        df_pairs = get_pairs_from_db(table_name)
        df_all_pairs = pd.concat([df_all_pairs,df_pairs])
    return df_all_pairs

def concat(row):  
    val = [row['id_1'],row['id_2']]
    val.sort()
    return str(val[0])+" "+str(val[1])
def split_row(row,i):
    return int(row['ids'].split()[i])

def delete_duplicates(df_all_pairs):
    df_all_pairs = df_all_pairs.sort_values(by='match_type', ascending=False)
    df_all_pairs['ids'] = df_all_pairs.apply(lambda row: concat(row), axis=1)
    df_all_pairs['id_1'] = df_all_pairs.apply(lambda row: split_row(row, 0), axis=1)
    df_all_pairs['id_2'] = df_all_pairs.apply(lambda row: split_row(row, 1), axis=1)
    df_all_pairs = df_all_pairs.drop(columns = ['ids'])

    df_all_pairs = df_all_pairs.drop_duplicates(subset = ['id_1','id_2'], keep = 'first')
    df_all_pairs['pair_id'] = range(df_all_pairs.shape[0])
    return df_all_pairs

def delete_unlabeled_data(df_all_pairs):
    df_all_pairs = df_all_pairs[(df_all_pairs['match_type'] != 4) & (df_all_pairs['match_type'] != -1)]
    return df_all_pairs

def get_products_from_db(table_name):
    conn = get_db_connection()
    cur = conn.cursor()
    query = 'SELECT * FROM '+ table_name +';'
    cur.execute(query)
    products = cur.fetchall()
    cur.close()
    conn.close()

    df = pd.DataFrame(products, columns = ['id','brand','title','price','description','specifications','category','marketplace','url','stars','sku'])
    return df

def load_products():
    df = pd.read_csv('data/all_wb_dns_smartphones.csv')
    return df

def get_product_info_by_id(id, df):
    new_df = df[df['id'] == id]
    product = {
        'id': id,
        'title': new_df['title'].tolist()[0],
        'brand': new_df['brand'].tolist()[0],
        'price': new_df['price'].tolist()[0],
        'description': new_df['description'].tolist()[0],
        'specifications': new_df['specifications'].tolist()[0],
    }
    return product

def get_pairs_with_info(df_all_pairs, products):
    pairs = []
    for idx, row in df_all_pairs.iterrows():
        product1 = get_product_info_by_id(row['id_1'], products)
        product2 = get_product_info_by_id(row['id_2'], products)
        pair = {
            'pair_id': row['pair_id'],
            'id_1': row['id_1'],
            'title_1': product1['title'],
            'brand_1': product1['brand'],
            'price_1': product1['price'],
            'description_1': product1['description'],
            'specifications_1': product1['specifications'],
            'id_2': row['id_2'],
            'title_2': product2['title'],
            'brand_2': product2['brand'],
            'price_2': product2['price'],
            'description_2': product2['description'],
            'specifications_2': product2['specifications'],
            'match_type': row['match_type']
        }
        pairs.append(pair)
        
    df_result = pd.DataFrame(pairs)
    return df_result

def main():
    df_all_pairs = get_all_pairs(['pairs','pairs_by_identifier','pairs_by_model'])
    df_all_pairs = delete_duplicates(df_all_pairs)
    df_all_pairs = delete_unlabeled_data(df_all_pairs)

    products = load_products()
    products['specifications'] = products['specifications'].apply(process_spec1)

    df_result = get_pairs_with_info(df_all_pairs, products)

    df_result.to_csv('data/dataset_to_model2.csv',index = False)

if __name__ == '__main__':
    main()









