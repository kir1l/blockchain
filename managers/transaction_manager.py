import json
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes

from logger import blockchain_logger

class TransactionManager:
    def __init__(self, wallet_manager):
        self.wallet_manager = wallet_manager
        self.pending_transactions = []
        blockchain_logger.info("TransactionManager initialized")

    def create_transaction(self, sender, recipient, amount, signature=None):
        transaction = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        }
        if sender != "0" and signature:  # Если это не транзакция создания кошелька и есть подпись
            transaction['signature'] = signature.hex()
        self.pending_transactions.append(transaction)
        blockchain_logger.info(f"Transaction created: {transaction}")
        return transaction

    def verify_transaction(self, transaction):
        if transaction['sender'] == "0":  # Если это транзакция создания кошелька
            blockchain_logger.info("Wallet creation transaction verified")
            return True
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
            blockchain_logger.info(f"Transaction verified: {transaction}")
            return True
        except:
            blockchain_logger.warning(f"Transaction verification failed: {transaction}")
            return False

    def get_pending_transactions(self):
        blockchain_logger.info(f"Retrieved {len(self.pending_transactions)} pending transactions")
        return self.pending_transactions

    def clear_pending_transactions(self):
        num_cleared = len(self.pending_transactions)
        self.pending_transactions = []
        blockchain_logger.info(f"Cleared {num_cleared} pending transactions")
