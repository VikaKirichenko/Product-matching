from flask import Flask, render_template, request, url_for, redirect
import ast
from config import get_db_connection

app = Flask(__name__)


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
    cur.execute('SELECT pair_id, id_1, id_2 FROM pairs WHERE match_type = (%s) LIMIT 4;',('-1',))
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


if __name__ == "__main__":
    app.run()