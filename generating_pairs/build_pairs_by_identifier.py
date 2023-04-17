import pandas as pd
import ast
import re
from build_pairs_by_model import generate_pairs

def get_identifiers(df):
    identifiers = []
    for ids, row in df_all.iterrows():
        row['specifications'] = ast.literal_eval(row['specifications'])
        if 'код производителя' in row['specifications']:
            identifiers.append(re.sub(r'[\[\]]',"",row['specifications']['код производителя']))
        else:
            identifiers.append("")
    return identifiers


def generate_pairs_by_identifier(df):
    groups_ident = df.groupby(['identifier'], as_index = False).count()
    groups_ident = groups_ident[(groups_ident['sku']>1) & (groups_ident['identifier'] != '')].sort_values(by=['sku'], ascending=False)#['identifier'].tolist()[0]

    identifiers = groups_ident['identifier'].tolist()

    pairs = generate_pairs(df,'identifier',identifiers)

    df_pairs_ident = pd.DataFrame(pairs)
    df_pairs_ident['pair_id'] = range(df_pairs_ident.shape[0])
    df_pairs_ident['match_type'] = -1

    df_pairs_ident.to_csv('data/pairs_by_identifier.csv',index = False)

    return df_pairs_ident


if __name__ == '__main__':
    df_all = pd.read_csv('data/all_wb_dns_smartphones_reduce_spec.csv')
    df_all['identifier'] = get_identifiers(df_all)

    pairs_by_identifier = generate_pairs_by_identifier(df_all)
    