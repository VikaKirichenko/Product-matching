import multiprocessing

import requests
from tqdm import tqdm

from utils import write_to_csv

categories_info = [
    {   'name': 'books',
        'url': 'https://catalog.wb.ru/catalog/books4/catalog?appType=1&cat=9127&curr=rub&dest=-1257786&fsupplier=-100;8969;9001;10465;10700;29634;33753&page=1&regions=80,64,38,4,115,83,33,68,70,69,30,86,75,40,1,66,48,110,31,22,71,114&sort=popular&spp=0',
        'n_pages': 34},
    {   'name':'parfumes',
        'url': 'https://catalog.wb.ru/catalog/beauty3/catalog?appType=1&cat=9001&curr=rub&dest=-1257786&fsupplier=-100;23266&page=1&regions=80,64,38,4,115,83,33,68,70,69,30,86,75,40,1,66,48,110,31,22,71,114&sort=popular&spp=0',
        'n_pages':12},
    {   'name': 'TV',
        'url': 'https://catalog.wb.ru/catalog/electronic13/catalog?appType=1&curr=rub&dest=-1257786&page=1&regions=80,64,38,4,115,83,33,68,70,69,30,86,75,40,1,66,48,110,31,22,71,114&sort=popular&spp=0&subject=2819',
        'n_pages':21},
    {   'name': 'LEGO',
        'url': 'https://catalog.wb.ru/catalog/toys2/catalog?appType=1&cat=128594&curr=rub&dest=-1257786&page=1&regions=80,64,38,4,115,83,33,68,70,69,30,86,75,40,1,66,48,110,31,22,71,114&sort=popular&spp=0',
        'n_pages':100}
]

def get_all_products_ids(category_url, n_pages):
    all_ids = []
    for i in range(1, n_pages + 1):
        url = category_url.replace('page=1',f'page={i}')
        # url = f'https://catalog.wb.ru/catalog/books4/catalog?appType=1&cat=9127&curr=rub&dest=-1257786&fsupplier=-100;8969;9001;10465;10700;29634;33753&page={i}&regions=80,64,38,4,115,83,33,68,70,69,30,86,75,40,1,66,48,110,31,22,71,114&sort=popular&spp=0'
        response  = requests.get(url)

        data = response.json()

        prods_info = data['data']['products']

        ids = [prod_info['id'] for prod_info in prods_info]

        all_ids.extend(ids)
    return all_ids

def get_card(id,category_name):
    basket_id = 1
    url = f'https://basket-01.wb.ru/vol{str(id)[:-5]}/part{str(id)[:-3]}/{id}/info/ru/card.json'
    if category_name == "TV":
        basket_id = 10
        url = f'https://basket-10.wb.ru/vol{str(id)[:-5]}/part{str(id)[:-3]}/{id}/info/ru/card.json'
    if category_name == "LEGO":
        basket_id = 11
        url = f'https://basket-11.wb.ru/vol{str(id)[:-5]}/part{str(id)[:-3]}/{id}/info/ru/card.json'

    response  = requests.get(url)
    status = 'empty'

    while status != 'ok':
        try:
            data = response.json()
            status = 'ok'
        except:
            if category_name == "TV":
                basket_id = basket_id - 1
            else:
                basket_id = basket_id + 1
            if basket_id > 15:
                print(id,'failed')
                return
            res = basket_id if len(str(basket_id)) > 1 else '0'+str(basket_id)
            # print(res)
            url = f'https://basket-{res}.wb.ru/vol{str(id)[:-5]}/part{str(id)[:-3]}/{id}/info/ru/card.json'
            response  = requests.get(url)
    return data

def get_all_products_info(all_ids, category_name):
    all_products_info = []

    for id in tqdm(all_ids):
        # print(id)
        # id  = '11996463'
        data = get_card(id,category_name)
        if not data:
            continue

        price_url = f'https://card.wb.ru/cards/detail?appType=1&curr=rub&dest=-1257786&regions=80,64,38,4,115,83,33,68,70,69,30,86,75,40,1,66,48,110,31,22,71,114&spp=0&nm={id}'
        price_response  = requests.get(price_url)

        price_data = price_response.json()  

        try:
            if category_name == 'books':
                auth = [i['value'] for i in data['options'] if i['name'] == 'Автор']
                brand = auth[0].split(';')[0] if len(auth)>0 else ""
            else:
                brand = data['selling']['brand_name']
        except Exception as e:
            print(e)
            brand = ""

        try:
            product = {'title': data.get('imt_name') if data.get('imt_name') else "",
                    'brand': brand,
                    'price': price_data['data']['products'][0]['salePriceU']/100,
                    'description': data.get('description') if data.get('description') else "",
                    'specifications': { opt['name']: opt['value'] for opt in data['options']},
                    'category': category_name,
                    'marketplace':'wb',
                    'url': f'https://www.wildberries.ru/catalog/{id}/detail.aspx',
                    'id_on_store': id
                    }
        except Exception as e:
            print(id)
            print(e)
            
        all_products_info.append(product)

        write_to_csv(product,'data/'+category_name + '_data.csv')
    print('data saved')
    return all_products_info

def main():
    for cat in categories_info:
        print(cat['name'])
        if cat['name'] in ['books','TV','parfumes']:
            continue
        print(cat['name'])
        all_ids = get_all_products_ids(cat['url'],cat['n_pages'])
        all_ids = list(set(all_ids))
        print(len(all_ids))
        # with open('all_ids.pickle', 'wb') as f:
        #     pickle.dump(all_ids, f)

        # with open('all_ids.pickle', 'rb') as f:
        #     all_ids = pickle.load(f)

        get_all_products_info(all_ids,cat['name'])


def main2():
    start = 0
    end = start + 3400
    for cat in categories_info:
        print(cat['name'])
        if cat['name'] in ['books','TV','parfumes']:
            continue

        all_ids = get_all_products_ids(cat['url'],cat['n_pages'])
        all_ids = list(set(all_ids))
        print(len(all_ids))
        
        processes = []
        for i in range(3):
            print("process number:" , i)
            if end > len(all_ids):
                end = len(all_ids)-1
            p = multiprocessing.Process(target=get_all_products_info, args=(all_ids[start:end],cat['name'],i,))
            p.start()
            processes.append(p)
            start += 3400
            end = start + 3400

        for p in processes:
            p.join()

if __name__ == '__main__':
    main()
