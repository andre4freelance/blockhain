import sys
import hashlib
import json

from time import time
from uuid import uuid4

from flask import Flask
from flask.globals import request
from flask.json import jsonify

import requests
from urllib.parse import urlparse

#code
class Blockchain(object):
    dificulty_target = "0000"

    def hash_block(self, block):
            block_encoded = json.dumps(block, sort_keys=True).encode()
            return hashlib.sha256(block_encoded).hexdigest() 

    def __init__(self):
        self.chain = []

        self.current_transaction = []   

        genesis_hash = self.hash_block("genesis_block")

        self.append_block(
            hash_opb = genesis_hash,
            nonce = self.pow(0, genesis_hash, [])
        )

    def pow(self, index, hash_opb, transaction):
        nonce = 0

        while self.valid_prof(index, hash_opb, transaction, nonce) is False :
            nonce += 1
        return nonce
    
    def valid_prof(self, index, hash_opb, transaction, nonce):
        content = f'{index}{hash_opb}{transaction}{nonce}'.encode()

        content_hash = hashlib.sha256(content).hexdigest()

        return content_hash[:len(self.dificulty_target)] == self.dificulty_target
    

    def append_block(self, nonce, hash_opb):
        block = {
              'index' : len(self.chain),
              'timestamp': time(),
              'transaction': self.current_transaction,
              'nonce': nonce,
              'hash_opb': hash_opb
         }

        self.current_transaction = []
    
        self.chain.append(block)
        return block

    def add_transaction(self, sender, recipient, amount):
         self.current_transaction.append({
              'amount' : amount,
              'recipient' : recipient,
              'sender'  : sender
         })

         return self.last_block['index'] + 1
    
    @property
    def last_block(self):
         return self.chain[-1]

app = Flask(__name__)

node_identifier = str(uuid4()).replace('-', "")

blockchain = Blockchain()

#routes
@app.route('/blockchain', methods=['GET'])
def full_chain():
     response = {
          'chain' : blockchain.chain,
          'length' : len(blockchain.chain)     
     }
     
     return jsonify(response), 200

@app.route('/mine', methods=['GET'])
def mine_block():
     blockchain.add_transaction(
          sender="0",
          recipient=node_identifier,
          amount=1
     )     

     last_block_hash = blockchain.hash_block(blockchain.last_block)

     index = len(blockchain.chain)
     nonce = blockchain.pow(index, last_block_hash, blockchain.current_transaction)

     block = blockchain.append_block(nonce, last_block_hash)
     response = {
          'messegae' : "Block baru berhasil di tambahkan {mined}",
          'index' : block['index'],
          'hash_opb' : block['hash_opb'],
          'nonce' : block['nonce'],
          'transaction' : block['transaction']
     }

     return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
     values = request.get_json()   

     required_fields = ['sender', 'recipient', 'amount']
     if not all(k in values for k in required_fields):
          return ('Missing fields', 400)
     
     index = blockchain.add_transaction(
          values['sender'],
          values['recipient'],
          values['amount']
     )

     response = {'message': f'Transaksi akan  di tambahkan ke block {index}'}
     return (jsonify(response), 201)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(sys.argv[1]))

