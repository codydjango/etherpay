import requests
from math import floor
from flask import Flask, jsonify, request

app = Flask(__name__)


def round_down(n, d=8):
    d = int('1' + ('0' * d))
    return floor(n * d) / d


@app.route('/convert')
def convert():
    original_amount = request.args.get('amount')
    currency = request.args.get('currency', 'usd')
    currency = currency.lower()

    r = requests.get('https://api.coinmarketcap.com/v1/ticker/ethereum/?convert={0}'.format(currency))
    json = r.json()
    data = json[0]
    ether_price = data['price_{0}'.format(currency)]
    conversion_rate = round_down(float(ether_price) / float(1), 9)
    amount_in_ether = round_down(float(original_amount) / conversion_rate, 9)

    response = jsonify({
        "status": "success",
        "payload": {
            "originalAmount": str(original_amount),
            "originalCurrency": str(currency),
            "etherPrice": str(ether_price),
            "amountInEther": str(amount_in_ether),
        }
    })

    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


@app.route('/contracts')
def contracts():
    import json, os, fnmatch

    contract_dir = os.path.join(os.path.dirname(__file__), 'build', 'contracts')
    all_contracts = os.listdir(contract_dir)
    contracts = {}
    for entry in all_contracts:
        if entry.endswith('json'):
            contract_name = os.path.splitext(entry)[0]
            truffle_file = json.load(open(os.path.join(contract_dir, entry)))
            contracts[contract_name] = {}
            contracts[contract_name]['abi'] = truffle_file['abi']
            contracts[contract_name]['bytecode'] = truffle_file['bytecode']

    response = jsonify(contracts)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port='8080')
