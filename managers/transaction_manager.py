import json
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization

class TransactionManager:
    def __init__(self):
        self.pending_transactions = []

    def create_transaction(self, sender, recipient, amount, signature=None, public_key=None):
        transaction = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        }
        if sender != "0" and signature and public_key:  # Если это не транзакция создания кошелька и есть подпись и публичный ключ
            transaction['signature'] = signature.hex()
            transaction['public_key'] = public_key
            if not self.verify_transaction(transaction):
                raise ValueError("Invalid transaction signature")
        self.pending_transactions.append(transaction)
        return transaction

    def verify_transaction(self, transaction):
        if transaction['sender'] == "0":  # Если это транзакция создания кошелька
            return True
        public_key = serialization.load_pem_public_key(transaction['public_key'].encode())
        signature = bytes.fromhex(transaction['signature'])
        transaction_copy = transaction.copy()
        del transaction_copy['signature']
        del transaction_copy['public_key']
        transaction_bytes = json.dumps(transaction_copy, sort_keys=True).encode('utf-8')
        
        try:
            public_key.verify(
                signature,
                transaction_bytes,
                ec.ECDSA(hashes.SHA256())
            )
            return True
        except Exception as e:
            print(f"Transaction verification failed: {e}")
            return False

    def get_pending_transactions(self):
        return self.pending_transactions

    def clear_pending_transactions(self):
        self.pending_transactions = []
