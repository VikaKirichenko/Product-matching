# здесь по id переходить не надо, все хранится на главной странице

import requests
from utils import write_to_csv
from tqdm import tqdm

cookies = {
    '__ddg2_': 'GaQafPD5yS0dURT1',
    '__ddg1_': 'IW6bAVrOKj4lXSDKRe2q',
    'refresh-token': '',
    'tmr_lvid': 'f84bb286dc1aa336706c722e9e7d4808',
    'tmr_lvidTS': '1653036559989',
    '_ga': 'GA1.1.38288911.1682717701',
    'gdeslon.ru.__arc_domain': 'gdeslon.ru',
    'gdeslon.ru.user_id': '2b2d65a2-7d8e-4425-b007-cb553a47a0ec',
    'popmechanic_sbjs_migrations': 'popmechanic_1418474375998%3D1%7C%7C%7C1471519752600%3D1%7C%7C%7C1471519752605%3D1',
    '_ym_uid': '1653036562721396406',
    '_ym_d': '1682717704',
    'chg_visitor_id': '3c6c9a25-9432-47b2-b8d4-ccf0be6bc675',
    'analytic_id': '1682718833484804',
    '__utmz': '106893445.1682725240.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
    'access-token': 'Bearer%20eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL3VzZXIucHJvZC5jZ29yb2QucHciLCJzdWIiOiJjMWJkODQ1YzhmYjBmODY0YmUxM2JiZjNiYjQ3NTY0Y2RkMmI3MGFmNjYzZDE1NzFiMWQyMGZkMWMyOGIxYWZhIiwiaWF0IjoxNjgyOTQxMTU0LCJleHAiOjE2ODMxMTM5NTQsInR5cGUiOjEwfQ.3Kll7x3QcOWHpTYbbruofBHhZXNDAqxEciWa6ihRCk8',
    '__utma': '159384943.320122458.1682717695.1682727366.1682941159.4',
    '__utmc': '159384943',
    '__utmz': '159384943.1682941159.4.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided)',
    '__utmt': '1',
    '_ym_isad': '2',
    '__utma': '106893445.38288911.1682717701.1682725240.1682941575.2',
    '__utmc': '106893445',
    '__utmb': '106893445.1.10.1682941575',
    'mindboxDeviceUUID': '19d177e2-db11-40cf-b6a7-fea4b07927a2',
    'directCrm-session': '%7B%22deviceGuid%22%3A%2219d177e2-db11-40cf-b6a7-fea4b07927a2%22%7D',
    '__utmb': '159384943.3.10.1682941159',
    '_ga_LN4Z31QGF4': 'GS1.1.1682941158.4.1.1682941601.46.0.0',
    '_ga_W0V3RXZCPY': 'GS1.1.1682941158.4.1.1682941601.0.0.0',
}

headers = {
    'authority': 'web-gate.chitai-gorod.ru',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'ru-RU,ru;q=0.9,en-RU;q=0.8,en;q=0.7,el-GR;q=0.6,el;q=0.5,en-US;q=0.4',
    'authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL3VzZXIucHJvZC5jZ29yb2QucHciLCJzdWIiOiJjMWJkODQ1YzhmYjBmODY0YmUxM2JiZjNiYjQ3NTY0Y2RkMmI3MGFmNjYzZDE1NzFiMWQyMGZkMWMyOGIxYWZhIiwiaWF0IjoxNjgyOTQxMTU0LCJleHAiOjE2ODMxMTM5NTQsInR5cGUiOjEwfQ.3Kll7x3QcOWHpTYbbruofBHhZXNDAqxEciWa6ihRCk8',
    'cache-control': 'no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0',
    # 'cookie': '__ddg2_=GaQafPD5yS0dURT1; __ddg1_=IW6bAVrOKj4lXSDKRe2q; refresh-token=; tmr_lvid=f84bb286dc1aa336706c722e9e7d4808; tmr_lvidTS=1653036559989; _ga=GA1.1.38288911.1682717701; gdeslon.ru.__arc_domain=gdeslon.ru; gdeslon.ru.user_id=2b2d65a2-7d8e-4425-b007-cb553a47a0ec; popmechanic_sbjs_migrations=popmechanic_1418474375998%3D1%7C%7C%7C1471519752600%3D1%7C%7C%7C1471519752605%3D1; _ym_uid=1653036562721396406; _ym_d=1682717704; chg_visitor_id=3c6c9a25-9432-47b2-b8d4-ccf0be6bc675; analytic_id=1682718833484804; __utmz=106893445.1682725240.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); access-token=Bearer%20eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL3VzZXIucHJvZC5jZ29yb2QucHciLCJzdWIiOiJjMWJkODQ1YzhmYjBmODY0YmUxM2JiZjNiYjQ3NTY0Y2RkMmI3MGFmNjYzZDE1NzFiMWQyMGZkMWMyOGIxYWZhIiwiaWF0IjoxNjgyOTQxMTU0LCJleHAiOjE2ODMxMTM5NTQsInR5cGUiOjEwfQ.3Kll7x3QcOWHpTYbbruofBHhZXNDAqxEciWa6ihRCk8; __utma=159384943.320122458.1682717695.1682727366.1682941159.4; __utmc=159384943; __utmz=159384943.1682941159.4.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __utmt=1; _ym_isad=2; __utma=106893445.38288911.1682717701.1682725240.1682941575.2; __utmc=106893445; __utmb=106893445.1.10.1682941575; mindboxDeviceUUID=19d177e2-db11-40cf-b6a7-fea4b07927a2; directCrm-session=%7B%22deviceGuid%22%3A%2219d177e2-db11-40cf-b6a7-fea4b07927a2%22%7D; __utmb=159384943.3.10.1682941159; _ga_LN4Z31QGF4=GS1.1.1682941158.4.1.1682941601.46.0.0; _ga_W0V3RXZCPY=GS1.1.1682941158.4.1.1682941601.0.0.0',
    'origin': 'https://www.chitai-gorod.ru',
    'referer': 'https://www.chitai-gorod.ru/',
    'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
}

params = {
    'category': 'biznes-torgovlya-9027',
}

def get_data(url):
    for i in range(1, 76):
        print('page',i)
        params['page'] = i
        response  = requests.get(url, params=params, cookies=cookies, headers=headers)
        # print(response)
        data = response.json()  

        # all_products_info = []
        # print(data)
        print(len(data['data']))

        for product in data['data']:
            # print(product)
            # break
            params1 = {'city': '213',}
            url_weight = f"https://web-gate.chitai-gorod.ru/api/v1/availability/{product['id']}"
            resp = requests.get(url_weight, params=params1, cookies=cookies, headers=headers)
            # print(resp)
            weight = resp.json().get('data').get('product').get('weight')
            weight = weight if weight else ""
            specs = {
                'Издательство': product.get('publisher').get('title'),
                'Год издания': product.get('yearPublishing'),
                'Кол-во страниц': product.get('pages'),
                'Тип обложки': product.get('binding'),
                'Вес': weight
            }
            specs = {key:val for key,val in specs.items() if val != "" and val is not None}

            auths = ', '.join([auth['firstName'] + ' '+ auth['lastName'] for auth in product['authors']])
            book = {
                'id_on_store': product['id'],
                'title': product['title'],
                'brand':auths,
                'price': product['price'],
                'description':product['description'],
                'specifications': specs,
                'category': 'books',
                'marketplace':'chitai-gorod',
                'url': 'https://www.chitai-gorod.ru/' + product['url']
            }
            # all_products_info.append(book)
            write_to_csv(book,'data/cg_books_data.csv')

    

def main():
    url = 'https://web-gate.chitai-gorod.ru/api/v1/products'
    get_data(url)

if __name__ == '__main__':
    main()
