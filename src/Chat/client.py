from AES_lib import *
from RSA import RSA
from keccak import sha3_256
from BB84 import BB84_User

RSA_KEY_LEN = 512

class Client:
    def __init__(self, key, sock):
        '''
            Create key and save socket for connection
        '''
        self.key = key
        self.aes = AES128(key)
        self.sock = sock
    
    def set_nickname(self, name):
        self.nick = name

    def encrypt(self, text: str):
        '''
            Encrypt string, using key of client. Lenght of the message is placed before chifertext
        '''
        sb = bytes(text, 'utf-8')
        cipher = self.aes.encrypt(sb)
        hash_value = bytes(sha3_256(cipher))
        new_value = cipher + hash_value
        return new_value
        # return self.aes.encrypt(sb)y
    
    def decrypt(self, sb: bytes):
        '''
            Decrypt bytes, using key of client, and getting lenght from start of the message
        '''
        # return str(self.aes.decrypt(sb), 'utf-8')
        if bytes(sha3_256(sb[:-32])) == sb[-32:]:
            return str(self.aes.decrypt(sb[:-32]), 'utf-8')
        else:
            return "The message was changed during transmission! For security reasons, the message can not be decrypted."
    
    def send(self, text):
        '''
            Send to socket encypted message
        '''
        self.sock.send(self.encrypt(text))

    def recv(self):
        '''
            Wait for message from socket and decrypt it
        '''
        return self.decrypt(self.sock.recv(1024))
   
    def close(self):
        self.sock.close()

    def key_exchange(self):
        '''
            Recieve public key, encrypt AES key and send it
        '''
        n = int.from_bytes(self.sock.recv(RSA_KEY_LEN), "big")
        e = int.from_bytes(self.sock.recv(RSA_KEY_LEN), "big")
        byte_key = bytes(i for i in self.key)
        self.sock.send(RSA(n, e=e).encrypt(byte_key))

    @staticmethod
    def get_key(sock):
        '''
            Send public key, recieve encrypted AES key and decrypt it
        '''
        n, e, d = RSA.generate_key(RSA_KEY_LEN)
        sock.send(n.to_bytes(RSA_KEY_LEN, "big"))
        sock.send(e.to_bytes(RSA_KEY_LEN, "big"))
        key = RSA(n, e=e, d=d).decrypt(sock.recv(AES_KEY_LEN * RSA_KEY_LEN))
        return gen_key([*key])
    

def list_int_to_str(li: list[int]):
    return "".join(str(x) for x in li)

def str_to_list_int(s: str):
    return [int(x) for x in s]

class Q_Key_Exchange:
    '''
        Imitation of quantum key exchange using BB84 protocol
    '''
    def __init__(self, sock, need_bytes: int = AES_KEY_LEN):
        '''
            Save socket for connection
            After key preparation get key of "need_bytes" bytes
        '''
        self.sock = sock
        self.need_bytes = need_bytes
    
    def send(self, text):
        '''
            Send to socket plaintext
        '''
        self.sock.send(bytes(text, "utf-8"))

    def recv(self, n: int):
        '''
            Wait for message from socket and decrypt it
        '''
        return str(self.sock.recv(n), "utf-8")
    
    def form_byte_key(self, bit_key: list[int]):
        if len(bit_key)//8 < self.need_bytes:
            return None
        return [sum(bit_key[8*i+j]*2**j for j in range(8)) for i in range(self.need_bytes)] 

    def do_alice_part(self) -> bytes:
        '''
            Alice's (leader) side of the protocol
        '''
        n = self.need_bytes * 8 * 4 # required number of bits with possible 75% key loss
        while True:
            print("START: " + str(n))
            self.send(str(n))
            alice = BB84_User(n, True)

            # === Quantum channel   ===
            self.send(alice.get_sends()) # send states (qubits)

            # === Classical channel ===
            # exchange bases
            self.send(alice.bases)
            bob_bases = self.recv(3*n) # each symbol up to 3 bytes

            alice.get_key(bob_bases) # form the key

            # Key error check
            chosen_compare = alice.get_chosen_compare(alice.n//2)
            self.send(list_int_to_str(chosen_compare))
            bob_check_bits = str_to_list_int(self.recv(n))

            alice_check_bits = alice.get_check_bits(chosen_compare)
            self.send(list_int_to_str(alice_check_bits))

            key = None
            if alice.check(chosen_compare, bob_check_bits):
                key = self.form_byte_key(alice.key)
            
            if self.recv(5) == 'OK' and key:
                self.send('END')
                print(list_int_to_str(alice.key))
                return key
            n = int(n*1.5) # increase number of qubits because of it's possible shortage
            self.send('NEW') # new try

    def do_bob_part(self) -> bytes:
        '''
            Bob's (follower) side of the protocol  
        '''
        while True:
            n = int(self.recv(20))
            bob = BB84_User(n, False)

            # === Quantum channel   ===
            bob.get_observations(self.recv(3*n)) # recieve and measure qubits 

            # === Classical channel ===
            # exchange bases
            alice_bases = self.recv(3*n) # each symbol up to 3 bytes
            self.send(bob.bases)

            bob.get_key(alice_bases)  # form the key

            # Key error check
            chosen_compare = str_to_list_int(self.recv(n))
            bob_check_bits = bob.get_check_bits(chosen_compare)
            self.send(list_int_to_str(bob_check_bits))

            alice_check_bits = str_to_list_int(self.recv(n))
            
            key = None
            if bob.check(chosen_compare, alice_check_bits):
                key = self.form_byte_key(bob.key)
            
            self.send('OK' if key else 'ERROR')
            if self.recv(5) == 'END':
                print(list_int_to_str(bob.key))
                return key
                