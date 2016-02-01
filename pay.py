"""
A small Python script to generate invoices for beer and other drinks.
"""

import sys

import requests

import bitcoin


CURRENCY = 'CHF'
NOTIFICATION_EMAIL = 'mail@dbrgn.ch'
REDIRECT_URL = 'https://www.coredump.ch/'
BUYER_NAME = 'Coredump Hacker'
BUYER_CITY = 'Rapperswil'
BUYER_ZIP = 8640
BUYER_COUNTRY = 'Switzerland'
PAIRING_CODE = 'XXX'


def parse_args(args):
    """
    Parse arguments, return dict.
    """
    if not args:
        raise ValueError('Empty argument list')
    if len(args) != 2:
        print('Usage: %s <amount-in-chf>' % args[0])
        print('Example: %s 2.50' % args[0])
    return {
        'amount': float(args[1]),
    }


def get_pairing_code():
    """
    Create a new API token, return pairing code.
    """
    sin = bitcoin.generate_sin()
    data = {
        'label': 'Beerpay',
        'id': sin,
        'facade': 'pos',
    }
    response = requests.post('https://bitpay.com/tokens', json=data)
    response.raise_for_status()
    return response.json()['data'][0]['pairingCode']


def authenticate():
    pairing_code = get_pairing_code()
    print('Please visit https://bitpay.com/api-access-request?pairingCode=%s' % pairing_code)
    print('and approve that API Token.')


def generate_invoice(amount, description):
    """
    Generate a BitPay invoice.

    If the amount is below 5 then the transaction speed "high" is used.
    Otherwise, the "medium" speed is used.

    """
    data = {
        'price': amount,
        'currency': CURRENCY,
        'transactionSpeed': 'high' if amount <= 5 else 'medium',
        'notificationEmail': NOTIFICATION_EMAIL,
        'redirectUrl': REDIRECT_URL,
        'itemDesc': description,
        'physical': True,
        'buyerName': BUYER_NAME,
        'buyerCity': BUYER_CITY,
        'buyerZip': BUYER_ZIP,
        'buyerCountry': BUYER_COUNTRY,
    }
    response = requests.post('https://bitpay.com/invoices', json=data)
    print(response.json())


if __name__ == '__main__':
    args = parse_args(sys.argv)
    authenticate()
    #generate_invoice(args['amount'], 'Beerpay Test')
