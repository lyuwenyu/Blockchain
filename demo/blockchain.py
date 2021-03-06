import hashlib
import json
from time import time
from urllib.parse import urlparse
import requests

class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.nodes = set()
        self.current_transaction = []

        self.new_block(previous_hash=1, proof=1000)
        
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

    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            
            if block['previous_hash'] != self.hash(last_block):
                return False

            if not self.valid_proof(last_block['proof'], block['proof']):
                return False
            
            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        neighbours = self.nodes
        new_chain = None

        max_length = len(self.chain)

        for node in neighbours:
            response = requests.get(f'http://{node}/chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain
            
        if new_chain:
            self.chain = new_chain
            return True
        
        return False
    

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
