# все id
# вроде 90 страниц
# https://api.rivegauche.ru/rg/v1/newRG/products/search?fields=FULL&currentPage=0&pageSize=24&categoryCode=Perfumery_Woman&tag=4564927438288954

# конкретный товар
# https://api.rivegauche.ru/rg/v1/newRG/products/{id}

from tqdm import tqdm

import requests
from utils import write_to_csv

all_ids = []
for i in tqdm(range(0, 92)):
    # print(i)
    url = f'https://api.rivegauche.ru/rg/v1/newRG/products/search?fields=FULL&currentPage={i}&pageSize=24&categoryCode=Perfumery_Woman&tag=4564927438288954'
    response = requests.get(url)
    # print(response.json())
    data = response.json()
    try:
        results = data['results']
        ids = [res['code'].replace('base_','') for res in results]
        all_ids.extend(ids)
    except Exception as e:
        print(i)
        print(e)
print(len(all_ids))

for id in tqdm(all_ids):
    url = f'https://api.rivegauche.ru/rg/v1/newRG/products/{id}'
    response = requests.get(url)
    # print(response.json())
    data = response.json()

    try:
        product = {
            'id_on_store': id,
            'title': data['name'],
            'brand': data['brand']['name'],
            'price': data['price']['value'],
            'description': data['description'],
            'specifications': {feat['name']:feat['value'] for feat in data['features']},
            'category': 'parfumes',
            'marketplace':'rivegauche',
            'url': 'https://rivegauche.ru/' + data['url']
        }
    except Exception as e:
        print(id)
        print(e)
    write_to_csv(product,'data/riv_parfumes.csv')
    
    

