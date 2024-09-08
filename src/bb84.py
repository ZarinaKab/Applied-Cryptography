from numpy import matrix
from math import pow, sqrt
from random import randint
import sys
import argparse

class Qubit:
    def __init__(self, initial_state):
        if initial_state:
            self.__state = matrix([[0],[1]])
        else:
            self.__state = matrix([[1],[0]])
        self.__measured = False
        self.__H = (1/sqrt(2))*matrix([[1,1],[1,-1]])
        self.__X = matrix([[0,1],[1,0]])

    def show(self):
        aux = ""
        if round(matrix([1,0])*self.__state,2):
            aux += "{0}|0>".format(str(round(matrix([1,0])*self.__state,2)) if round(matrix([1,0])*self.__state,2) != 1.0 else '')
        if round(matrix([0,1])*self.__state,2):
            if aux:
                aux += " + "
            aux += "{0}|1>".format(str(round(matrix([0,1])*self.__state,2)) if round(matrix([0,1])*self.__state,2) != 1.0 else '')
        return aux

    def measure(self):
        if self.__measured:
            raise Exception("Qubit already measured!")
        M = 1000000
        m = randint(0,M)
        self.__measured = True
        if m < round(pow((matrix([1,0])*self.__state)[0, 0], 2), 2) * M:
            return 0
        else:
            return 1

    def hadamard(self):
        if self.__measured:
            raise Exception("Qubit already measured!")
        self.__state = self.__H*self.__state

    def X(self):
        if self.__measured:
            raise Exception("Qubit already measured!")
        self.__state = self.__X*self.__state

class QuantumUser:
    def __init__(self, name):
        self.name = name

    def send(self, data, basis):
        qubits = []
        for i in range(len(data)):
            if not basis[i]:
                if not data[i]:
                    qubits.append(Qubit(0))
                else:
                    qubits.append(Qubit(1))
            else:
                if not data[i]:
                    aux = Qubit(0)
                else:
                    aux = Qubit(1)
                aux.hadamard()
                qubits.append(aux)
        return qubits

    def receive(self, data, basis):
        bits = []
        for i in range(len(data)):
            if not basis[i]:
                bits.append(data[i].measure())
            else:
                data[i].hadamard()
                bits.append(data[i].measure())
        return bits

def generate_random_bits(N):
    return [randint(0,1) for _ in range(N)]

def QKD(N):
    alice_basis = generate_random_bits(N)
    alice_bits = generate_random_bits(N)
    alice = QuantumUser("Alice")
    alice_qubits = alice.send(data=alice_bits, basis=alice_basis)
    alice_key = [alice_bits[i] for i in range(N) if alice_basis[i] == bob_basis[i]]
    
    bob_basis = generate_random_bits(N)
    bob_bits = bob.receive(data=alice_qubits, basis=bob_basis)
    bob = QuantumUser("Bob")
    bob_key = [bob_bits[i] for i in range(N) if alice_basis[i] == bob_basis[i]]
    
    key_match = alice_key == bob_key
    key_length = len(bob_key)
    return key_match, bob_key

def save_key_to_file(key, filename):
    with open(filename, 'w') as f:
        f.write(''.join(map(str, key)))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='BB84 QKD demonstration with Python.')
    requiredNamed = parser.add_argument_group('Required arguments')
    optionalNamed = parser.add_argument_group('Optional arguments')
    requiredNamed.add_argument('-q', '--qubits', required=True, help='Number of Qubits.')
    optionalNamed.add_argument('-i', '--iterate', required=False, help='Number of iterations.')
    args = parser.parse_args()
    assert int(args.qubits)
    ret = []
    if args.iterate:
        assert int(args.iterate)
        N = int(args.iterate)
    else:
        N = 1
    for i in range(N):
        key_match, bob_key = QKD(int(args.qubits))
        if key_match:
            save_key_to_file(bob_key, f'key-{i}.txt')
            print(f"Key-{i}.txt")
