from managers.wallet_manager import WalletManager
from managers.transaction_manager import TransactionManager
from managers.block_manager import BlockManager
from managers.chain_manager import ChainValidator

from logger import blockchain_logger

class Blockchain:
    def __init__(self):
        self.chain = []
        self.wallet_manager = WalletManager()
        self.transaction_manager = TransactionManager(self.wallet_manager)
        self.block_manager = BlockManager()
        self.chain_validator = ChainValidator(self.block_manager, self.transaction_manager)
        
        # Create genesis block
        genesis_block = self.block_manager.create_block([], "0")
        self.chain.append(genesis_block)
        blockchain_logger.info("Blockchain initialized with genesis block")

    def create_wallet(self, address, public_key):
        wallet_data = self.wallet_manager.create_wallet(address, public_key)
        blockchain_logger.info(f"Wallet created: {address}")
        
        # Добавление транзакции создания кошелька
        self.transaction_manager.create_transaction("0", address, 100)
        blockchain_logger.info(f"Initial transaction created for wallet: {address}")
        
        # Автоматический майнинг блока после создания кошелька
        self.mine_block()
        
        return wallet_data

    def get_balance(self, wallet_address):
        balance = 0
        for block in self.chain:
            for transaction in block['transactions']:
                if transaction['sender'] == wallet_address:
                    balance -= transaction['amount']
                if transaction['recipient'] == wallet_address:
                    balance += transaction['amount']
        blockchain_logger.info(f"Balance for {wallet_address}: {balance}")
        return balance

    def find_wallet(self, address):
        for block in self.chain:
            for transaction in block['transactions']:
                if transaction['sender'] == address or transaction['recipient'] == address:
                    return True
        return False

    def create_transaction(self, sender, recipient, amount, signature):
        blockchain_logger.info(f"Transaction created: {sender} -> {recipient}, amount: {amount}")
        transaction = self.transaction_manager.create_transaction(sender, recipient, amount, signature)
        self.mine_block()
        return transaction

    def mine_block(self):
        last_block = self.chain[-1]
        
        # Отладочное сообщение
        blockchain_logger.debug(f"Pending transactions before mining: {self.transaction_manager.get_pending_transactions()}")
        
        new_block = self.block_manager.create_block(
            self.transaction_manager.get_pending_transactions(),
            last_block['hash']
        )
        mined_block = self.block_manager.mine_block(new_block)
        self.chain.append(mined_block)
        
        self.transaction_manager.clear_pending_transactions()
        
        # Отладочное сообщение
        blockchain_logger.debug(f"Pending transactions after mining: {self.transaction_manager.get_pending_transactions()}")
        
        blockchain_logger.info(f"New block mined and added to the chain. Block hash: {mined_block['hash']}")
        return mined_block

    def is_chain_valid(self):
        is_valid = self.chain_validator.is_valid_chain(self.chain)
        blockchain_logger.info(f"Chain validation result: {'Valid' if is_valid else 'Invalid'}")
        return is_valid

    def get_chain(self):
        blockchain_logger.info(f"Current chain length: {len(self.chain)}")
        return self.chain
