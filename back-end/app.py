from flask import Flask
from flask import g
from flask import Response
from flask import request
from invoice import make_twilio_client

import pyodbc
import json
import payment_handler

app = Flask(__name__)

server = 'pay-r.database.windows.net'
database = 'pay-r'
username = 'pay-r'
password = 'Party123'
driver= '{SQL Server}'

def get_twilio_client():
    if not hasattr(g, 'twilio'):
        g.twilio = make_twilio_client()

def get_db():
    if not hasattr(g, 'conn'):
        g.conn = get_db_connection()

    return g.conn

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'connection'):
        g.conn.close()
    
def get_db_connection():
    return pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)

@app.route('/')
def hello_world():
    return 'Weclome to Pay-R'

@app.route('/shops/<shopId>', methods=['GET'])
def shop(shopId):
    conn = get_db()
    cursor = conn.cursor() 

    try:
        row = cursor.execute('SELECT * FROM shops WHERE ID=?', shopId).fetchone()   
        shop = { 
            'shop': {
                'id': row.id,
                'name': row.name,
                'email': row.email,
                'phone': row.phone,
            },
        }
        return Response(json.dumps(shop), mimetype='application/json')
    except:
        return Response(json.dumps({ 'shop': None, 'error': 'No shop with id {}'.format(shopId)}), mimetype='application/json')

@app.route('/shops', methods=['GET'])
def shops():
    conn = get_db()
    cursor = conn.cursor()

    try:   
        rows = cursor.execute('SELECT * FROM shops').fetchall()
        shops = {
            'shops': [{ 
                'id': row.id,
                'name': row.name,
                'email': row.email,
                'phone': row.phone,
            } for row in rows]
        }
        
        return Response(json.dumps(shops), mimetype='application/json')
    except:
        return Response(json.dumps({ 'shops': None, 'error': 'Error fetching shops' }), mimetype='application/json')

@app.route('/products', methods=['GET'])
def products():
    conn = get_db()
    cursor = conn.cursor()

    try:   
        rows = cursor.execute('SELECT * FROM products').fetchall()
        products = {
            'products': [{ 
                'id': row.id,
                'name': row.name,
                'price': float(row.price),
                'inventory_count': row.inventory_count,
                'description': row.description,
            } for row in rows]
        }
        
        return Response(json.dumps(products), mimetype='application/json')
    except Exception as e:
        print(e)
        return Response(json.dumps({ 'products': None, 'error': 'Error fetching products' }), mimetype='application/json')


@app.route('/products/<productId>', methods=['GET'])
def product(productId):
    conn = get_db()
    cursor = conn.cursor()

    try:   
        row = cursor.execute('SELECT * FROM products WHERE id=?', productId).fetchone()
        product = {
            'product': { 
                'id': row.id,
                'name': row.name,
                'price': float(row.price),
                'inventory_count': row.inventory_count,
                'description': row.description,
            }
        }
        
        return Response(json.dumps(product), mimetype='application/json')
    except:
        return Response(json.dumps({ 'product': None, 'error': 'Error fetching product with id {}'.format(productId) }), mimetype='application/json')

@app.route('/carts/<cartId>', methods=['GET', 'PUT', 'DELETE'])
def cart(cartId):
    if request.method == 'GET':
        return find_cart(cartId)
    else:
        productId = json.loads(request.data)['product_id']
        if request.method == 'PUT':
            return insert_cart_entry(cartId, productId)
        elif request.method == 'DELETE':
            return delete_cart_entry(cartId, productId)

def find_cart(cartId):
    conn = get_db()
    cursor = conn.cursor()
    try:
        rows = cursor.execute('''
            SELECT 
                cart_id, product_id, name, description, price
            FROM
                cart_entries 
            JOIN 
                products
            ON 
                cart_entries.product_id = products.id 
            WHERE cart_id=?
        ''', 
        cartId).fetchall()

        products = [{ 
            'id': row.product_id,
            'name': row.name,
            'price': float(row.price),
            'description': row.description,
        } for row in rows]

        quantities = {}
        for product in products:
            productId = product['id']
            count = quantities.get(productId)
            if count is not None:
                quantities[productId] = count + 1
            else:
                quantities[productId] = 1

        items = []
        for product in products:
            productId = product['id']
            if productId in quantities.keys():
                items.append({ 
                    'product': product,
                    'quantity': quantities[productId],
                })

                quantities.pop(productId)

        total = 0
        for item in items:
            total += item['product']['price'] * item['quantity']

        return Response(json.dumps({ 
            'cart': {
                'items': items,
                'total': total,
            } 
        }), mimetype='application/json')
    except Exception as e:
        print(e)
        return Response(json.dumps({ 'cart': None, 'error': 'Error fetching cart with id {}'.format(cartId)}))

