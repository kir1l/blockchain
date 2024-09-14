import hashlib
import json
from time import time
import requests
from urllib.parse import urlparse

# Cryptography
from mnemonic import Mnemonic
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from ecdsa import SigningKey, VerifyingKey, SECP256k1

from logger import blockchain_logger

class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.nodes = set()
        self.new_block(previous_hash='1', proof=100)
        blockchain_logger.info("Blockchain initialized")

    def valid_chain(self, chain):
        last_block = chain[0]
        for block in chain[1:]:
            if block['previous_hash'] != self.hash(last_block):
                return False
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False
            last_block = block
        return True

    def resolve_conflicts(self):
        new_chain = None
        max_length = len(self.chain)

        for node in self.nodes:
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True
        return False

    def register_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
        blockchain_logger.info(f"New node registered: {address}")
   
    def new_block(self, proof, previous_hash=None):
        block = Block(
            index=len(self.chain) + 1,
            transactions=self.current_transactions,
            proof=proof,
            previous_hash=previous_hash or self.hash(self.chain[-1])
        )

        self.process_transactions(block)
        self.chain.append(block)
        return block
   
    def new_transaction(self, sender, recipient, amount, signature):
        sender_wallet = self.find_wallet(sender)
        if not sender_wallet or not self.verify_signature(sender_wallet, sender, recipient, amount, signature):
            blockchain_logger.info(f"Transaction failed: {sender} -> {recipient} ({amount}). Invalid signature.")
            return False
        
        if self.get_balance(sender) < amount:
            blockchain_logger.info(f"Transaction failed: {sender} -> {recipient} ({amount}). Insufficient funds.")
            return False
        
        self.current_transactions.append({
            'type': 'transaction',
            'data': {
                'sender': sender,
                'recipient': recipient,
                'amount': amount,
                'signature': signature.hex()
            }
        })

        self.new_block(proof=100)

        blockchain_logger.info(f"New transaction added: {self.current_transactions[-1]}")
        return True

    def verify_signature(self, sender_wallet, sender, recipient, amount, signature):
      public_key = VerifyingKey.from_string(bytes.fromhex(sender_wallet['public_key']), curve=SECP256k1)
      message = f"{sender}{recipient}{amount}".encode()
      return public_key.verify(signature, message)

    def get_balance(self, address):
        balance = 0
        # Find wallet and get balance if no transactions found
        wallet_data = self.find_wallet(address)
        if wallet_data:
            balance = wallet_data['balance']

        for block in self.chain:
            for transaction in block.transactions:
                if transaction['type'] == 'transaction':
                    if transaction['data']['recipient'] == address:
                        balance += transaction['data']['amount']
                    if transaction['data']['sender'] == address:
                        balance -= transaction['data']['amount']

        if balance != 0:
            return balance

        # Find wallet and get balance if no transactions found
        wallet_data = self.find_wallet(address)
        if wallet_data:
            return wallet_data['balance']

        return 0

    def create_wallet(self): 
        mnemo = Mnemonic("english")
        seed_phrase = mnemo.generate(strength=128)
        seed = mnemo.to_seed(seed_phrase)
        private_key = SigningKey.from_string(seed[:32], curve=SECP256k1)
        public_key = private_key.get_verifying_key()
        address = self.generate_address(public_key.to_string().hex())
        
        self.current_transactions.append({
            'type': 'wallet',
            'data': {
                'address': address,
                'public_key': public_key.to_string().hex(),
                'balance': 100
            }
        })
        
        self.new_block(proof=100)
        return {
            'address': address,
            'public_key': public_key.to_string().hex(),
            'seed_phrase': seed_phrase
        }

    def generate_key_from_seed(self, seed_phrase):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'fixed_salt',
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(seed_phrase.encode()))
        return key

    def encrypt_data(self, data, key):
        f = Fernet(key)
        return f.encrypt(data.encode())

    def decrypt_data(self, encrypted_data, seed_phrase):
        key = self.generate_key_from_seed(seed_phrase)
        f = Fernet(key)
        return f.decrypt(encrypted_data).decode()

    @staticmethod
    def generate_address(public_key):
        return hashlib.sha256(public_key.encode()).hexdigest()[:34]

    def generate_seed_phrase(self):
        mnemo = Mnemonic("english")
        return mnemo.generate(strength=128)

    def decrypt_wallet(self, address, seed_phrase):
        mnemo = Mnemonic("english")
        seed = mnemo.to_seed(seed_phrase)
        private_key = SigningKey.from_string(seed[:32], curve=SECP256k1)
        public_key = private_key.get_verifying_key()
        generated_address = self.generate_address(public_key.to_string().hex())
        
        if generated_address != address:
            return None
        
        wallet_data = self.find_wallet(address)
        if wallet_data:
            return {
                'address': address,
                'public_key': public_key.to_string().hex(),
                'balance': self.get_balance(address)
            }
        return None

    def find_wallet(self, address):
        for block in self.chain:
            for transaction in block.transactions:
                if transaction['type'] == 'wallet' and transaction['data']['address'] == address:
                    blockchain_logger.info(f"Found wallet address: {address}")
                    return transaction['data']
        blockchain_logger.info(f"No wallet found with address: {address}")
        return None
    
    def process_transactions(self, block):
        for transaction in self.current_transactions:
            if transaction['type'] == 'wallet':
                block.add_wallet(transaction['data']['address'], transaction['data']['public_key'], transaction['data']['balance'])
            elif transaction['type'] == 'transaction':
                sender_balance = block.get_wallet_balance(transaction['data']['sender'])
                if sender_balance >= transaction['data']['amount']:
                    block.update_wallet_balance(transaction['data']['sender'], -transaction['data']['amount'])
                    block.update_wallet_balance(transaction['data']['recipient'], transaction['data']['amount'])
                    blockchain_logger.info(f"Transaction processed: {transaction['data']['amount']} from {transaction['data']['sender']} to {transaction['data']['recipient']}")
                else:
                    blockchain_logger.warning(f"Transaction failed: Insufficient balance for sender {transaction['data']['sender']}")
        self.current_transactions = []

    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        blockchain_logger.info(f"Proof of work found: {proof}")
        return proof

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    @staticmethod
    def hash(block):
        block_string = json.dumps(block.to_dict(), sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()
   
    @property
    def last_block(self):
        return self.chain[-1]

class Block:
    def __init__(self, index, transactions, proof, previous_hash):
        self.index = index
        self.timestamp = time()
        self.transactions = transactions
        self.proof = proof
        self.previous_hash = previous_hash
        self.wallets = {}

    def to_dict(self):
        return {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': self.transactions,
            'proof': self.proof,
            'previous_hash': self.previous_hash,
        }

    def add_wallet(self, address, public_key, initial_balance=0):
        self.wallets[address] = {'public_key': public_key, 'balance': initial_balance}

    def get_wallet_balance(self, address):
        if address in self.wallets:
            return self.wallets[address]['balance']
        blockchain_logger.warning(f"Attempted to get balance for non-existent wallet: {address}")
        return 0

    def update_wallet_balance(self, address, amount):
        if address in self.wallets:
            self.wallets[address]['balance'] += amount
            blockchain_logger.info(f"Wallet balance updated for {address}: new balance {self.wallets[address]['balance']}")
        else:
            blockchain_logger.warning(f"Attempted to update balance for non-existent wallet: {address}")