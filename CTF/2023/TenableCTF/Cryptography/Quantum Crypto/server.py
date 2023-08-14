import numpy as np
import random
from base64 import b64encode, b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

...

# computational basis states
one_state = np.array([[1.0],[0.0]])
zero_state = np.array([[0.0],[1.0]])

# Hadamard and X-pauli gates
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
    
    key = bitstring_to_bytes(key_bits[0:128])
    
    cipher = AES.new(key, AES.MODE_CBC)
    cipher_text = cipher.encrypt(pad(flag, AES.block_size))
    iv = cipher.iv
    
    return {"basis": our_basis, "iv":b64encode(iv), "ciphertext":b64encode(cipher_text)}