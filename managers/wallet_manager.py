import hashlib
import json
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization

class WalletManager:
    def __init__(self):
        self.wallets = {}

    def create_wallet(self):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        public_key = private_key.public_key()
        
        wallet_address = hashlib.sha256(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        ).hexdigest()

        self.wallets[wallet_address] = {
            'private_key': private_key,
            'public_key': public_key,
            'balance': 0
        }
        
        return wallet_address

    def get_balance(self, wallet_address):
        return self.wallets[wallet_address]['balance']

    def update_balance(self, wallet_address, amount):
        self.wallets[wallet_address]['balance'] += amount

    def sign_transaction(self, wallet_address, transaction):
        private_key = self.wallets[wallet_address]['private_key']
        transaction_bytes = json.dumps(transaction, sort_keys=True).encode('utf-8')
        signature = private_key.sign(
            transaction_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature
