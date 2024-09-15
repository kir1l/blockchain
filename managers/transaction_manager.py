import json
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization

class TransactionManager:
    def __init__(self):
        self.pending_transactions = []

    def create_transaction(self, sender, recipient, amount, private_key=None):
        transaction = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        }
        if sender != "0" and private_key:  # Если это не транзакция создания кошелька
            signature = self.sign_transaction(private_key, transaction)
            transaction['signature'] = signature.hex()
        self.pending_transactions.append(transaction)
        return transaction

    def verify_transaction(self, transaction, public_key_pem):
        if transaction['sender'] == "0":  # Если это транзакция создания кошелька
            return True
        public_key = self.get_public_key(public_key_pem)
        signature = bytes.fromhex(transaction['signature'])
        transaction_copy = transaction.copy()
        del transaction_copy['signature']
        transaction_bytes = json.dumps(transaction_copy, sort_keys=True).encode('utf-8')
        
        try:
            public_key.verify(
                signature,
                transaction_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except:
            return False

    def get_pending_transactions(self):
        return self.pending_transactions

    def clear_pending_transactions(self):
        self.pending_transactions = []

    def sign_transaction(self, private_key, transaction):
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

    def get_public_key(self, public_key_pem):
        return serialization.load_pem_public_key(public_key_pem.encode())
