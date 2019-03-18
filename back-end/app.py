from flask import Flask
from flask import g
from flask import Response
from flask import request
from invoice import make_twilio_client, send_invoice, send_invoice_merchant, send_cancel_invoice

import sqlite3
import pyodbc
import json
import payment_handler

app = Flask(__name__)

server = 'pay-r.database.windows.net'
database = 'pay-r'
username = 'pay-r'
password = 'Party123'
driver= '{ODBC Driver 17 for SQL Server}'

def get_twilio_client():
    if not hasattr(g, 'twilio'):
        g.twilio = make_twilio_client()
    return g.twilio

def get_db():
    if not hasattr(g, 'conn'):
        g.conn = get_db_connection()

    return g.conn

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'connection'):
        g.conn.close()
    
def get_db_connection():
    try:
        conn = sqlite3.connect('payar.db')

        products = '''
            CREATE TABLE IF NOT EXISTS `products` (
            `id` INTEGER primary key autoincrement,
            `name` INTEGER NOT NULL,
            `price` DECIMAL(19,4) NOT NULL,
            `inventory_count` INTEGER NOT NULL DEFAULT 0,
            `description` VARCHAR(45));
            '''

        cart_entries = '''
            CREATE TABLE IF NOT EXISTS `cart_entries` (
            `id` INTEGER primary key autoincrement,
            `cart_id` INTEGER NOT NULL,
            `product_id` INTEGER NOT NULL,
            CONSTRAINT `fk_PRODUCT_ID1`
                FOREIGN KEY (`product_id`)
                REFERENCES `products` (`id`)
                ON DELETE NO ACTION
                ON UPDATE NO ACTION);
            '''

        pending = '''
            CREATE TABLE IF NOT EXISTS `PendingPayments` (
            `id` INTEGER primary key autoincrement,
            `cart_id` INTEGER NOT NULL,
            `req_id` VARCHAR(32) NOT NULL);
        '''

        shops = '''
            CREATE TABLE IF NOT EXISTS `shops` (
            `id` INTEGER primary key autoincrement,
            `name` VARCHAR(50) NOT NULL,
            `email` VARCHAR(50) NOT NULL,
            `phone` INTEGER NOT NULL);
        '''

        users ='''
            CREATE TABLE IF NOT EXISTS `users` (
            `id` INTEGER primary key autoincrement,
            `name` VARCHAR(50) NOT NULL,
            `phone` INTEGER NOT NULL,
            `code` INTEGER NOT NULL,
            `email` VARCHAR(50) NOT NULL);

        '''

        some_products = '''
            insert into products (name, price, inventory_count, description) values 
            ('SHARP EL-531X', 19.99, 100, 'ENCS-approved calculator'),
            ('Shea Beard Balm', 8.99, 100, 'Look good, smell great!'),
            ('Romance by Amarisse', 39.99, 100, 'Rosepetal Scented'),
            ('Surface Pro Book', 99.99, 100, 'The best 2-in-1'),
            ('Mints', 2.95, 100, 'Keep away bad breath with these hacker mints'),
            ('Playing Cards', 5, 100, 'Go fish')
        '''

        some_users = '''
            insert into users (name, phone, code, email) values 
            ('Jay Wreh', 5148362376, 1, 'jeremiahdavid.wreh@gmail.com')
        '''

        some_shops = '''
            insert into shops (name, email, phone) values
            ('Bys Buy', 'zachary.bys@gmail.com', 5149701830)
        '''


        conn.execute(products)
        conn.execute(cart_entries)
        conn.execute(pending)
        conn.execute(shops)
        conn.execute(users)
        return conn
    except Exception as e:
        app.logger.error(e)    

    # return pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)

@app.route('/')
def hello_world():
    return 'Weclome to Pay-R'

@app.route('/seed')
def seed():
    conn = get_db()
    some_products = '''
    insert into products (name, price, inventory_count, description) values 
    ('SHARP EL-531X', 19.99, 100, 'ENCS-approved calculator'),
    ('Shea Mositure Beard Balm', 8.99, 100, 'Look good, smell great!'),
    ('Romance by Amarisse', 39.99, 100, 'Rosepetal Scented'),
    ('Dell XPS 13', 99.99, 100, 'The best ultrabook'),
    ('Mints', 2.95, 100, 'Keep away bad breath with these hacker mints'),
    ('Playing Cards', 5, 100, '')
'''

    some_users = '''
        insert into users (name, phone, code, email) values 
        ('Jay Wreh', 5148362376, 1, 'jeremiahdavid.wreh@gmail.com')
    '''

    some_shops = '''
        insert into shops (name, email, phone) values
        ('Bys Buy', 'zachary.bys@gmail.com', 5149701830)
            '''
    conn.execute(some_users)
    conn.execute(some_shops)
    conn.execute(some_products)

