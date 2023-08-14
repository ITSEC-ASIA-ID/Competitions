import numpy as np
import random
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad,unpad
import requests 

def bitstring_to_bytes(s):
    return int(s, 2).to_bytes((len(s) + 7) // 8, byteorder='big')

H = np.array([[1.0,1.0],[1.0,-1.0]])/np.sqrt(2), 
X = np.array([[0.0,1.0],[1.0,0.0]])
def get_quantum_key(state_list, basis_list):
    key_bits = ''   
    
    if(len(state_list) != 1024 or len(basis_list) != 1024):
        return -1
    
    for basis in basis_list:
        if(str.upper(basis) not in ['H', 'X']):
                return -1
                    
    our_basis = []
                    
    for i in range(0, 1024):
        our_basis.append(random.choice(["H", "X"]))
            
    for i in range(0, 1024):
        if(our_basis[i] == basis_list[i]):
                if(basis_list[i] == "H"):
                    state = np.dot(H, state_list[i])
                else:
                    state = np.dot(X, state_list[i])

                if(state[0][0] > .99):
                    key_bits += '1'
                else:
                    key_bits += '0'
    
    if(len(key_bits) < 128):
        return -1

    print(key_bits[0:128])
    key = bitstring_to_bytes(key_bits[0:128])
    

def decrypt(data):

    key = bitstring_to_bytes('0'*128)
    cipher = AES.new(key, AES.MODE_CBC, b64decode(data['iv']))
    plaintext = unpad(cipher.decrypt(b64decode(data['ciphertext'])), AES.block_size)
    print(plaintext)

a = [[1,1]]*1024
b = ["H"]*1024
get_quantum_key(a,b)

json_data = {
    "state_list":a,
    "basis_list":b
}

res = requests.post("https://nessus-quantumcrypto.chals.io/quantum_key",json=json_data)

data = res.json()

decrypt(data)