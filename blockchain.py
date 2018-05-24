import hashlib
import json
from time import time
from urllib.parse import urlparse

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transaction = []

        self.new_block(previous_hash=1, proof=1000)
        
        self.nodes = set()

    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transaction,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }
        self.current_transaction = []
        self.chain += [block]
        return block
    
    def new_transaction(self, sender, recipient, amount):
        '''
        Creat a new transaction to go into the next mined block

        :param sender: <str> Address of the sender
        :param recipient: <str> Adress of the recipient
        :param amount: <int> Amount
        :return <int> The index of the block that will hold this transaction
        '''
        self.current_transaction += [{
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        }]
        return self.last_block['index'] + 1

    def proof_of_work(self, last_proof):
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1
        return proof

    def register_node(self, address):
        self.nodes.add(urlparse(address).netloc)


    @staticmethod
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self,):
        return self.chain[-1]

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == '0000'


if __name__ == '__main__':

    bc = Blockchain()

    print(bc.chain)
    print(bc.last_block)

    print(bc.proof_of_work(bc.last_block['proof']))
