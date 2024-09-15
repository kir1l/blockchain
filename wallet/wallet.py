import hashlib
from ecdsa import SigningKey, SECP256k1
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
        # Генерация сид фразы
        mnemo = Mnemonic("english")
        seed_phrase = mnemo.generate(strength=128)
        seed = mnemo.to_seed(seed_phrase)

        # Генерация ключей
        private_key = SigningKey.from_string(seed[:32], curve=SECP256k1)
        public_key = private_key.get_verifying_key()

        # Генерация адреса
        address = hashlib.sha256(public_key.to_string()).hexdigest()[:34]

        # Сериализация публичного ключа в PEM-формат
        public_key_pem = public_key.to_pem().decode()

        # Отправка публичного ключа и адреса на сервер
        response = requests.post('http://localhost:5000/wallet/new', json={
            'address': address,
            'public_key': public_key_pem
        })

        if response.status_code == 201:
            return cls(address, public_key_pem, seed_phrase, private_key.to_string().hex())
        else:
            raise Exception("Failed to create wallet on server")

    @classmethod
    def from_seed_phrase(cls, seed_phrase):
        # Генерация ключей на основе сид фразы
        mnemo = Mnemonic("english")
        seed = mnemo.to_seed(seed_phrase)
        private_key = SigningKey.from_string(seed[:32], curve=SECP256k1)
        public_key = private_key.get_verifying_key()
        address = hashlib.sha256(public_key.to_string()).hexdigest()[:34]
        public_key_pem = public_key.to_pem().decode()

        # Проверка существования кошелька на сервере
        if cls.find_wallet(address):
            return cls(address, public_key_pem, seed_phrase, private_key.to_string().hex())
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
        message = f"{self.address}{recipient}{amount}".encode()
        private_key = SigningKey.from_string(bytes.fromhex(self.private_key), curve=SECP256k1)
        signature = private_key.sign(message)

        response = requests.post('http://localhost:5000/transactions/new', json={
            'sender': self.address,
            'recipient': recipient,
            'amount': amount,
            'signature': signature.hex()
        })

        if response.status_code == 201:
            return True
        else:
            return False

    def get_balance(self):
        response = requests.get('http://localhost:5000/chain')
        if response.status_code == 200:
            chain = response.json()['chain']
            balance = 0
            for block in chain:
                for transaction in block['transactions']:
                    if transaction['sender'] == self.address:
                        balance -= transaction['amount']
                    if transaction['recipient'] == self.address:
                        balance += transaction['amount']
            self.balance = balance
            return self.balance
        else:
            raise Exception("Failed to get balance")

    def save_wallet_local_data(self):
        data = {
            'address': self.address,
            'public_key': self.public_key,
            'seed_phrase': self.seed_phrase
        }
        try:
            with open('wallet_data.json', 'w') as f:
                json.dump(data, f, indent=4)
        except IOError as e:
            print(f"Error saving wallet data: {e}")
            print(f"Current working directory: {os.getcwd()}")
            print(f"Attempting to save in user's home directory...")
            home_dir = os.path.expanduser("~")
            file_path = os.path.join(home_dir, 'wallet_data.json')
            try:
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=4)
                print(f"Wallet data saved successfully in {file_path}")
            except IOError as e:
                print(f"Error saving wallet data in home directory: {e}")
                print("Please check file permissions and try again.")

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