@app.route('/shops/<shopId>', methods=['GET'])
def shop(shopId):
    conn = get_db()
    cursor = conn.cursor() 

    try:
        row = cursor.execute('SELECT * FROM shops WHERE ID=?', shopId).fetchone()   
        shop = { 
            'shop': {
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'phone': row[3],
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
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'phone': row[3],
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
                'id': row[0],
                'name': row[1],
                'price': float(row[2]),
                'inventory_count': row[3],
                'description': row[4],
            } for row in rows]
        }
        
        return Response(json.dumps(products), mimetype='application/json')
    except Exception as e:
        app.logger.error(e)
        return Response(json.dumps({ 'products': None, 'error': 'Error fetching products' }), mimetype='application/json')


@app.route('/products/<productId>', methods=['GET'])
def product(productId):
    conn = get_db()
    cursor = conn.cursor()

    try:   
        row = cursor.execute('SELECT * FROM products WHERE id=?', productId).fetchone()
        product = {
            'product': { 
                'id': row[0],
                'name': row[1],
                'price': float(row[2]),
                'inventory_count': row[3],
                'description': row[4],
            }
        }
        
        return Response(json.dumps(product), mimetype='application/json')
    except:
        return Response(json.dumps({ 'product': None, 'error': 'Error fetching product with id {}'.format(productId) }), mimetype='application/json')

@app.route('/carts/<cartId>', methods=['GET', 'PUT', 'DELETE'])
def cart(cartId):
    conn = get_db()
    cursor = conn.cursor()

    try:
        row = cursor.execute('SELECT * FROM PendingPayments WHERE cart_id=?', [cartId]).fetchone()
        if row is not None:
            app.logger.info('Checkout already in progress for cart with id {}'.format(cartId))
            return Response(json.dumps({ 'cart': None }), mimetype='application/json')
    except Exception as e:
        app.logger.error(e)
        return Response(json.dumps({ 'cart': None, 'error': 'Error checking cart status' }), mimetype='application/json')
    if request.method == 'GET':
        return Response(json.dumps(find_cart(cartId)), mimetype='application/json')
    else:
        productId = json.loads(request.data)['product_id']
        if request.method == 'PUT':
            return Response(json.dumps(insert_cart_entry(cartId, productId)), mimetype='application/json')
        elif request.method == 'DELETE':
            return Response(json.dumps(delete_cart_entry(cartId, productId)), mimetype='application/json')

