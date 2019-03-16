from twilio.rest import Client

account_sid = 'ACf15f803466e552406bc7159a2799755b'
auth_token = 'dfd6cab4f988fb3374156b471ad1ab2e'
twilio_number = '+16474902397'

def make_twilio_client():
    return Client(account_sid, auth_token)

def get_order_summary(order):
    summary = ''
    for item in order['items']:
        item_name = item['product']['name']
        item_quantity = item['quantity']
        item_price = item['product']['price']
        summary += '{} x {}:\t${}\n'.format(item_name, item_quantity, item_price * item_quantity)
    
    summary += '\t--------------------------\n'
    summary += 'Total:\t${}\n'.format(str(order['total']))

    return summary

def send_invoice(to_user, cart, twilio):
    name = to_user['name']
    to_number = to_user['phone']
    shop = 'Chris\' Antiques'
    formattedOrderSummary = get_order_summary(cart['cart'])

    invoice = '''
        Hi {},

        Thank you for your recent purchase at {}!

        Order summary:

        {}
    '''.format(name, shop, formattedOrderSummary)

    twilio.messages.create(body=invoice, from_=twilio_number, to=to_number)


def send_invoice_merchant(to_merchant, cart, twilio):
    shop_name = to_merchant['name']
    number = to_merchant['phone']
    formattedOrderSummary = get_order_summary(cart['cart'])
    invoice = '''
        {},

        A new order has been placed!

        Order summary:

        {}
    '''.format(shop_name, formattedOrderSummary)

    twilio.messages.create(body=invoice, from_=twilio_number, to=number)

def send_cancel_invoice(to_user, cart, twilio):
    shop_name = to_user['name']
    number = to_user['phone']
    formattedOrderSummary = get_order_summary(cart['cart'])
    invoice = '''
        {},

        The following order was canceled:

        {}
    '''.format(shop_name, formattedOrderSummary)

    twilio.messages.create(body=invoice, from_=twilio_number, to=number)
