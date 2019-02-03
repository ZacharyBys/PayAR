from flask import Flask
from flask import g
from flask import Response
from flask import request
from invoice import make_twilio_client, send_invoice, send_invoice_merchant, send_cancel_invoice

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
        cartId).fetchall()

        products = [{ 
            'id': row.product_id,
            'name': row.name,
            'price': float(row.price),
            'inventory_count': row.inventory_count,
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

        return { 
            'cart': {
                'id': cartId,
                'items': items,
                'total': total,
            } 
        }
    except Exception as e:
        print(e)
        return { 'cart': None, 'error': 'Error fetching cart with id {}'.format(cartId)}

def insert_cart_entry(cartId, productId):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO cart_entries (cart_id, product_id) VALUES (?, ?)', cartId, productId)
        conn.commit()
        return 'Item added to cart'
    except Exception as e:
        print(e)
        return { 'error': 'Error adding product with id {} to cart with id {}'.format(productId, cartId) }

def delete_cart_entry(cartId, productId):
    conn = get_db()
    cursor = conn.cursor()
    try:
        row = cursor.execute('DELETE TOP(1) FROM cart_entries WHERE cart_id=? AND product_id=?', cartId, productId)
        conn.commit()
        return 'Item removed from cart'
    except Exception as e:
        print(e)
        return { 'error': 'Error deleting product with id {} from cart with id {}'.format(productId, cartId) }

@app.route('/carts/<cartId>/checkout', methods=['POST'])
def checkout(cartId):
    conn = get_db()
    cursor = conn.cursor()

    userId = json.loads(request.data)['user_id']
    user = find_user(userId)
    
    cart = find_cart(cartId)
    try:
        source_money_req_id, message = payment_handler.request_payment(user, str(cart['total']), "sms")

        cursor.execute('INSERT into PendingPayments (req_id, cart_id) values (?, ?)', source_money_req_id, cartId)
        return Response(json.dumps({
            'message': message,
            'order': cart,
        }))
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
        row = cursor.execute('''
            SELECT 
                *
            FROM
                users
            WHERE id=?
        ''', 
        userId).fetchone()

        user = { 
            'id': row.id,
            'name': row.name,
            'phone': row.phone,
            'code': row.code,
            'email': row.email,
        }

        app.logger.info(user)
        return user
    except Exception as e:
        print(e)

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
        row = cursor.execute('SELECT * FROM PendingPayments WHERE req_id=?', source_money_req_id).fetchone()
        app.logger.info('row')
        app.logger.info(row)
        cartId = row.cart_id
        app.logger.info(cartId)
        cart = find_cart(cartId)
        user = find_user(cartId)
    except Exception as e:
        app.logger.error(e)
        
    if state == "REQUEST_COMPLETED":
        app.logger.info('payment was accepted')
        for item in cart['cart']['items']:
            product_id = item['product']['id']
            inventory_count = item['product']['inventory_count']
            quantity = item['quantity']

            if inventory_count < quantity:
                raise Exception('Insufficient inventory')

            cursor.execute('UPDATE products SET inventory_count = inventory_count - ? WHERE id=?', quantity, product_id)

            send_invoice(user, cart, twilio)
            app.logger.info('Sent invoice to {}'.format(user['phone']))
            send_invoice_merchant({ 'name': 'Chris\' Antiques', 'phone': '+15142125431' }, cart, twilio)
            app.logger.info('Sent invoice to {}'.format('+15142125431'))

    else:
        app.logger.info('payment failed or abort')
        send_cancel_invoice(user, cart, twilio)
        app.logger.info('Sent cancel invoice to {}'.format(user['phone']))
            

    cursor.execute('DELETE FROM cart_entries WHERE cart_id=?', cartId)
    cursor.execute('DELETE FROM PendingPayments WHERE cart_id=? and req_id=?', cartId, source_money_req_id)
    conn.commit()

    return Response(json.dumps({ 'message': 'Notification successfully sent' }))

if __name__ == '__main__':
    app.run(debug=True)
