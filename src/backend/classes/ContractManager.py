
import asyncio
import threading

from time import sleep
from web3 import Web3, HTTPProvider

w3 = Web3(HTTPProvider('http://127.0.0.1:7545'))

async def log_loop(event_filter, poll_interval, on_paid):
    while True:
        for event in event_filter.get_new_entries():
            on_paid(order_id=int(event.args.orderId),
                    wei=str(event.args.value),
                    sender=str(event.args.sender),
                    transaction_hash=str(event.transactionHash.hex()),
                    block_number=str(event.blockNumber))
        await asyncio.sleep(poll_interval)

def monitor(contract, on_paid):
    sleep(5)
    asyncio.set_event_loop(asyncio.new_event_loop())
    paid_filter = contract.events.Paid.createFilter(fromBlock='latest')
    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(asyncio.gather(log_loop(paid_filter, 2, on_paid)))
    except Exception as e:
        print('exception', e)
    finally:
        loop.close()

class ContractManager:
    def __init__(self):
        self._contract = None
        self._contract_address = None
        self._watching = False


    def update(self, **kwargs):
        self._abi = kwargs.get('abi', None)
        self._bytecode = kwargs.get('bytecode', None)
        self._contract_address = kwargs.get('address', None)

        if self._bytecode:
            self._contract = w3.eth.contract(abi=self._abi, bytecode=self._bytecode)
        elif self._contract_address:
            self._contract = w3.eth.contract(abi=self._abi, address=self._contract_address)

    def deploy(self, private_key):
        account = w3.eth.account.privateKeyToAccount(private_key)

        tx = self._contract.constructor().buildTransaction({
            'from': account.address,
            'nonce': w3.eth.getTransactionCount(account.address),
            'gas': 1728712,
            'gasPrice': w3.toWei('21', 'gwei')
        })

        signed = account.signTransaction(tx)
        tx_hash = w3.eth.sendRawTransaction(signed.rawTransaction)
        receipt = None

        i = 0
        while receipt == None and i < 60:
            print('attempt at deploying contract: ', i)

            receipt = w3.eth.getTransactionReceipt(tx_hash)
            sleep(1)
            i += 1

        if receipt == None:
            raise Exception('exceeded time limit')

        transaction_hash = receipt.transactionHash.hex()
        contract_address = Web3.toChecksumAddress(receipt.contractAddress)
        block_number = receipt.blockNumber

        self._receipt = {
            'transaction_hash': transaction_hash,
            'contract_address': contract_address,
            'block_number': block_number
        }

        print('receipt', self._receipt)

        self._contract_address = contract_address

        return contract_address

    def on_paid(self, fn):
        if not self._watching:
            self._watching = True
            t = threading.Thread(target=monitor, args=(self._contract, fn), daemon=True)
            t.start()

    def get_deployed_contract_address(self):
        return self._contract_address

    def get_abi(self):
        return self._abi

