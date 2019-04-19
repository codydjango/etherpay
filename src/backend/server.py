import requests
import json
import os

from math import floor
from flask import Flask, jsonify, request
from web3 import Web3

from settings import CONTRACT_ABI, CONTRACT_BYTECODE, PRIVATE_KEY
from classes import OrderManager, ContractManager

app = Flask(__name__)
order_manager = OrderManager()
contract_manager = ContractManager()

@app.route('/convert', methods=['GET'])
def convert():

    # Helper method
    def round_down(n, d=8):
        d = int('1' + ('0' * d))
        return floor(n * d) / d


    original_amount = request.args.get('amount')
    currency = request.args.get('currency', 'usd')
    currency = currency.lower()

    r = requests.get('https://api.coinmarketcap.com/v1/ticker/ethereum/?convert={0}'.format(currency))
    json = r.json()
    data = json[0]
    ether_price = data['price_{0}'.format(currency)]
    conversion_rate = round_down(float(ether_price) / float(1), 9)
    amount_in_ether = round_down(float(original_amount) / conversion_rate, 9)
    amount_in_wei = Web3.toWei(amount_in_ether, 'ether')

    response = jsonify({
        'status': 'success',
        'payload': {
            'originalAmount': str(original_amount),
            'originalCurrency': str(currency),
            'etherPrice': '{:.2f}'.format(float(ether_price)),
            'amountInEther': str(amount_in_ether),
            'amountInWei': str(amount_in_wei)
        }
    })

    response.headers['Access-Control-Allow-Origin'] = '*'

    return response


@app.route('/contract', methods=['GET'])
def contract():
    response = jsonify({
        'status': 'success',
        'payload': {
            'abi':  contract_manager.get_abi(),
            'address': contract_manager.get_deployed_contract_address()
        }
    })

    response.headers['Access-Control-Allow-Origin'] = '*'

    return response


@app.route('/order', methods=['GET'])
def order():
    response = jsonify({
        'status': 'success',
        'payload': order_manager.create()
    })

    response.headers['Access-Control-Allow-Origin'] = '*'

    return response


@app.route('/order/<order_id>', methods=['GET'])
def order_by_id(order_id):
    response = jsonify({
        'status': 'success',
        'payload': order_manager.get_by_id(order_id)
    })

    response.headers['Access-Control-Allow-Origin'] = '*'

    return response


def on_paid_callback(**kwargs):
        order = order_manager.get_by_id(kwargs.get('order_id'))

        # check it hasn't been paid already
        if order['paid'] == True:
            print('order has already been paid')
            return

        # check it has paid the right amount
        order['paid'] = True
        order['wei'] = kwargs.get('wei')
        order['sender'] = kwargs.get('sender')
        order['transaction_hash'] = kwargs.get('transaction_hash')
        order['block_number'] = kwargs.get('block_number')


if __name__ == '__main__':
    def monitor(address):
        contract_manager.update(abi=CONTRACT_ABI, address=address)
        contract_manager.on_paid(on_paid_callback)

    def deploy():
        contract_manager.update(abi=CONTRACT_ABI, bytecode=CONTRACT_BYTECODE['object'])
        contract_address = contract_manager.deploy(PRIVATE_KEY)

        return contract_address

    # testing
    contract_address = False
    contract_address = '0x299ed46DdF28a8080365a41223C013bD0082DFD3'

    if not contract_address:
        contract_address = deploy()

    monitor(contract_address)

    app.run(debug=True, host='127.0.0.1', port='8080')

