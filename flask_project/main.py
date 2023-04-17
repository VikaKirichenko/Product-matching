from flask import Flask, render_template, request, url_for, redirect, jsonify
# from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from datetime import datetime, timedelta
from random import randint
import os
import pandas as pd
import psycopg2
import ast


app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(host='84.201.175.11',
                            database='wishlist',
                            user='web_app',
                            password='shopsdb9274')
    return conn


def get_info_by_id(product_id,cur):
    cur.execute('SELECT title, brand, price, description, specifications '
                'FROM products '
                'WHERE id = (%s);',(product_id,))
    product_info = cur.fetchall()[0]
    product = {
        'title':product_info[0],
        'brand':product_info[1],
        'price':product_info[2],
        'description':product_info[3],
        'specifications':ast.literal_eval(product_info[4])
    }
    return product


@app.route('/')
def index():
    # сделать url_for на products
    return render_template('index.html')

@app.route('/products/', methods=['GET', 'POST'])
def products():
    if request.method == 'POST':
        keys=[]
        for key in request.form:
            # print(key, request.form[key])
            keys.append((key, request.form[key]))
        ids = keys[::2]
        options = keys[1::2]
        # print(ids)
        # print(options)
        
        # option = request.form.getlist('options')
        # print(request.form.get('match0'))
        # print(request.form.get('match1'))
        # тут надо еще проверить, что все элементы не None
        conn = get_db_connection()
        cur = conn.cursor()
        for id, option in zip(ids,options):
            id_ =  request.form.get(id[0])
            option_ = request.form.get(option[0])
            # print('id',id_,'match', option_)
            
            cur.execute('UPDATE pairs SET match_type = %s WHERE pair_id = %s;',(str(option_),int(id_)))
            updated_rows = cur.rowcount
            conn.commit()
            # print(updated_rows)
        cur.close()
        conn.close()
        

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT pair_id, id_1, id_2 FROM pairs WHERE match_type = (%s) LIMIT 4;',('-1',))
    pairs = cur.fetchall()

    # print(pairs,cur)
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

    # print(pairs_to_show[0])
    # print(len(pairs_to_show))





    data = []
    pair1 = {
        'id': 0,
        'title_1':'смартфон1',
        'brand_1':'brand1',
        'price_1':'price1',
        'description_1':'desc1',
        'attributes_1': 'attrs',
        'title_2':'смартфон2',
        'brand_2':'brand2',
        'price_2':'price2',
        'description_2':'desc2',
        'attributes_2': 'attr2'
    }
    data.append(pair1)

    return render_template('products1.html',data = pairs_to_show, displays = [0,0,0,0])


if __name__ == "__main__":
    app.run()