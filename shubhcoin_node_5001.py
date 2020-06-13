# Module 1 Creating a cryptocurrency
"""
Created on Mon May 18 13:18:13 2020

@author: sk520
"""
#importing the libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse
from flask_api import FlaskAPI

# Building the blockchain
class Blockchain:
    
    def __init__(self): #declaring a chain and createblock func
        self.chain=[]
        self.transactions=[]
        self.create_block(proof=1, previous_hash='0')
        self.nodes=set()
       
    def create_block(self,proof,previous_hash): #creation of block
        block={'index':len(self.chain)+1,
               'timestamp':str(datetime.datetime.now()),
               'proof':proof,
               'previous_hash':previous_hash,
               'transactions':self.transactions}
        self.transactions=[]
        self.chain.append(block)
        return block
    
    def get_previous_block(self): #retrieve previous block
        return self.chain[-1]
    
    def proof_of_work(self,previous_proof): #proof of work to be solved by miners to add a block to the chain
        new_proof=1
        check_proof=False
        while check_proof is False:
            hash_operation=hashlib.sha256(str(new_proof**2-previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000': #the generated proof should have 4 trailing zeroes
                check_proof=True
            else:
                new_proof+=1
        return new_proof
    
    def hash(self,block):
        encoded_block=json.dumps(block,sort_keys=True).encode() #json.dumps is used to convert dictionary values of a block into a string which is accepted by a hash function
        return hashlib.sha256(encoded_block).hexdigest()  

    def is_chain_valid(self,chain): #validation of chain by checking hashes and proof
        previous_block=chain[0] #first block
        block_index=1
        while block_index < len(chain):
            block=chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof=previous_block['proof']
            proof=block['proof']
            hash_operation=hashlib.sha256(str(proof**2-previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block=block
            block_index+=1
        return True
    
    def add_transaction(self,sender,receiver,amount):
        self.transactions.append({'sender':sender,
                                  'receiver':receiver,
                                  'amount':amount})
        previous_block=self.get_previous_block()
        return previous_block['index'] + 1
        
    def add_node(self,address):
        parsed_url=urlparse(address)
        self.nodes.add(parsed_url.netloc)
        
    def replace_chain(self):
        network=self.nodes
        longest_chain=None
        max_length=len(self.chain)
        for node in network:
            response=requests.get(f"http://{node}/get_chain")
            if response.status_code == 200:
                length=response.json()['length']
                chain=response.json()['chain']
                if length>max_length and self.is_chain_valid(chain):
                    max_length=length
                    longest_chain=chain
        if longest_chain:
            self.chain=longest_chain
            return True
        return False
# Mining the blockchain

# creating an address for the node on port=5000
node_address=str(uuid4()).replace('-','')

# Creating a web app
app=FlaskAPI(__name__)
        
# Creating a blockchain
blockchain=Blockchain()

# mining a new block
@app.route("/mine_block",methods=['GET'])
def mine_block():
    previous_block=blockchain.get_previous_block()
    previous_proof=previous_block['proof']
    proof=blockchain.proof_of_work(previous_proof)
    previous_hash=blockchain.hash(previous_block)
    blockchain.add_transaction(sender=node_address,receiver= 'Shubham',amount=1)
    block=blockchain.create_block(proof,previous_hash)
    response={'message':'Congratulations you successfully mined a block.',
              'index':block['index'],
              'timestamp':block['timestamp'],
              'proof':block['proof'],
              'previous_hash':block['previous_hash'],
              'transactions':block['transactions']}
    return jsonify(response), 200

#Getting a full blockchain
@app.route("/get_chain",methods=['GET'])
def get_chain():
    response={'chain':blockchain.chain,
              'length':len(blockchain.chain)}
    return jsonify(response), 200

#checking the validity of the blockchain
@app.route("/is_valid",methods=['GET'])
def is_valid():
    valid=blockchain.is_chain_valid(blockchain.chain)
    if valid:
        response={'message':'All good, The blockchain is valid'}
    else:
        response={'message':'OOPS!!! Something went wrong. The Blockchain is not valid.'}    
    return jsonify(response), 200

@app.route("/add_transaction",methods=['POST'])
def add_transaction():
    json=request.get_json()
    transac_keys=['sender','receiver','amount']
    if not all (key in json for key in transac_keys):
        return 'Some elements of the transaction are missing', 400
    index=blockchain.add_transaction(json['sender'],json['receiver'],json['amount'])
    response={'message':f'This transaction will be added to the block {index}'}
    return jsonify(response), 201

@app.route("/connect_node",methods=['POST'])
def connect_node():
    json=request.get_json()
    nodes=json.get('nodes')
    if nodes is None:
        return "No node", 400
    for node in nodes:
        blockchain.add_node(node)
    response={'message':'All the nodes are now connected. The Shubhcoin blockchain contains the following nodes:',
              'total_nodes':list(blockchain.nodes)}    
    return jsonify(response), 201
    
# Decentralising the blockchain
    
# Replacing the chain with the longest chain
@app.route("/replace_chain",methods=['GET'])
def replace_chain():
    is_chain_replaced=blockchain.replace_chain()
    if is_chain_replaced:
        response={'message':'The nodes had different chain so the chain was updated.',
                  'new_chain':blockchain.chain}
    else:
        response={'message':'OOPS!!! Something went wrong. The Blockchain is not valid.',
                  'actual_chain':blockchain.chain}    
    return jsonify(response), 200

#Running the app
app.run(host='0.0.0.0',port=5001)