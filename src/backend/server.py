import requests
import asyncio
import json
import random
import threading

from time import sleep
from math import floor
from flask import Flask, jsonify, request

from web3 import Web3

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
app = Flask(__name__)

CONTRACT_ADDRESS = Web3.toChecksumAddress('0x14094ca0f2f8a6bf0ad82aecca9ce0c2f5a406f8')
CONTRACT_ABI = json.loads("""[
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
]""")

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


def get_order_by_id(order_id):
    for order in ORDERS:
        if str(order['id']) == str(order_id):
            return order
    else:
        raise Exception('Order id "{0}" not found'.format(order_id))


def handle_event(event):
    # AttributeDict({
    #     'args': AttributeDict({
    #         'orderId': 2,
    #         'value': 189353117000000000,
    #         'sender': '0x9e255d6e6Fc04F6606E1E601835dbaB764A6E447'
    #     }),
    #     'event': 'Paid',
    #     'logIndex': 0,
    #     'transactionIndex': 0,
    #     'transactionHash': HexBytes('0x225d3aa5de80409bbec89a2ea0bddca3c3cabd3ec2200dc8f302d8519b663a25'),
    #     'address': '0x14094cA0f2f8A6BF0AD82AEccA9Ce0c2F5a406f8',
    #     'blockHash': HexBytes('0x16693c5ec269e9bdde63b9777ea111ef676443cc787ff9be576c6a135a2f77e2'),
    #     'blockNumber': 2
    # })

    if event.event == 'Paid':
        order_id = int(event.args.orderId)
        wei = str(event.args.value)
        sender = str(event.args.sender)
        transaction_hash = str(event.transactionHash.hex())
        block_number = str(event.blockNumber)
        order = get_order_by_id(order_id)

        if order['paid'] == False:
            order['wei'] = wei
            order['sender'] = sender
            order['transacton_hash'] = transaction_hash
            order['paid'] = True
            order['block_number'] = block_number


async def log_loop(event_filter, poll_interval):
    while True:
        for event in event_filter.get_new_entries():
            handle_event(event)

        await asyncio.sleep(poll_interval)


def watch(contract):
    sleep(5)

    asyncio.set_event_loop(asyncio.new_event_loop())
    paid_filter = contract.events.Paid.createFilter(fromBlock='latest')
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(asyncio.gather(log_loop(paid_filter, 2)))
    except Exception as e:
        print('exception', e)
    finally:
        loop.close()


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
            'abi': CONTRACT_ABI,
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


@app.route('/order/<order_id>', methods=['GET'])
def order_by_id(order_id):
    response = jsonify({
        'status': 'success',
        'payload': get_order_by_id(order_id)
    })

    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


if __name__ == '__main__':
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

    t = threading.Thread(target=watch, args=(contract,), daemon=True)
    t.start()

    app.run(debug=True, host='127.0.0.1', port='8080')