def insert_cart_entry(cartId, productId):
    conn = get_db()
    cursor = conn.cursor()
    try:
        row = cursor.execute('INSERT INTO cart_entries (cart_id, product_id) VALUES (?, ?)', cartId, productId)
        conn.commit()
        return Response(json.dumps({}), mimetype='application/json')
    except Exception as e:
        print(e)
        return Response(json.dumps({ 'error': 'Error adding product with id {} to cart with id {}'.format(productId, cartId) }))

def delete_cart_entry(cartId, productId):
    conn = get_db()
    cursor = conn.cursor()
    try:
        row = cursor.execute('DELETE TOP(1) FROM cart_entries WHERE cart_id=? AND product_id=?', cartId, productId)
        conn.commit()
        return Response(json.dumps({}), mimetype='application/json')
    except Exception as e:
        print(e)
        return Response(json.dumps({ 'error': 'Error deleting product with id {} from cart with id {}'.format(productId, cartId) }), mimetype='application/json')

@app.route('/carts/<cartId>/checkout', methods=['POST'])
def checkout(cartId):
    dropProcedure = 'DROP PROCEDURE IF EXISTS checkout'
    createProcedure = '''
     CREATE PROCEDURE checkout (IN product_id INT, IN quantity INT)
        BEGIN 
            DECLARE available INT;
            SET available = (SELECT inventory_count FROM products WHERE ID = product_id);
            IF 
                available < quantity 
            THEN
                SIGNAL SQLSTATE '45000';
            END IF;

            UPDATE 
                products
            SET
                inventory_count = inventory_count - quantity
            WHERE
                ID = product_id;
        END
    '''
    userId = json.loads(request.data)['user_id']
    cart = find_cart(cartId)
    user = find_user(userId)
    query = ''
    values = []
    cost = 0
    for item in cart['items']:
        product_id = item['product']['id']
        quantity = item['quantity']
        cost += int(quantity)*float(item['product']['price'])

        values.append(product_id, quantity)
        query += '''
            SET @PRODUCT_ID := ?
            SET @QUANTITY := ?

            CALL checkout(@PRODUCT_ID, @QUANTITY)
        '''

    values.append(cartId)
    query += '''
        DELETE FROM cart_entries WHERE cart_id=?
    '''

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(dropProcedure)
    cursor.execute(createProcedure)

    try:
        cursor.execute(query)
        return Response(json.dumps({'message':payment_handler.request_payment(user,str(cost),"sms")}))
    except Exception as e:
        print(e)
        return Response(json.dumps({ 'error': 'Error checking out cart with id {}'.format(cartId) }))

@app.route('/users', methods=['GET'])
def users():
    conn = get_db()
    cursor = conn.cursor()

    try:   
        rows = cursor.execute('SELECT * FROM users').fetchall()
        users = {
            'users': [{ 
                'id': row.id,
                'name': row.name,
                'phone': row.phone,
                'code': row.code,
                'email': row.email,
            } for row in rows]
        }
        
        return Response(json.dumps(users), mimetype='application/json')
    except Exception as e:
        print(e)
        return Response(json.dumps({ 'users': None, 'error': 'Error fetching products' }), mimetype='application/json')

def find_user(userId):
    conn = get_db()
    cursor = conn.cursor()
    try:
        rows = cursor.execute('''
            SELECT 
                *
            FROM
                users
            WHERE id=?
        ''', 
        userId).fetchall()

        users = {
            'users': [{ 
                'id': row.id,
                'name': row.name,
                'phone': row.phone,
                'code': row.code,
                'email': row.email,
            } for row in rows]
        }

        return users[0]
    except Exception as e:
        print(e)

@app.route('/notifications', methods=['POST'])
def notifications():
        state = json.loads(request.data)['moneyRequestUpdates'][0]["state"]
        if state == "REQUEST_FULFILLED":
                print('success')
                #TODO: GIVE THIS TO CLIENT SOMEHOW
        else:
                print('fail')
                #TODO: GIVE TO CLIENT THIS FAILURE

if __name__ == '__main__':
    app.run(debug=True)
