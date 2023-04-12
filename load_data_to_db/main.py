import pandas as pd
from sqlalchemy import create_engine
import psycopg2
import sys

param_dic = {
    "host"      : "localhost",
    "database"  : "products_db",
    "user"      : "postgres",
    "password"  : "12345"
}


def connect(params_dic):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params_dic)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        sys.exit(1) 
    print("Connection successful")
    return conn


connect = "postgresql+psycopg2://%s:%s@%s:5432/%s" % (
    param_dic['user'],
    param_dic['password'],
    param_dic['host'],
    param_dic['database']
)
def to_alchemy(df,table_name):
    """
    Using a dummy table to test this call library
    """
    engine = create_engine(connect)
    df.to_sql(
        table_name, 
        con=engine, 
        index=False, 
        if_exists='replace'
    )
    print("to_sql() done (sqlalchemy)")



# df = pd.read_csv("all_wb_dns_smartphones.csv")
# df = df.drop(columns = ['Unnamed: 0'])
# df['category'] = ['smartphones'] * df.shape[0]
# df = df[['id','brand','title','price','description','specifications','category', 'marketplace','url', 'stars','sku']]
# print('done')
# to_alchemy(df, 'products')


df_pairs = pd.read_csv("all_pairs_smartphones2.csv")
df_pairs = df_pairs.drop(columns = ['Unnamed: 0'])
df_pairs['pair_id'] = range(len(df_pairs))
df_pairs = df_pairs[['pair_id','id_1','title_1','id_2','title_2']]
df_pairs['match_type'] = ['-1'] * df_pairs.shape[0]
df_pairs = df_pairs.drop_duplicates(subset = ['id_1','title_1','title_2'])
df_pairs['pair_id'] = range(len(df_pairs))
print('done')
to_alchemy(df_pairs, 'pairs')



# conn = connect(param_dic)