def find_cart(cartId):
    conn = get_db()
    cursor = conn.cursor()
    try:
        rows = cursor.execute('''
            SELECT 
                cart_id, product_id, name, description, price, inventory_count
            FROM
                cart_entries 
            JOIN 
                products
            ON 
                cart_entries.product_id = products.id 
            WHERE cart_id=?
        ''', 
        (cartId,)).fetchall()

        products = [{ 
            'id': row[1],
            'name': row[2],
            'description': row[3],
            'price': float(row[4]),
            'inventory_count': row[5],
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

        return { 
            'cart': {
                'id': cartId,
                'items': items,
                'total': total,
            } 
        }
    except Exception as e:
        app.logger.error(e)
        return { 'cart': None, 'error': 'Error fetching cart with id {}'.format(cartId)}

def insert_cart_entry(cartId, productId):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO cart_entries (cart_id, product_id) VALUES (?, ?)', (cartId, productId))
        conn.commit()
        app.logger.info('Added item with id {} to cart with id {}'.format(productId, cartId))
        return 'Item added to cart'
    except Exception as e:
        app.logger.error(e)
        return { 'error': 'Error adding product with id {} to cart with id {}'.format(productId, cartId) }

def delete_cart_entry(cartId, productId):
    conn = get_db()
    cursor = conn.cursor()
    try:
        row = cursor.execute('SELECT id FROM cart_entries WHERE cart_id=? AND product_id=?', (cartId, productId)).fetchall()
        if len(row) == 0:
            return 'Item not in cart'

        row_to_delete = row[0]
        row = cursor.execute('DELETE FROM cart_entries WHERE id=?', row_to_delete)
        conn.commit()
        app.logger.info('Removed item with id {} to cart with id {}'.format(productId, cartId))
        return 'Item removed from cart'
    except Exception as e:
        app.logger.error(e)
        return { 'error': 'Error deleting product with id {} from cart with id {}'.format(productId, cartId) }

@app.route('/carts/<cartId>/checkout', methods=['POST'])
def checkout(cartId):
    conn = get_db()
    cursor = conn.cursor()

    user = find_user(cartId)
    cart = find_cart(cartId)

    if len(cart['cart']['items']) == 0:
        return Response(json.dumps({ 'error': 'Cannot checkout an empty cart' }))

    try:
        row = cursor.execute('SELECT * FROM PendingPayments WHERE cart_id=?', [cartId]).fetchone()
        if row is not None:
            app.logger.info('Checkout already in progress for cart with id {}'.format(cartId))
            return Response(json.dumps({ 'cart': None, 'message': 'Checkout already in progress' }), mimetype='application/json')
    except Exception as e:
        app.logger.error(e)
        return Response(json.dumps({ 'cart': None, 'error': 'Error checking cart status' }), mimetype='application/json')

    for item in cart['cart']['items']:
        product_id = item['product']['id']
        inventory_count = item['product']['inventory_count']
        quantity = item['quantity']

        if inventory_count < quantity:
            return Response(json.dumps({ 'error': 'Insufficient inventory to checkout cart' }))

    try:
        source_money_req_id, message = payment_handler.request_payment(user, str(cart['cart']['total']), "sms")
        cursor.execute('INSERT INTO PendingPayments (req_id, cart_id) values (?, ?)', (source_money_req_id, cartId))
        conn.commit()
        app.logger.info('Order for cart with id {} is now pending'.format(cartId))
        return Response(json.dumps({
            'message': message,
            'order': cart,
        }))
    except Exception as e:
        app.logger.error(e)
        return Response(json.dumps({ 'error': 'Error checking out cart with id {}'.format(cartId) }))

@app.route('/users', methods=['GET'])
def users():
    conn = get_db()
    cursor = conn.cursor()

    try:   
        rows = cursor.execute('SELECT * FROM users').fetchall()
        users = {
            'users': [{ 
                'id': row[0],
                'name': row[1],
                'phone': row[2],
                'code': row[3],
                'email': row[4],
            } for row in rows]
        }
        
        return Response(json.dumps(users), mimetype='application/json')
    except Exception as e:
        app.logger.error(e)
        return Response(json.dumps({ 'users': None, 'error': 'Error fetching products' }), mimetype='application/json')

def find_user(userId):
    conn = get_db()
    cursor = conn.cursor()
    try:
        row = cursor.execute('''
            SELECT 
                *
            FROM
                users
            WHERE id=?
        ''', 
        (userId,)).fetchone()

        user = { 
            'id': row[0],
            'name': row[1],
            'phone': row[2],
            'code': row[3],
            'email': row[4],
        }

        return user
    except Exception as e:
        app.logger.error(e)

@app.route('/notifications', methods=['POST'])
def notifications():
    twilio = get_twilio_client()

    state = json.loads(request.data)['moneyRequestUpdates'][0]["state"]
    source_money_req_id = json.loads(request.data)['moneyRequestUpdates'][0]["moneyRequestDetails"]['requesterMessage'] # to change back
    app.logger.info(source_money_req_id)

    conn = get_db()
    cursor = conn.cursor()

    user = None
    cart = None
    try:
        row = cursor.execute('SELECT * FROM PendingPayments WHERE req_id=?', [source_money_req_id]).fetchone()
        cartId = row[1]
        cart = find_cart(cartId)
        user = find_user(cartId)
    except Exception as e:
        app.logger.error(e)

    try:     
        if state == "REQUEST_COMPLETED" or state == "REQUEST_FULFILLED":
            app.logger.info('payment was accepted')
            for item in cart['cart']['items']:
                product_id = item['product']['id']
                inventory_count = item['product']['inventory_count']
                quantity = item['quantity']

                if inventory_count < quantity:
                    raise Exception('Insufficient inventory')

                query = 'UPDATE products SET inventory_count = inventory_count - {} WHERE id=?'.format(quantity)
                cursor.execute(query, [product_id])

            send_invoice(user, cart, twilio)
            app.logger.info('Sent invoice to {}'.format(user['phone']))
            # ADD PHONE NUMBER TO BOTH LINES BELOW
            send_invoice_merchant({ 'name': 'Bys Buy', 'phone': '5149701830' }, cart, twilio)
            app.logger.info('Sent invoice to {}'.format('5148362376'))

        else:
            app.logger.info('payment failed or abort')
            send_cancel_invoice(user, cart, twilio)
            app.logger.info('Sent cancel invoice to {}'.format(user['phone']))        

        cursor.execute('DELETE FROM cart_entries WHERE cart_id=?', [cartId])
        app.logger.debug('Deleting PendingPayment with cart id {} and req id {}'.format(cartId, source_money_req_id))
        cursor.execute('DELETE FROM PendingPayments WHERE cart_id=? and req_id=?', (cartId, source_money_req_id))
        conn.commit()

        return Response(json.dumps({ 'message': 'Notification successfully sent' }))
    except Exception as e:
        app.logger.error(e)
        Response(json.dumps({ 'message': 'Error completing cart' }))

if __name__ == '__main__':
    app.run(debug=True)
