import hashlib
import json
import time

class BlockManager:
    def __init__(self):
        self.difficulty = 4

    def create_block(self, transactions, previous_hash):
        block = {
            'timestamp': time.time(),
            'transactions': transactions,
            'previous_hash': previous_hash,
            'nonce': 0
        }
        block['hash'] = self.calculate_hash(block)
        return block

    def calculate_hash(self, block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def mine_block(self, block):
        target = '0' * self.difficulty
        while block['hash'][:self.difficulty] != target:
            block['nonce'] += 1
            block['hash'] = self.calculate_hash(block)
        return block
