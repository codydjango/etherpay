from settings import INFURA_PROJECT_ID
from web3.auto.infura import w3
import os

os.environ['INFURA_API_KEY'] = INFURA_PROJECT_ID

connected = w3.isConnected()

if connected:
	print(w3.version.node)
else:
	print('not auto connected')

# if connected and w3.version.node.startswith('Parity'):
#     enode = w3.parity.enode

# elif connected and w3.version.node.startswith('Geth'):
#     enode = w3.admin.nodeInfo['enode']

# else:
#     enode = None



# print(w3.eth.blockNumber)