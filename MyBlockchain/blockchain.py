import sys
import hashlib
import json
from time import time
from uuid import uuid4
from flask import Flask, jsonify, request, redirect, url_for
import requests
from urllib.parse import urlparse

class Blockchain(object):
    difficulty_target = "0000"
    # difficulty_target = "00000"
    # difficulty_target = "000000"
    # difficulty_target = "00000000"
    # difficulty_target = "0000000000"

    #function to hash return sha256 block
    def hash_block(self, block):
        block_encoded = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_encoded).hexdigest()

    def __init__(self):
        # stores all the blocks in the entire blockchain
        self.chain = []
        # temporarily stores the transactions for the
        # current block
        self.current_transactions = []
        #create set of nodes
        self.nodes = []
        # create the genesis block with a specific fixed hash
        # of previous block genesis block starts with index 0
        genesis_hash = self.hash_block("genesis_block")
    
        self.append_block(hash_of_previous_block = genesis_hash, nonce = self.proof_of_work(0, genesis_hash, []))
    
    #add new node to list of nodes
    def add_new_nodes(self,port):
        address_node = port
        if port in self.nodes:
            print('port {} is already a node'.format(address_node))
        else:
            self.nodes.append(address_node)
            return print(self.nodes)

    #validate blockchain by verifying hashes - return true or false for validation result
    def validate_blockchain(self,chain):
        #initialize prev_block as genesis block.
        prev_block = chain[0]
        #set initial index as 2nd block
        current_index = 1

        #work way back from genesis to latest to ensure block is not tampered. 
        while current_index < len(chain):
            block_to_validate = chain[current_index]
            prev_hash = self.hash_block(prev_block)
            #check if block of prev's hash == prev_hash
            if block_to_validate['hash_of_previous_block'] != prev_hash:
                return False
            #else, we continue to check POW 
            if not self.valid_proof(block_to_validate['index'],block_to_validate['hash_of_previous_block'],block_to_validate['transactions'],block_to_validate['nonce']):
                return False
            
            #if all is in order, we continue through the block
            prev_block=block_to_validate
            current_index+=1
        return True

    #synchronize nodes by updating blockchain on neighbour nodes
    def sync_nodes(self):
        #make sure that our chain is the longest chain.(block height)
        neighbour_nodes = self.nodes
        new_chain = None
        print(self.nodes)
        length_block = len(self.chain)
        print('len of block: {}'.format(length_block))
        #check with our neighbours
        for node in neighbour_nodes:
            response = requests.get('http://localhost:{}/blockchain'.format(node))
            if response.status_code==200:
                length = response.json()['length']
                chain = response.json()['chain']

                #update if longer
                if length > length_block and self.validate_blockchain(chain):
                    length_block = length
                    new_chain = chain   
        #changed
        if new_chain:
            self.chain = new_chain
            return True
        #unchanged
        return False

    # use PoW to find the nonce for the current block
    def proof_of_work(self, index, hash_of_previous_block, transactions):
        # try with nonce = 0
        nonce = 0
        time_start = time()
        # try hashing the nonce together with the hash of the
        # previous block until it is valid
        while self.valid_proof(index, hash_of_previous_block, transactions, nonce) is False:
            nonce += 1
        return nonce

    def valid_proof(self, index, hash_of_previous_block, transactions, nonce):
        # create a string containing the hash of the previous
        # block and the block content, including the nonce
        content = f'{index}{hash_of_previous_block}{transactions}{nonce}'.encode()
        # hash using sha256
        content_hash = hashlib.sha256(content).hexdigest()
        # check if the hash meets the difficulty target
        return content_hash[:len(self.difficulty_target)] == self.difficulty_target

    # creates a new block and adds it to the blockchain
    def append_block(self, nonce, hash_of_previous_block):

        block = {'index': len(self.chain), 'timestamp': time(), 'transactions': self.current_transactions,'nonce': nonce,'hash_of_previous_block': hash_of_previous_block}
        
        #reset the current list of transactions
        self.current_transactions = []
        # add the new block to the blockchain
        self.chain.append(block)
        return block

    def add_transaction(self, sender, recipient, amount):
        self.current_transactions.append({'amount': amount,'recipient': recipient,'sender': sender,})
        return self.last_block['index'] + 1

    @property
    def last_block(self):
        # returns the last block in the blockchain
        return self.chain[-1]


app = Flask(__name__)
# generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')
# instantiate the Blockchain
blockchain = Blockchain()


# return the entire blockchain
@app.route('/blockchain', methods=['GET'])
def full_chain():
    # blockchain.sync_nodes()
    response = {'chain': blockchain.chain, 'length': len(blockchain.chain),}
    return jsonify(response), 200


@app.route('/mine', methods=['GET'])
def mine_block():
    time_start = time()
    blockchain.add_transaction(sender="0",recipient=node_identifier,amount=1,)
    # obtain the hash of last block in the blockchain
    last_block_hash = blockchain.hash_block(blockchain.last_block)
    # using PoW, get the nonce for the new block to be added to the blockchain
    index = len(blockchain.chain)
    nonce = blockchain.proof_of_work(index, last_block_hash,blockchain.current_transactions)
    # add the new block to the blockchain using the last block
    # hash and the current nonce
    block = blockchain.append_block(nonce, last_block_hash)
    time_stop = time()
    elapsed = time_stop-time_start
    response = {'message': "New Block Mined",'index': block['index'],'hash_of_previous_block':block['hash_of_previous_block'],'nonce': block['nonce'],'transactions': block['transactions'],'elapsed_time':elapsed}
    return jsonify(response), 200

@app.route('/nodes/new',methods=['POST'])
def new_nodes():
    #get values passed from client
    values = request.get_json()
    # add the port number into nodes list.
    blockchain.add_new_nodes(values['port'])
    response = {'message':'The following Nodes are in Neighbour list: {}'.format(blockchain.nodes)}
    return(jsonify(response),201)
    
@app.route('/nodes/sync',methods=['GET'])
def sync():
    sync_outcome = blockchain.sync_nodes()
    if sync_outcome == True:
        response = {'message:':'block successfully sync with latest','blockchain':blockchain.chain}
    else:
        response = {'message:':'block is already latest','blockchain':blockchain.chain}
    return jsonify(response), 200
    
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    # get the value passed in from the client
    values = request.get_json()
    print(values)
    # check that the required fields are in the POST'ed data
    required_fields = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required_fields):
        return ('Missing fields', 400)

    # create a new transaction
    index = blockchain.add_transaction(values['sender'],values['recipient'],values['amount'])
    response = {'message': f'Transaction will be added to Block {index}'}
    return (jsonify(response), 201)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(sys.argv[1]))
