from flask import Flask, jsonify, request
from uuid import uuid4
from blockchain import Blockchain
from logger import blockchain_logger

class BlockchainAPI:
    def __init__(self):
        self.app = Flask(__name__)
        self.node_identifier = str(uuid4()).replace('-', '')
        self.blockchain = Blockchain()
        self.setup_routes()

    def setup_routes(self):
        self.app.route('/wallet/new', methods=['GET'])(self.new_wallet)
        self.app.route('/wallet/check', methods=['GET'])(self.check_address)
        self.app.route('/wallet/import', methods=['GET'])(self.import_wallet)
        self.app.route('/wallet/balance', methods=['GET'])(self.get_balance)
        self.app.route('/mine', methods=['GET'])(self.mine)
        self.app.route('/chain', methods=['GET'])(self.full_chain)
        self.app.route('/transactions/new', methods=['POST'])(self.new_transaction)
        self.app.route('/nodes/register', methods=['POST'])(self.register_nodes)
        self.app.route('/nodes/resolve', methods=['GET'])(self.consensus)

    def new_wallet(self):
        wallet_data = self.blockchain.create_wallet()
        blockchain_logger.info(f"Created new wallet with address: {wallet_data['address']}")
        return jsonify(wallet_data), 201

    def check_address(self):
        address = request.args.get('address')
        if address:
            wallet = self.blockchain.find_wallet(address)
            if wallet:
                blockchain_logger.info(f"Address {address} exists")
                return jsonify(True), 200
            else:
                blockchain_logger.info(f"Address {address} does not exist")
                return jsonify(False), 200

    def import_wallet(self):
        values = request.get_json()
        seed_phrase = values.get('seed_phrase')
        address = values.get('address')

        if not seed_phrase or not address:
            blockchain_logger.warning(f"Attempt to import wallet with missing seed phrase or address")
            return 'Missing seed phrase or address', 400

        wallet_data = self.blockchain.decrypt_wallet(address, seed_phrase)

        if wallet_data:
            blockchain_logger.info(f"Imported wallet with address: {address}")
            return jsonify(wallet_data), 200
        else:
            blockchain_logger.error(f"Failed to import wallet with address: {address}")
            return 'Wallet not found or incorrect seed phrase', 400

    def get_balance(self):
        values = request.args
        if 'address' not in values:
            return 'Missing address', 400

        balance = self.blockchain.get_balance(values['address'])

        if balance is None:
            blockchain_logger.error(f"Failed to get balance for address: {values['address']}")
            return 'Wallet not found', 400
        
        blockchain_logger.info(f"Balance for address {values['address']} checked")
        return jsonify({'balance': balance}), 200

    def mine(self):
        last_block = self.blockchain.last_block
        last_proof = last_block['proof']
        proof = self.blockchain.proof_of_work(last_proof)

        self.blockchain.new_transaction(
            sender="0",
            recipient=self.node_identifier,
            amount=1,
        )

        previous_hash = self.blockchain.hash(last_block)
        block = self.blockchain.new_block(proof, previous_hash)

        response = {
            'message': "New Block Forged",
            'index': block.index,
            'transactions': block.transactions,
            'proof': block.proof,
            'previous_hash': block.previous_hash,
        }

        blockchain_logger.info(f"Block mined: {block.index}")
        return jsonify(response), 200

    def full_chain(self):
        response = {
            'chain': [block for block in self.blockchain.chain],
            'length': len(self.blockchain.chain),
        }
        return jsonify(response), 200

    def new_transaction(self):
        values = request.get_json()
        required = ['sender', 'recipient', 'amount', 'signature']
        if not all(k in values for k in required):
            return 'Missing values', 400

        if not self.blockchain.find_wallet(values['sender']):
            return 'Sender not found', 400

        signature = bytes.fromhex(values['signature'])
        success = self.blockchain.new_transaction(values['sender'], values['recipient'], values['amount'], signature)

        if success:
            response = {'message': 'Transaction will be added to the next block'}
            blockchain_logger.info(f"New transaction added: {values['sender']} -> {values['recipient']} ({values['amount']})")
            return jsonify(response), 201
        else:
            return 'Invalid transaction', 400

    def register_nodes(self):
        values = request.get_json()

        nodes = values.get('nodes')
        if nodes is None:
            return "Error: Please supply a valid list of nodes", 400

        for node in nodes:
            self.blockchain.register_node(node)

        response = {
            'message': 'New nodes have been added',
            'total_nodes': list(self.blockchain.nodes),
        }

        blockchain_logger.info(f"New nodes registered: {nodes}")
        return jsonify(response), 201

    def consensus(self):
        replaced = self.blockchain.resolve_conflicts()

        if replaced:
            response = {
                'message': 'Our chain was replaced',
                'new_chain': self.blockchain.chain
            }
        else:
            response = {
                'message': 'Our chain is authoritative',
                'chain': self.blockchain.chain
            }
        
        blockchain_logger.info("Consensus algorithm executed")
        return jsonify(response), 200

    def run(self, host='0.0.0.0', port=5000):
        self.app.run(host=host, port=port)

