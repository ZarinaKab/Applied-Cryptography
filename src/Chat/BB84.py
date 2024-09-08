from random import random, randint, choices

rect_basis = '+'
diag_basis = 'X'

arrow_up = '↑'
arrow_ri = '→'
arrow_lu = '↖'
arrow_ru = '↗'

def observe(basis: str, state: str):
    if basis == rect_basis:
        if state in (arrow_up, arrow_ri):
            return int(state == arrow_up), state
        if random() < 0.5:
            return 0, arrow_ri
        return 1, arrow_up
    
    if state in (arrow_lu, arrow_ru):
        return int(state == arrow_lu), state
    if random() < 0.5:
        return 0, arrow_ru
    return 1, arrow_lu

class BB84_User:
    def __init__(self, n: int, gen_bits: bool):
        self.n = n
        if gen_bits:
            self.bits = [randint(0, 1) for i in range(n)]
        self.bases = "".join(rect_basis if randint(0, 1) else diag_basis for i in range(n))

    def get_sends(self):
        self.sends = ''.join((arrow_up if self.bits[i] else arrow_ri) 
                             if self.bases[i] == rect_basis else 
                             (arrow_lu if self.bits[i] else arrow_ru)
                             for i in range(self.n))
        return self.sends
        
    def get_observations(self, data: str):
        assert len(data) == self.n
        self.bits, self.observations = zip(*(observe(self.bases[i], data[i]) for i in range(self.n)))
        self.observations = ''.join(self.observations)
        return self.bits
    
    def get_key(self, another_bases: str):
        assert len(another_bases) == self.n
        self.key = [x for i, x in enumerate(self.bits) if self.bases[i] == another_bases[i]]
        self.n = len(self.key)
        return self.key
        
    def get_chosen_compare(self, count: int):
        indices = choices(list(range(self.n)), k=count) # indices, chosen to compare
        res = [0]*self.n
        for ind in indices:
            res[ind] = 1
        return res

    def get_check_bits(self, chosen_compare: list[bool]):
        assert len(chosen_compare) == self.n
        return [x for i, x in enumerate(self.key) if chosen_compare[i]]
    
    def check(self, chosen_compare: list[bool], bits: list[int]):
        assert len(chosen_compare) == self.n
        assert sum(chosen_compare) == len(bits)
        if self.get_check_bits(chosen_compare) != bits:
            key = None
            return False
        self.key = [x for i, x in enumerate(self.key) if not chosen_compare[i]]
        return True

    
def gen_key(n: int):
    alice = BB84_User(n, True)
    bob = BB84_User(n, False)
    bob.get_observations(alice.get_sends())

    is_same_basis = [alice.bases[i] == bob.bases[i] for i in range(n)]
    alice.get_key(bob.bases)
    bob.get_key(alice.bases)

    print(f"Alice's random bits       : {' '.join(map(str, alice.bits))}")
    print(f"Alice's random bases      : {' '.join(alice.bases)}")
    print(f"Alice sends               : {' '.join(alice.sends)}")
    print()
    print(f"Bob's random bases        : {' '.join(bob.bases)}")
    print(f"Bob observes              : {' '.join(bob.observations)}")
    print(f"Bob's bits                : {' '.join(map(str, bob.bits))}")
    print()
    print(f"Which agree?              : {' '.join('✓' if x else ' ' for x in is_same_basis)}")
    print(f"Alice's key               : {' '.join(str(alice.key[sum(is_same_basis[:i])]) if x else ' ' for i, x in enumerate(is_same_basis))}")
    print(f"Bob's key                 : {' '.join(str(bob.key[sum(is_same_basis[:i])]) if x else ' ' for i, x in enumerate(is_same_basis))}")
    print()

    chosen_compare = alice.get_chosen_compare(alice.n//2)
    alice_check_bits = alice.get_check_bits(chosen_compare)
    bob_check_bits = bob.get_check_bits(chosen_compare)

    alice.check(chosen_compare, alice_check_bits)
    bob.check(chosen_compare, bob_check_bits)

    print(f"Randomly chosen to compare: {' '.join('✓' if is_same_basis[i] and chosen_compare[sum(is_same_basis[:i])] else ' ' for i in range(n))}")
    print(f"Alice's chosen bits       : {' '.join(str(alice_check_bits[sum(chosen_compare[:sum(is_same_basis[:i])])]) if is_same_basis[i] and chosen_compare[sum(is_same_basis[:i])] else ' ' for i in range(n))}")
    print(f"Bob's chosen bits         : {' '.join(str(bob_check_bits[sum(chosen_compare[:sum(is_same_basis[:i])])]) if is_same_basis[i] and chosen_compare[sum(is_same_basis[:i])] else ' ' for i in range(n))}")

    if alice.key == None or bob.key == None:
        print("Chosen bits are not equal! Error!")
        return
    print("Success!")
    print(f"Key                       : {' '.join(str(alice.key[sum(not x for x in chosen_compare[:sum(is_same_basis[:i])])]) if is_same_basis[i] and not chosen_compare[sum(is_same_basis[:i])] else ' ' for i in range(n))}")

if __name__ == '__main__':
    n = int(input("N: "))
    gen_key(n)