import requests
import asyncio
import json
import random

from math import floor
from flask import Flask, jsonify, request

from web3.auto import w3

CONTRACT_ADDRESS = "0x4f33a6338ad3c1b1a211f0026d543af29a89c85d"
CONTRACT_ABI = """[
	{
		"constant": false,
		"inputs": [],
		"name": "destroy",
		"outputs": [
			{
				"name": "",
				"type": "bool"
			}
		],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [
			{
				"name": "orderId",
				"type": "uint256"
			}
		],
		"name": "pay",
		"outputs": [
			{
				"name": "",
				"type": "bool"
			}
		],
		"payable": true,
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [
			{
				"name": "orderId",
				"type": "uint256"
			}
		],
		"name": "refund",
		"outputs": [
			{
				"name": "",
				"type": "bool"
			}
		],
		"payable": true,
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [],
		"name": "renounceOwnership",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [
			{
				"name": "newOwner",
				"type": "address"
			}
		],
		"name": "transferOwnership",
		"outputs": [],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"constant": false,
		"inputs": [],
		"name": "withdraw",
		"outputs": [
			{
				"name": "",
				"type": "bool"
			}
		],
		"payable": false,
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"name": "orderId",
				"type": "uint256"
			},
			{
				"indexed": true,
				"name": "value",
				"type": "uint256"
			},
			{
				"indexed": true,
				"name": "sender",
				"type": "address"
			}
		],
		"name": "Paid",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"name": "orderId",
				"type": "uint256"
			},
			{
				"indexed": true,
				"name": "value",
				"type": "uint256"
			},
			{
				"indexed": true,
				"name": "sender",
				"type": "address"
			}
		],
		"name": "Refunded",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": true,
				"name": "previousOwner",
				"type": "address"
			},
			{
				"indexed": true,
				"name": "newOwner",
				"type": "address"
			}
		],
		"name": "OwnershipTransferred",
		"type": "event"
	},
	{
		"constant": true,
		"inputs": [],
		"name": "getBalance",
		"outputs": [
			{
				"name": "",
				"type": "uint256"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [
			{
				"name": "orderId",
				"type": "uint256"
			}
		],
		"name": "getInvoice",
		"outputs": [
			{
				"name": "",
				"type": "uint256"
			},
			{
				"name": "",
				"type": "bool"
			},
			{
				"name": "",
				"type": "bool"
			},
			{
				"name": "",
				"type": "address"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [
			{
				"name": "",
				"type": "uint256"
			}
		],
		"name": "invoices",
		"outputs": [
			{
				"name": "paid",
				"type": "bool"
			},
			{
				"name": "amount",
				"type": "uint256"
			},
			{
				"name": "from",
				"type": "address"
			},
			{
				"name": "refund",
				"type": "bool"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [],
		"name": "isOwner",
		"outputs": [
			{
				"name": "",
				"type": "bool"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	},
	{
		"constant": true,
		"inputs": [],
		"name": "owner",
		"outputs": [
			{
				"name": "",
				"type": "address"
			}
		],
		"payable": false,
		"stateMutability": "view",
		"type": "function"
	}
]"""



ORDERS = []

def get_next_order_id():
    try:
        currentOrder = ORDERS[-1]['id']
        return currentOrder + 1
    except IndexError:
        return 1

def create_order():
    order = {
        'amount': '{0}.00'.format(random.randrange(10, 200)),
        'currency': random.choice(['CAD', 'USD', 'EUR']),
        'id': get_next_order_id(),
        'paid': False,
    }

    ORDERS.append(order)
    return order

def getOrderById(id):
    for order in ORDERS:
        if order['id'] == id:
            return order
    else:
        raise Exception('not found')


# def handle_event(event):
#     print(event)
#     # and whatever

# async def log_loop(event_filter, poll_interval):
#     while True:
#         for event in event_filter.get_new_entries():
#             handle_event(event)
#         await asyncio.sleep(poll_interval)

# def watch():
#     block_filter = w3.eth.filter('latest')
#     tx_filter = w3.eth.filter('pending')
#     loop = asyncio.get_event_loop()
#     try:
#         loop.run_until_complete(
#             asyncio.gather(
#                 log_loop(block_filter, 2),
#                 log_loop(tx_filter, 2)))
#     finally:
#         loop.close()




app = Flask(__name__)


def round_down(n, d=8):
    d = int('1' + ('0' * d))
    return floor(n * d) / d


@app.route('/convert', methods=['GET'])
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
        'status': 'success',
        'payload': {
            'originalAmount': str(original_amount),
            'originalCurrency': str(currency),
            'etherPrice': '{:.2f}'.format(float(ether_price)),
            'amountInEther': str(amount_in_ether),
        }
    })

    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


@app.route('/contract', methods=['GET'])
def contract():
    response = jsonify({
        'status': 'success',
        'payload': {
            'abi': json.loads(CONTRACT_ABI),
            'address': CONTRACT_ADDRESS
        }
    })

    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/order', methods=['GET'])
def order():
    order = create_order()

    response = jsonify({
        'status': 'success',
        'payload': order
    })

    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/order/<id>', methods=['GET'])
def orderById(orderId):
    order = getOrderById(orderId)

    response = jsonify({
        'status': 'success',
        'payload': order
    })

    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port='8080')
    # watch()
