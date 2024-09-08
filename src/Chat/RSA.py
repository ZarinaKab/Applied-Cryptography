import random, math, sympy

class RSA:
    def __init__(self, n, e=None, d=None):
        '''
            n = RSA modulus 
            d = private key
            e = public key
        '''
        self.n = n
        self.d = d
        self.e = e

    @staticmethod
    def extgcd(a: int, b: int):
        '''
            Realization of Extended Euclidean algorithm from egcd python module
            Find x, y such that a*x + b*y = gcd(a, b)
            Return tuple of (gcd(a, b), x, y)
        '''    
        (x0, x1, y0, y1) = (1, 0, 0, 1)
        while b != 0:
            q, a, b = (a // b, b, a % b)
            x0, x1 = (x1, x0 - q * x1)
            y0, y1 = (y1, y0 - q * y1)
        return (a, x0, y0)

    @staticmethod
    def generate_key(key_len: int):
        '''
            Generate keys for RSA. Each prime in range (sqrt(2^key_len), 2^key_len)
            Return tuple (n, e, d), where (n, e) is public key, (n, d) - private
        '''
        lower_bound = 2**(key_len//4)
        upper_bound = 2**(key_len//2)
        gen_prime = lambda: sympy.randprime(lower_bound, upper_bound)

        p = gen_prime()
        while True:
            q = gen_prime()
            if p != q:
                break
        
        n = p*q
        phi = math.lcm(p-1, q-1)

        while True:
            e = random.randint(3, phi-1)
            cur_gcd, d, _ = RSA.extgcd(e, phi)
            if cur_gcd == 1:
                break
        d = (d%phi + phi)%phi
        return (n, e, d)

    def encrypt(self, plaintext: bytes):
        if self.e == None:
            raise RuntimeError("Private key is unspecified")
        chifered = (pow(x, self.e, self.n) for x in plaintext) # encrypt
        bytes_chifered = (x.to_bytes(self.len_n(), "big") for x in chifered) # encode to bytes array
        return bytes().join(bytes_chifered) # concatenate

    def decrypt(self, ciphertext: bytes):
        if self.d == None:
            raise RuntimeError("Public key is unspecified")
        # split bytes in segments, each of length of RSA modulus
        splitted = (ciphertext[i:i+self.len_n()] for i in range(0, len(ciphertext), self.len_n()))
        ints = (int.from_bytes(x, "big") for x in splitted) # convert to ints
        return bytes(pow(x, self.d, self.n) for x in ints) # decrypt
    
    def len_n(self):
        # ceil division
        return (self.n.bit_length() + 7) // 8

def save(n, e, d):
    with open("public.key", "w") as f:
        f.write(str(n) + ", " + str(e))

    with open("private.key", "w") as f:
        f.write(str(n) + ", " + str(d))

def main():
    choise = input("What do you want? (enc/dec/gen) ")
    if choise == "gen":
        key_len = int(input("Enter lenght of keys: "))
        print("...Generating...")
        n, e, d = RSA.generate_key(key_len) 
        save(n, e, d)
        print("Done!")

    elif choise == "enc":
        from_path = input("Enter the path to the file to encrypt: ")
        to_path = input("Enter the path to the file to save: ")

        with open(from_path, "rb") as f:
            plaintext = f.read()

        print("...Encrypting...")

        with open("public.key", "r") as f:
            n, e = map(int, f.read().split(", "))

        ciphertext = RSA(n, e=e).encrypt(plaintext)

        with open(to_path, "wb") as f:
            f.write(ciphertext)

        print("Done!")

    elif choise == "dec":
        from_path = input("Enter the path to encrypted file: ")
        to_path = input("Enter the path to the file to save: ")
        with open(from_path, "rb") as f:
            ciphertext = f.read()

        print("...Decrypting...")
        
        with open("private.key", "r") as f:
            n, d = map(int, f.read().split(", "))

        plaintext = RSA(n, d=d).decrypt(ciphertext)
        with open(to_path, "wb") as f:
            f.write(plaintext)
        print("Done!")

    else:
        print("!!!!Incorrect Input!!!!")

if __name__ == "__main__":
    main()