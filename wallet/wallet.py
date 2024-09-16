import hashlib
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from mnemonic import Mnemonic
import requests
import json
import os

class Wallet:
    def __init__(self, address, public_key, seed_phrase, private_key):
        self.address = address
        self.public_key = public_key
        self.seed_phrase = seed_phrase
        self.private_key = private_key
        self.balance = 0

    @classmethod
    def create_wallet(cls):
        # Генерация seed phrase
        mnemo = Mnemonic("english")
        seed_phrase = mnemo.generate(strength=128)
        seed = mnemo.to_seed(seed_phrase)

        # Генерация ключей на основе seed
        private_key = ec.derive_private_key(int.from_bytes(seed[:32], byteorder='big'), ec.SECP256R1())
        public_key = private_key.public_key()

        # Генерация адреса
        address = hashlib.sha256(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        ).hexdigest()[:34]

        # Сериализация публичного ключа в PEM-формат
        public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()

        # Отправка публичного ключа и адреса на сервер
        response = requests.post('http://localhost:5000/wallet/new', json={
            'address': address,
            'public_key': public_key_pem
        })

        if response.status_code == 201:
            return cls(address, public_key_pem, seed_phrase, private_key)
        else:
            raise Exception("Failed to create wallet on server")

    @classmethod
    def from_seed_phrase(cls, seed_phrase):
        # Генерация ключей на основе seed phrase
        mnemo = Mnemonic("english")
        seed = mnemo.to_seed(seed_phrase)
        private_key = ec.derive_private_key(int.from_bytes(seed[:32], byteorder='big'), ec.SECP256R1())
        public_key = private_key.public_key()
        address = hashlib.sha256(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        ).hexdigest()[:34]
        public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()

        # Проверка существования кошелька на сервере
        if cls.find_wallet(address):
            return cls(address, public_key_pem, seed_phrase, private_key)
        else:
            return None

    @staticmethod
    def find_wallet(address):
        response = requests.get('http://localhost:5000/chain')
        if response.status_code == 200:
            chain = response.json()['chain']
            for block in chain:
                for transaction in block['transactions']:
                    if transaction['sender'] == address or transaction['recipient'] == address:
                        return True
        return False

    def send_transaction(self, recipient, amount):
        transaction = {
            'sender': self.address,
            'recipient': recipient,
            'amount': amount
        }
        transaction_bytes = json.dumps(transaction, sort_keys=True).encode('utf-8')
        signature = self.private_key.sign(
            transaction_bytes,
            ec.ECDSA(hashes.SHA256())
        )

        response = requests.post('http://localhost:5000/transactions/new', json={
            'sender': self.address,
            'recipient': recipient,
            'amount': amount,
            'signature': signature.hex(),
            'public_key': self.public_key
        })

        if response.status_code == 201:
            return True
        else:
            return False

    def get_balance(self):
        response = requests.get(f'http://localhost:5000/wallet/balance?address={self.address}')
        if response.status_code == 200:
            self.balance = response.json()['balance']
            return self.balance
        else:
            raise Exception("Failed to get balance")

    def save_wallet_local_data(self):
        data = {
            'address': self.address,
            'public_key': self.public_key,
            'seed_phrase': self.seed_phrase
        }
        with open('wallet_data.json', 'w') as f:
            json.dump(data, f)

    @staticmethod
    def delete_wallet_local_data(f=None):
        try:
            if not f:
                try:
                    os.remove('wallet_data.json')
                    return
                except:
                    return

            f.close()
            os.remove('wallet_data.json')
        except FileNotFoundError:
            pass

    @staticmethod
    def load_wallet_local_data():
        try:
            with open('wallet_data.json', 'r') as f:
                data = json.load(f)
                # Check data for validity
                if 'address' in data and 'seed_phrase' in data:
                    wallet = Wallet.from_seed_phrase(data['seed_phrase'])
                    if not wallet:
                        Wallet.delete_wallet_local_data(f)
                        return None
                    return wallet
                else:
                    Wallet.delete_wallet_local_data(f)
                    return None
        except FileNotFoundError:
            return None
