from twilio.rest import Client

account_sid = 'ACf15f803466e552406bc7159a2799755b'
auth_token = 'dfd6cab4f988fb3374156b471ad1ab2e'
twilio_number = '+16474902397'

def make_twilio_client():
    return Client(account_sid, auth_token)

def get_order_summary(order):
    summary = ''
    for item in order:
        item_name = item['product']['name']
        item_quantity = item['quantity']
        item_price = item['product']['price']
        summary += '{} x {}:\t{}\n'.format(item_name, item_quantity, item_price * item_quantity)
    
    summary += '-------'
    summary += order['total']

    return summary

def send_invoice(to_user, order, twilio):
    name = to_user['name']
    to_number = to_user['to_number']
    shop = order['shop']
    formattedOrderSummary = get_order_summary(order)

    invoice = '''
        Hi {},

        Thank you for your recent purchase at {}!

        Order summary:

        {}
    '''.format(name, shop, formattedOrderSummary)

    twilio.messages.create(body=invoice, from_=twilio_number, to=to_number)

def send_invoice_merchant(to_merchant, order, twilio):
    shop_name = to_merchant['name']
    formattedOrderSummary = get_order_summary(order)
    invoice = '''
        {},

        A new order has been placed!

        Order summary:

        {}
    '''.format(shop_name, formattedOrderSummary)


