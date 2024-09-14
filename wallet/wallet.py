import hashlib
from ecdsa import SigningKey, SECP256k1
import base58
from mnemonic import Mnemonic
import logging
import requests
import json
import os

# Configure the logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create a logger instance
blockchain_logger = logging.getLogger('blockchain')

import requests

class Wallet:
    def __init__(self):
        response = requests.get('http://localhost:5000/wallet/new')
        if response.status_code == 201:
            data = response.json()

            self.address = data['address']
            self.public_key = data['public_key']
            self.seed_phrase = data['seed_phrase']
            self.private_key = self.generate_private_key(self.seed_phrase)

            self.balance = 0
        else:
            raise Exception("Failed to create new wallet")

    def generate_private_key(self, seed_phrase):
        mnemo = Mnemonic("english")
        seed = mnemo.to_seed(seed_phrase)
        return SigningKey.from_string(seed[:32], curve=SECP256k1)

    @staticmethod
    def generate_address(public_key):
        return hashlib.sha256(public_key.encode()).hexdigest()[:34]

    @classmethod
    def from_seed_phrase(cls, address, seed_phrase):
        response = requests.get('http://localhost:5000/wallet/import', json={'address': address, 'seed_phrase': seed_phrase})

        if response.status_code == 200:
            data = response.json()
            wallet = cls.__new__(cls)
            wallet.address = data['address']
            wallet.public_key = data['public_key']
            wallet.seed_phrase = seed_phrase
            wallet.private_key = wallet.generate_private_key(seed_phrase)
            wallet.balance = data['balance']
            return wallet
        else:
            return None

    def send_transaction(self, recipient, amount):
      message = f"{self.address}{recipient}{amount}".encode()
      signature = self.private_key.sign(message)
      
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
         # close file
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
                  wallet = Wallet.from_seed_phrase(data['address'], data['seed_phrase'])
                  if not wallet:
                     Wallet.delete_wallet_local_data(f)
                     return None
                  return wallet
               else:
                  Wallet.delete_wallet_local_data(f)
                  return None
      except FileNotFoundError:
         return None