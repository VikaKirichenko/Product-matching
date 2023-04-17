import re
import ast
import pandas as pd


def get_models(df):
    '''
    функция для получения моделей для всех товаров, если модели у товара нет, то пустая строка
    '''
    models = []
    for ids, row in df.iterrows():
        row['specifications'] = ast.literal_eval(row['specifications'])
        if 'модель' in row['specifications']:
            models.append(row['specifications']['модель'])
        else:
            models.append("")
    return models

def generate_pairs(df, column_name, sequence):
    df = df.copy()
    pairs = []
    for elem in sequence:
        pos_prods = df[df[column_name] == elem].reset_index()

        idxs = pos_prods['id'].tolist()
        titles = pos_prods['title'].tolist()
        for i, prod in pos_prods.iterrows():
            for idx, title in zip(idxs[i+1:], titles[1:]):
                pair = {'id_1':prod['id'], 'title_1': prod['title'],
                        'id_2': idx, 'title_2':title, column_name:elem}
                pairs.append(pair)

    print(len(pairs))
    return pairs

def generate_pairs_by_model(df):
    '''
    функция для генераци пар по модели
    '''
    # group by model
    groups_model = df.groupby(['model'], as_index = False).count()
    # select non empty model name and groups where only 2 products (for reducing number of pairs)
    groups_model = groups_model[(groups_model['sku']==2) & (groups_model['model'] != '')].sort_values(by=['sku'], ascending=False)#['identifier'].tolist()[0]

    models = groups_model['model'].tolist()
    pairs = generate_pairs(df,'model',models)

    df_pairs_model = pd.DataFrame(pairs)
    df_pairs_model['pair_id'] = range(df_pairs_model.shape[0])
    df_pairs_model['match_type'] = -1

    df_pairs_model.to_csv('data/pairs_by_model.csv',index = False)

    return df_pairs_model

def get_prods_with_info(df):
    '''
    функция для получения дополнительной информации о товаре
    '''
    prods = []
    for ids, row in df.iterrows():
        prod = {}
        row['specifications'] = ast.literal_eval(row['specifications'])
        keys = re.findall(r'(диагональ экрана|емкость аккумулятора|объем встроенной памяти \(гб\)|объем оперативной памяти \(гб\))',','.join(row['specifications'].keys()))

        if len(keys) == 4:
            prod['id'] = row['id']
            prod['model'] = row['model']
            prod['diag'] = re.search(r'\d+\.\d+',row['specifications'].get('диагональ экрана').replace(',',".").split(' ')[0].replace("''",""))
            if not prod['diag']:
                prod['diag'] = ""
            else:
                prod['diag'] = prod['diag'].group()
            prod['akk'] = row['specifications'].get('емкость аккумулятора').split(";")[0].split(' ')[0]
            prod['bim'] = row['specifications'].get('объем встроенной памяти (гб)').replace('гб',"").replace('gb',"").strip().split(";")[0]
            prod['ram'] = row['specifications'].get('объем оперативной памяти (гб)').replace('гб',"").replace('gb',"").strip().split(";")[0]
            prods.append(prod)
    df = pd.DataFrame(prods)
    return df

def generate_pairs_by_model_bim_ram(df):
    df = get_prods_with_info(df)
    agg_func_max_min = {'id': ['min', 'max', 'count']}
    groups_ident = df.groupby(['model','diag','akk','bim','ram'], as_index = False, group_keys=True).agg(agg_func_max_min)
    groups_ident = groups_ident[(groups_ident['diag']!="") & (groups_ident['model'] != '')& (groups_ident['id']['count'] == 2)]

    pairs = groups_ident['id'][['min','max']]
    pairs = pairs.rename(columns={"max": "id_1", "min": "id_2"})
    pairs['match_type'] = -1
    pairs['pair_id'] = range(pairs.shape[0])

    pairs.to_csv('data/pairs_by_model_diag_akk_bim_ram.csv',index = False)

    return pairs

if __name__ == '__main__':
    df_all = pd.read_csv('data/all_wb_dns_smartphones_reduce_spec.csv')
    df_all['model'] = get_models(df_all)
    pairs_by_model = generate_pairs_by_model(df_all)

    pairs_by_model_bim_ram = generate_pairs_by_model_bim_ram(df_all)



