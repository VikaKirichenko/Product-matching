from flask import Flask, render_template, request, url_for, redirect
import ast
from config import get_db_connection
from utilities import get_random_product, get_products_to_match
from utilities import predict_products
import pandas as pd


app = Flask(__name__)

product = ""
product_info = ''

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

@app.route('/predict_matches/', methods=['GET', 'POST'])
def predict_matches():
    global product
    global product_info
    if request.method == 'POST':
        # print('ok')
        if 'generate' in request.form:
            # return 'генерация товара'
            product = get_random_product(random_state = 12)

            conn = get_db_connection()
            cur = conn.cursor()
            product_info = get_info_by_id(product['id'],cur)

            cur.close()
            conn.close()
            # product = product_info
            for key,val in product.items(): 
                product[key] = '' if val is None else val
                # print(type(val))
            print(product)
            return render_template('predict_matches.html', product = product_info)
        
        elif 'search_matches' in request.form:
            products_to_match = get_products_to_match()
            print(products_to_match.shape)
            
            matched_pairs = predict_products(product.copy(),products_to_match)

            conn = get_db_connection()
            cur = conn.cursor()

            products_to_show = []
            for idx, pair in matched_pairs.iterrows():
                product1 = get_info_by_id(int(pair['id_1']),cur)
                products_to_show.append(product1)

            cur.close()
            conn.close()
            print(matched_pairs.shape)

            return render_template('predict_matches.html', product = product_info, matching_products = products_to_show)
        elif 'search' in request.form:
            # демо на этом товаре хорошо https://www.wildberries.ru/catalog/114477950/detail.aspx
            # демо на этом тож хорошо iphone 13,apple,70000, Спецификация модели - А2633. iPhone 13. Самая совершенная система двух камер на iPhone. Режим "Киноэффект" делает из видео настоящее кино. Супербыстрый чип A15 Bionic. Неутомимый аккумулятор. Прочный корпус. И еще более яркий дисплей Super Retina XDR.
            # print(request.form)
            product = {
                'id': -1, 
                'title':request.form['title'],
                'brand':request.form['brand'],
                'description':request.form['description'],
                'specifications':request.form['specifications'],
                'price': float(request.form['price']),
                'marketplace':'no'
            }
            product_info = product.copy()

            return render_template('predict_matches.html', product = product)
            # return product

            
    return render_template('predict_matches.html')
    product = {
        'title':'Xiaomi redmi note 8 pro',
        'brand':'Xiaomi',
        'price':19999,
        'description':'the best one',
        'specifications':'best^best^best'
    }
    product = get_random_product(random_state = 2)
    for key,val in product.items():
        product[key] = "" if pd.isna(val) else val

    print(product)


    conn = get_db_connection()
    cur = conn.cursor()
    product_info = get_info_by_id(product['id'],cur)

    cur.close()
    conn.close()


    # print(product)

    products_to_match = get_products_to_match()

    print(products_to_match.shape)

    # print(products_to_match.to_dict('records')
    
    matched_pairs = predict_products(product,products_to_match)
    print(type(matched_pairs))

    conn = get_db_connection()
    cur = conn.cursor()

    products_to_show = []
    for idx, pair in matched_pairs.iterrows():
        print(type(int(pair['id_1'])))
        product = get_info_by_id(int(pair['id_1']),cur)
        products_to_show.append(product)

    cur.close()
    conn.close()



    print(matched_pairs.shape)

    # prods = [product]
    return render_template('predict_matches.html', product = product_info, matching_products = products_to_show)


if __name__ == "__main__":
    app.run()