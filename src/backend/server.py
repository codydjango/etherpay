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

# from web3.auto import w3

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

def get_order_by_id(id):
    for order in ORDERS:
        if order['id'] == id:
            return order
    else:
        raise Exception('not found')


def handle_event(event):
    print('event', event)
    print(type(event))
    print(dir(event))

    transaction_hash = event['transactionHash']

    print('transactionHash', transaction_hash)

    # receipt = w3.eth.waitForTransactionReceipt(event['transactionHash'])
    # result = contract.events.greeting.processReceipt(receipt)
    # print(result[0]['args'])
    # print('HANDLE THE EVENT JACKASS', event)


def handle_event_paid(event):
    print('paid', event)
    print(type(event))
    print(dir(event))

    transaction_hash = event.hex()
    # transaction_hash = event['transactionHash']

    print('transactionHash', transaction_hash)

    # receipt = w3.eth.waitForTransactionReceipt(event['transactionHash'])
    # result = contract.events.greeting.processReceipt(receipt)
    # print(result[0]['args'])

# async def log_loop(event_filter, poll_interval):
#     while True:
#         new_entries = event_filter.get_new_entries()
#         print('new entries', new_entries)

#         for event in new_entries:
#             handle_event(event)

#         await asyncio.sleep(poll_interval)

async def log_loop_paid(event_filter, poll_interval):
    print('log loop paid')
    while True:
        # new_entries = event_filter.get_new_entries()
        # print('new entries paid', new_entries)
        new_entries = event_filter.get_all_entries()
        print('new_entries', new_entries)
        for event in new_entries:
            handle_event_paid(event)

        await asyncio.sleep(poll_interval)

def watch(contract):
    asyncio.set_event_loop(asyncio.new_event_loop())

    # block_filter = w3.eth.filter('latest')
    # refunded_filter = contract.events.refunded.createFilter(fromBlock='latest')
    # paid_filter = contract.events.Paid.createFilter(fromBlock='latest')
    # paid_filter = w3.eth.filter({
    #     "address": contract.address,
    #     "from_block": "latest"
    # })

    # paid_filter = contract.events.Paid.createFilter(fromBlock='latest')
    # paid_filter = contract.events.Paid.createFilter(fromBlock=0)
    # contract.eventFilter('Paid', { 'toBlock': 'latest', })

    # paid_filter = contract.eventFilter('Paid', { 'fromBlock': 0, 'toBlock': 'latest' })
    # paid_filter2 = contract.events.Paid.createFilter(
    #     fromBlock='latest',
    #     toBlock='latest',
    #     argument_filters={}
    # )

    print('watch')
    paid_filter3 = contract.eventFilter('Paid', {'fromBlock': 0,'toBlock': 'latest'});

    # myfilter = mycontract.eventFilter('EventName', {'fromBlock': 0,'toBlock': 'latest'});
    # eventlist = myfilter.get_all_entries()



    # block_filter = w3.eth.filter('latest')

    # tx_filter = w3.eth.filter('pending')
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(
            asyncio.gather(
                # log_loop(block_filter, 2),
                # log_loop(tx_filter, 2),
                # log_loop_paid(paid_filter2, 2)
                log_loop_paid(paid_filter3, 2)
                # ,
                # log_loop_paid(paid_filter, 2)
            )
        )
    except Exception as e:
        print('exception', e)
    finally:
        loop.close()

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


@app.route('/order/<id>', methods=['GET'])
def orderById(orderId):
    order = get_order_by_id(orderId)

    response = jsonify({
        'status': 'success',
        'payload': order
    })

    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


if __name__ == '__main__':
    print('address', CONTRACT_ADDRESS)
    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

    worker = threading.Thread(target=watch, args=(contract,))
    # daemon=True
    worker.start()

    app.run(debug=True, host='127.0.0.1', port='8080')

