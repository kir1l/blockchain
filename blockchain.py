from managers.wallet_manager import WalletManager
from managers.transaction_manager import TransactionManager
from managers.block_manager import BlockManager
from managers.chain_manager import ChainValidator

class Blockchain:
    def __init__(self):
        self.chain = []
        self.wallet_manager = WalletManager(self)
        self.transaction_manager = TransactionManager()
        self.block_manager = BlockManager()
        self.chain_validator = ChainValidator(self.block_manager, self.transaction_manager)
        
        # Create genesis block
        genesis_block = self.block_manager.create_block([], "0")
        self.chain.append(genesis_block)

    def create_wallet(self, address, public_key):
        wallet_data = {
            'address': address,
            'public_key': public_key
        }
        
        # Добавление транзакции создания кошелька
        self.transaction_manager.create_transaction("0", address, 100)
        
        # Автоматический майнинг блока после создания кошелька
        self.mine_block()
        
        return wallet_data

    def get_balance(self, wallet_address):
        return self.wallet_manager.get_balance(wallet_address)

    def create_transaction(self, sender, recipient, amount, signature, public_key):
        response = self.transaction_manager.create_transaction(sender, recipient, amount, signature, public_key)
        self.mine_block()
        return response

    def mine_block(self):
        last_block = self.chain[-1]
        
        new_block = self.block_manager.create_block(
            self.transaction_manager.get_pending_transactions(),
            last_block['hash']
        )
        mined_block = self.block_manager.mine_block(new_block)
        self.chain.append(mined_block)
        
        self.transaction_manager.clear_pending_transactions()
        
        return mined_block

    def is_chain_valid(self):
        return self.chain_validator.is_valid_chain(self.chain)

    def get_chain(self):
        return self.chain

    def find_wallet(self, address):
        return self.wallet_manager.find_wallet(address)
