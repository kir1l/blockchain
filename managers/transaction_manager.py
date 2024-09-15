import json
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

class TransactionManager:
    def __init__(self, wallet_manager):
        self.wallet_manager = wallet_manager
        self.pending_transactions = []

    def create_transaction(self, sender, recipient, amount):
        transaction = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        }
        signature = self.wallet_manager.sign_transaction(sender, transaction)
        transaction['signature'] = signature.hex()
        self.pending_transactions.append(transaction)
        return transaction

    def verify_transaction(self, transaction):
        sender = transaction['sender']
        public_key = self.wallet_manager.wallets[sender]['public_key']
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
