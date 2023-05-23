import ast

import pandas as pd
from flask import Flask, redirect, render_template, request, url_for

from config import get_db_connection, to_db
from utilities import (get_products_to_match, get_random_product,
                       predict_matches_bert, predict_products)

app = Flask(__name__)

product = ""
product_info = ''
products_to_show = []

def get_info_by_id(product_id,cur):
    cur.execute('SELECT title, brand, price, description, specifications, marketplace,url '
                'FROM products '
                'WHERE id = (%s);',(product_id,))
    product_info = cur.fetchall()[0]
    
    product = {
        'id' : product_id,
        'title':product_info[0],
        'brand':product_info[1],
        'price':product_info[2],
        'description':product_info[3],
        'specifications':ast.literal_eval(product_info[4]),
        'marketplace':product_info[5],
        'url':product_info[6]
    }
    return product

def get_info_by_id_web(product_id,cur):
    cur.execute('SELECT title, brand, price, description, specifications,category '
                'FROM input_products '
                'WHERE id = (%s);',(product_id,))
    product_info = cur.fetchall()[0]
    product = {
        'id' : product_id,
        'title':product_info[0],
        'brand':product_info[1],
        'price':product_info[2],
        'description':product_info[3],
        'specifications':product_info[4],
        'category':product_info[5]
    }
    return product


@app.route('/')
def index():
    # указать ссылки для выбора либо разбетки данных, либо проверки качества
    return redirect(url_for('products'))
    # return render_template('index.html')

@app.route('/products/', methods=['GET', 'POST'])
def products():
    if request.method == 'POST':
        keys=[]
        for key in request.form:
            keys.append((key, request.form[key]))
        ids = keys[::2]
        options = keys[1::2]

        conn = get_db_connection()
        cur = conn.cursor()
        for id, option in zip(ids,options):
            id_ =  request.form.get(id[0])
            option_ = request.form.get(option[0])
            
            cur.execute('UPDATE pairs SET match_type = %s WHERE pair_id = %s;',(str(option_),int(id_)))
            updated_rows = cur.rowcount
            conn.commit()
        cur.close()
        conn.close()
        

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT pair_id, id_1, id_2 FROM pairs WHERE match_type = (%s) and category = (%s) LIMIT 4;',('-1','tv',))
    # cur.execute('SELECT pair_id, id_1, id_2 FROM pairs p INNER JOIN products pr1 ON p.id_1 = pr1.id INNER JOIN products pr2 ON p.id_2 = pr2.id WHERE pr1.marketplace = (%s) and p.match_type = (%s) and p.category = (%s) LIMIT 4;',('wb','-1','tv',))
    # cur.execute('SELECT pair_id, id_1, id_2 FROM pairs WHERE match_type = (%s) LIMIT 4;',('-1',))
    # cur.execute('SELECT pair_id, id_1, id_2 FROM pairs_by_model WHERE match_type > 4 LIMIT 4;')
    pairs = cur.fetchall()

    pairs_to_show = []
    for pair in pairs:
        product1 = get_info_by_id(pair[1],cur)
        product2 = get_info_by_id(pair[2],cur)
        new_pair = {
            'pair_id':pair[0],
            'product1': product1,
            'product2': product2
            }
        pairs_to_show.append(new_pair)

    cur.close()
    conn.close()

    return render_template('products1.html',data = pairs_to_show, displays = [0,0,0,0])


@app.route('/saved_searches/', methods=['GET', 'POST'])
def saved_searches():
    # запрос к бд с сохраненными поисками
    # вывод всей инфы как в predict_matches, только вместо app/rej указать количество матчей на кнопке,
    #  по которой можно жмакнуть и посмотреть все детально, а еще можно добавить кнопку для удаления
    if request.method == 'POST':
        if 'get_matches' in request.form:
            item_id = request.form['get_matches']
            web = True if 'True' in item_id else False
            item_id = item_id.replace(str(web),'')
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('SELECT main_id, matched_ids, web FROM saved_searches WHERE main_id = (%s) and web = (%s);',(item_id,web,))
            saved_searches = cur.fetchall()
            searches_to_show = []
            for search in saved_searches:
                if search[2]:
                    product = get_info_by_id_web(search[0],cur)
                else:
                    product = get_info_by_id(search[0],cur)
                match_ids = search[1].split(',')
                matches_products = []
                for id in match_ids:
                    match_product = get_info_by_id(id,cur)
                    matches_products.append(match_product)

                new_search = {
                    'product': product,
                    'matches': matches_products,
                    'web':search[2]
                }

                searches_to_show.append(new_search)
            cur.close()
            conn.close()
            searches_to_show = searches_to_show[0]
            return render_template('saved_matches.html',product = searches_to_show['product'],data = searches_to_show['matches'],web = searches_to_show['web'])
        elif 'delete_prod' in request.form:
            item_id = request.form['item_id']
            item_id = request.form['delete_prod']
            web = True if 'True' in item_id else False
            item_id = item_id.replace(str(web),'')
            # print(web, item_id)
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('DELETE FROM saved_searches WHERE main_id = (%s) and web = (%s);',(item_id,web,))
            conn.commit()
            cur.close()
            conn.close()


    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT main_id, matched_ids, web FROM saved_searches;')
    saved_searches = cur.fetchall()
    
    searches_to_show = []
    for search in saved_searches:
        if search[2]:
            product = get_info_by_id_web(search[0],cur)
        else:
            product = get_info_by_id(search[0],cur)
        num_matches = len(search[1].split(','))
        new_search = {
            'product': product,
            'num_matches': num_matches,
            'web':search[2]
        }

        searches_to_show.append(new_search)
    cur.close()
    conn.close()
    return render_template('saved_searches.html',data = searches_to_show)


