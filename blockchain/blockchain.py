"""
Created on Wed Nov  7 21:18:35 2018

@author: wborbaneto
"""
import datetime
from hashlib import sha256
import json
from flask import Flask, jsonify


# Part 1 - Building a Blockchain
class Blockchain:

	def __init__(self):
		self.chain = []
		self.create_block(proof=1, previous_hash='0')

	def create_block(self, proof, previous_hash):
		"""Simple create a block after it is successfully mined.
        
        GENERALLY, a block can be build with a INDEX, the TIME in which it was
        mined, a PROOF that proofs its mining and a POINTER to the previous
        block.
        """
		block = {'index': len(self.chain) + 1,
				 'timestamp': str(datetime.datetime.now()),
				 'proof': proof,
				 'previous_hash': previous_hash}
		self.chain.append(block)
		return block

	def get_previous_block(self):
		"""Returns the previous block's dictionary."""
		return self.chain[-1]

	def proof_of_work(self, previous_proof):
		"""Calculate the proof of work.
        
        The proof of work is needed for the miner be able to mine the block.
        The proof  of work is calculated in a way that the miner has to guess
        some value that will be accounted in the calculation of a hash.
        In this case we are simply using some algebraic function that uses the
        previous proof and actual proof.
        """

		new_proof = 1
		check_proof = False

		while check_proof is False:
			hash_operation = self.hash_op(new_proof, previous_proof)
			if hash_operation[:4] == '0000':
				check_proof = True
			else:
				new_proof += 1
		return new_proof

	def hash_block(self, block):
		"""Calculate the hash of a block."""
		encoded_block = json.dumps(block, sort_keys=True).encode()
		return sha256(encoded_block).hexdigest()

	def hash_op(self, proof, previous_proof):
		"""Calculate the hash operation.
        
        The hash operation is done by a miner to try to get a valid hash for
        the block that is being mine. It can be done in a sort of ways, bu here
        we use a simple non-symmetrical operation.
        sha256 must receive a b'' parameter, which is accomplished by the 
        .encode() method. 
        In other hand, the .hexdigest() converts the b'' return from sha256 in
        a string of hexadecimal values.
        """
		return sha256(
			str(proof ** 2 - previous_proof ** 2).encode()).hexdigest()

	def is_chain_valid(self, chain):
		"""Check the validity of a chain.
        
        To check the validity of a chain we will do two simple steps, despite
        all the enormous amount of checks that have to be done in a real
        network, the two featured here are "okay-ish" for educational purposes.
        These two are (i) Checking if each block points to the previous block
        and (ii) Checking if the hash of each block is valid.
        """
		previous_block = chain[0]
		block_index = 1

		while block_index < len(chain):
			block = chain[block_index]
			# Checking if the previous_hash field is equal to the hash of the
			# previous_block
			if block['previous_hash'] != self.hash_block(previous_block):
				return False
			previous_proof = previous_block['proof']
			proof = block['proof']
			# Calculating the hash of the actual block
			hash_operation = self.hash_op(proof, previous_proof)
			# Checking if the hash starts with four leading zeros
			if hash_operation[:4] != '0000':
				return False
			previous_block = block
			block_index += 1
		return True


# Part 2 - Mining our Blockchain

# Creating Web App
app = Flask(__name__)

# Creating a blockchain
blockchain = Blockchain()


# Mining a new block
@app.route('/mine_block', methods=['GET'])
def mine_block():
	previous_block = blockchain.get_previous_block()
	previous_proof = previous_block['proof']
	proof = blockchain.proof_of_work(previous_proof)
	previous_hash = blockchain.hash_block(previous_block)
	block = blockchain.create_block(proof, previous_hash)
	response = {'message': 'Congratulations, you just mined a block!',
				'index': block['index'],
				'timestamp': block['timestamp'],
				'proof': block['proof'],
				'previous_hash': block['previous_hash']}
	return jsonify(response), 200


# Getting the full Blockchain
@app.route('/get_chain', methods=['GET'])
def get_chain():
	response = {'chain': blockchain.chain,
				'length': len(blockchain.chain)}
	return jsonify(response), 200


# Testing the validity of a blockchain
@app.route('/is_valid', methods=['GET'])
def is_valid():
	bchain = blockchain.chain
	response = {'validity': blockchain.is_chain_valid(bchain)}
	return jsonify(response), 200


# Running the app
app.run(host='0.0.0.0', port=5000)
