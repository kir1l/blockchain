import hashlib
from cryptography.hazmat.primitives import serialization

class WalletManager:
    def __init__(self):
        pass

    def create_wallet(self, address, public_key_pem):
        public_key = serialization.load_pem_public_key(public_key_pem.encode())
        return {
            'address': address,
            'public_key': public_key_pem
        }

    def get_public_key(self, public_key_pem):
        return serialization.load_pem_public_key(public_key_pem.encode())