@app.route('/predict_matches/', methods=['GET', 'POST'])
def predict_matches():
    global product
    global product_info
    global products_to_show
    if request.method == 'POST':
        if 'generate' in request.form:
            product = get_random_product(category=request.form['category']) # random_state = 1, 

            conn = get_db_connection()
            cur = conn.cursor()
            product_info = get_info_by_id(product['id'],cur)

            cur.close()
            conn.close()
            for key,val in product.items(): 
                product[key] = '' if val is None else val
            return render_template('predict_matches.html', product = product_info)
        
        elif 'search_matches' in request.form:
            products_to_match = get_products_to_match(category=product['category'])
            print(products_to_match.shape)
            
            matched_pairs = predict_products(product.copy(),products_to_match)
            # matched_pairs = predict_matches_bert(product.copy())

            print('ok')

            conn = get_db_connection()
            cur = conn.cursor()

            products_to_show = []
            for idx, pair in matched_pairs.iterrows():
                product1 = get_info_by_id(int(pair['id_1']),cur)
                products_to_show.append(product1)

            cur.close()
            conn.close()
            print(matched_pairs.shape)

            return render_template('predict_matches.html', product = product_info, matching_products = products_to_show, search = False if product['id'] == -1 else True)
        elif 'search' in request.form:
            # демо на этом товаре хорошо https://www.wildberries.ru/catalog/114477950/detail.aspx
            # демо на этом тож хорошо iphone 13,apple,70000, Спецификация модели - А2633. iPhone 13. Самая совершенная система двух камер на iPhone. Режим "Киноэффект" делает из видео настоящее кино. Супербыстрый чип A15 Bionic. Неутомимый аккумулятор. Прочный корпус. И еще более яркий дисплей Super Retina XDR.
            # хорошее демо для игрушек https://www.wildberries.ru/catalog/122890770/detail.aspx
            # print(request.form)
            product = {
                'id': -1, 
                'title':request.form['title'],
                'brand':request.form['brand'],
                'description':request.form['description'],
                'specifications':request.form['specifications'],
                'price': float(request.form['price']),
                'marketplace':'no',
                'category':request.form['category'],
            }
            product_info = product.copy()

            return render_template('predict_matches.html', product = product, search = False if product['id'] == -1 else True)
        elif 'save_corrections' in request.form:

            keys=[]
            for key in request.form:
                keys.append((key, request.form[key]))
            # print(keys)
            main_id = [el[1] for el in keys if 'main_id' in el[0]][0]
            
            ids_to_pair = [{'pair_id':main_id+el[1],'id_1':main_id,'id_2':el[1],'match_correction':-1} for el in keys if 'item_id' in el[0]]
            
            for pair in ids_to_pair:
                for key in keys:
                    if pair['id_2'] in key[0] and 'match' in key[0]:
                        if key[1] == '1':
                            pair['match_correction'] = 1  
                        else:
                            pair['match_correction'] = 0
            not_null = [pair['id_2'] for pair in ids_to_pair if pair['match_correction']!=0]
            pairs_to_correction1 = pd.DataFrame(ids_to_pair)
            pairs_to_correction = pairs_to_correction1[pairs_to_correction1['match_correction']!=-1]
            to_db(pairs_to_correction,'corrected_pairs')
            products_to_show = [prod for prod in products_to_show if str(prod['id']) in not_null]
            return render_template('predict_matches.html', product = product_info, matching_products = products_to_show)
        elif 'save_search' in request.form: 
            keys=[]
            for key in request.form:
                keys.append((key, request.form[key]))
            main_id = [el[1] for el in keys if 'main_id' in el[0]][0]
            ids_to_pair = [el[1] for el in keys if 'item_id' in el[0]]
            # main_id может быть -1, если это из поиска, нужно это обработать путем изначального добавления товара в бд,
            #  если его не существует, но указав, что там нет маркетплейса и тд, чтобы в дальнейшем анализе они не участвовали 
            # или участвовали, не знаю, не решила
            
            # сделать тут insert values
            web = False
            if product['id'] == -1:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute('INSERT INTO input_products(title, brand, price, description, specifications, category) \
                            VALUES(%s,%s,%s,%s,%s,%s) RETURNING id;'
                            ,(product['title'],product['brand'],product['price'],product['description'],product['specifications'],product['category'],))
                id_of_new_row = cur.fetchone()[0]
                conn.commit()
                cur.close()
                conn.close()
                main_id = id_of_new_row
                web = True
            pairs = [{'main_id':main_id, 'matched_ids': ','.join(ids_to_pair),'web':web}]
            pairs_to_save = pd.DataFrame(pairs)
            to_db(pairs_to_save,'saved_searches')
        elif 'saved_searches' in request.form:
            return redirect(url_for('saved_searches'))

            
    return render_template('predict_matches.html')


if __name__ == "__main__":
    app.run()