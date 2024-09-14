from flask import Flask, jsonify, request
from uuid import uuid4

from blockchain import Blockchain
from logger import blockchain_logger

app = Flask(__name__)
node_identifier = str(uuid4()).replace('-', '')
blockchain = Blockchain()


wallets = {}

@app.route('/wallet/new', methods=['GET'])
def new_wallet():
    wallet_data = blockchain.create_wallet()

    blockchain_logger.info(f"Created new wallet with address: {wallet_data['address']}")
    return jsonify(wallet_data), 201

# Endpoint for checking address existence
@app.route('/wallet/check', methods=['GET'])
def check_address():
    address = request.args.get('address')
    if address:
        wallet = blockchain.find_wallet(address)
        if wallet:
            blockchain_logger.info(f"Address {address} exists")
            return True, 200
        else:
            blockchain_logger.info(f"Address {address} does not exist")
            return False, 200


@app.route('/wallet/import', methods=['GET'])
def import_wallet():
    values = request.get_json()
    seed_phrase = values.get('seed_phrase')
    address = values.get('address')

    if not seed_phrase or not address:
        blockchain_logger.warning(f"Attempt to import wallet with missing seed phrase or address")
        return 'Missing seed phrase or address', 400

    wallet_data = blockchain.decrypt_wallet(address, seed_phrase)

    if wallet_data:
        blockchain_logger.info(f"Imported wallet with address: {address}")
        return jsonify(wallet_data), 200
    else:
        blockchain_logger.error(f"Failed to import wallet with address: {address}")
        return 'Wallet not found or incorrect seed phrase', 400

@app.route('/wallet/balance', methods=['GET'])
def get_balance():
    values = request.args
    if 'address' not in values:
        return 'Missing address', 400

    balance = blockchain.get_balance(values['address'])

    if balance is None:
        blockchain_logger.error(f"Failed to get balance for address: {values['address']}")
        return 'Wallet not found', 400
    
    blockchain_logger.info(f"Balance for address {values['address']} checked")
    return jsonify({'balance': balance}), 200

# Mine new block
@app.route('/mine', methods=['GET'])
def mine() -> dict:
   last_block = blockchain.last_block # get the last block from the chain
   last_proof = last_block['proof'] # get the proof of the last block
   proof = blockchain.proof_of_work(last_proof) # calculate the proof of work

   blockchain.new_transaction(
       sender="0",
       recipient=node_identifier,
       amount=1,
   )

   previous_hash = blockchain.hash(last_block)
   block = blockchain.new_block(proof, previous_hash)

   response = {
       'message': "New Block Forged",
       'index': block.index,
       'transactions': block.transactions,
       'proof': block.proof,
       'previous_hash': block.previous_hash,
   }

   blockchain_logger.info(f"Block mined: {block.index}")
   return jsonify(response), 200

@app.route('/chain', methods=['GET'])
def full_chain():
   response = {
       'chain': [block.to_dict() for block in blockchain.chain],
       'length': len(blockchain.chain),
   }
   return jsonify(response), 200

#  Create a new transaction
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    required = ['sender', 'recipient', 'amount', 'signature']
    if not all(k in values for k in required):
        return 'Missing values', 400

    if not blockchain.find_wallet(values['sender']):
        return 'Sender not found', 400

    signature = bytes.fromhex(values['signature'])
    success = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'], signature)

    if success:
        response = {'message': 'Transaction will be added to the next block'}
        blockchain_logger.info(f"New transaction added: {values['sender']} -> {values['recipient']} ({values['amount']})")
        return jsonify(response), 201
    else:
        return 'Invalid transaction', 400

# Register new nodes
@app.route('/nodes/register', methods=['POST'])
def register_nodes():
   values = request.get_json()

   nodes = values.get('nodes')
   if nodes is None:
       return "Error: Please supply a valid list of nodes", 400

   for node in nodes:
       blockchain.register_node(node)

   response = {
       'message': 'New nodes have been added',
       'total_nodes': list(blockchain.nodes),
   }

   blockchain_logger.info(f"New nodes registered: {nodes}")
   return jsonify(response), 201

# Resolve conflicts between nodes
@app.route('/nodes/resolve', methods=['GET'])
def consensus():
   replaced = blockchain.resolve_conflicts()

   if replaced:
      response = {
         'message': 'Our chain was replaced',
         'new_chain': blockchain.chain
      }
   else:
      response = {
         'message': 'Our chain is authoritative',
         'chain': blockchain.chain
      }
   
   blockchain_logger.info("Consensus algorithm executed")
   return jsonify(response), 200