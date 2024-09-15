class ChainValidator:
    def __init__(self, block_manager, transaction_manager):
        self.block_manager = block_manager
        self.transaction_manager = transaction_manager

    def is_valid_chain(self, chain):
        for i in range(1, len(chain)):
            current_block = chain[i]
            previous_block = chain[i-1]
            
            if current_block['previous_hash'] != previous_block['hash']:
                return False
            
            if current_block['hash'] != self.block_manager.calculate_hash(current_block):
                return False
            
            for transaction in current_block['transactions']:
                if not self.transaction_manager.verify_transaction(transaction):
                    return False
        
        return True
