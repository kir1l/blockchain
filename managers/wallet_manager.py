import hashlib
import json
from cryptography.hazmat.primitives.asymmetric import ec, padding
from cryptography.hazmat.primitives import hashes, serialization

class WalletManager:
    def __init__(self, blockchain):
        self.blockchain = blockchain

    def create_wallet(self, address, public_key_pem):
        public_key = serialization.load_pem_public_key(public_key_pem.encode())
        return {
            'address': address,
            'public_key': public_key_pem
        }

    def get_public_key(self, address):
        for block in self.blockchain.get_chain():
            for transaction in block['transactions']:
                if transaction['recipient'] == address:
                    return serialization.load_pem_public_key(transaction['public_key'].encode())
        raise ValueError(f"Wallet with address {address} not found")

    def sign_transaction(self, private_key, transaction):
        transaction_bytes = json.dumps(transaction, sort_keys=True).encode('utf-8')
        signature = private_key.sign(
            transaction_bytes,
            ec.ECDSA(hashes.SHA256())
        )
        return signature

    def get_balance(self, wallet_address):
        balance = 0
        for block in self.blockchain.get_chain():
            for transaction in block['transactions']:
                if transaction['sender'] == wallet_address:
                    balance -= transaction['amount']
                if transaction['recipient'] == wallet_address:
                    balance += transaction['amount']
        return balance
    
    def find_wallet(self, address):
        for block in self.blockchain.get_chain():
            for transaction in block['transactions']:
                if transaction['sender'] == address or transaction['recipient'] == address:
                    return True
        return False
