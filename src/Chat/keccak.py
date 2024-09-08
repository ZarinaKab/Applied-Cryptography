class Keccak:
    def __init__(self, rate, capacity, input_bytes, padding_byte):
        if rate + capacity != 1600 or rate%8:
            raise ValueError
        
        # prepare constants
        self._rho = [[0]*5 for _ in range(5)]
        x, y = 1, 0
        for t in range(1, 25):
            self._rho[x][y] = t*(t+1)//2
            x, y = y, (2*x + 3*y)%5

        self._R = [0]*25
        R = 1
        for round in range(25):
            for j in range(7):
                R = ((R << 1) ^ ((R >> 7) * 0x71)) % 256
                if R & 2:
                    self._R[round] ^= (1 << ((1 << j) - 1))

        self._rate = rate // 8
        self._state = [[0]*5 for _ in range(5)]
        for i, byte in enumerate(input_bytes):
            self._add_to_state(i % self._rate, byte)
            if i+1 == self._rate: # block filled, need to hash
                self._keccak_f()
        self._add_to_state(len(input_bytes) % self._rate, padding_byte)
        self._add_to_state(self._rate - 1, 0x80) # end of padding

    def _add_to_state(self, pos, byte):
        arr_pos = pos // 8
        byte <<= 8 * (pos % 8) # shift to position on lane
        self._state[arr_pos % 5][arr_pos // 5] ^= byte

    @staticmethod
    def _rot64(a, n):
        n %= 64
        return ((a >> (64 - n)) | (a << n)) & ((1 << 64) - 1)

    def _keccak_f(self):
        state = self._state
        R = 1
        for round in range(24):
            # θ
            C = [state[x][0] ^ state[x][1] ^ state[x][2] ^ state[x][3] ^ state[x][4] for x in range(5)]
            D = [C[(x + 4) % 5] ^ Keccak._rot64(C[(x + 1) % 5], 1) for x in range(5)]
            state = [[state[x][y] ^ D[x] for y in range(5)] for x in range(5)]
            # ρ and π
            new_state = [[0]*5 for _ in range(5)]
            for x in range(5):
                for y in range(5):
                    new_state[y][(2*x + 3*y)%5] = Keccak._rot64(state[x][y], self._rho[x][y])
            state = new_state
            # χ
            for y in range(5):
                T = [state[x][y] for x in range(5)]
                for x in range(5):
                    state[x][y] = T[x] ^ ((~T[(x + 1) % 5]) & T[(x + 2) % 5])
            # ι
            state[0][0] ^= self._R[round]
        self._state = state

    def hash(self, byte_len):
        res = bytearray()
        while byte_len > len(res):
            self._keccak_f()
            byte_state = b''.join(self._state[i%5][i//5].to_bytes(8, 'little') for i in range(25))
            res += byte_state[:min(byte_len - len(res), self._rate)]
        return bytes(res)

def shake_128(input_bytes, output_byte_len):
    return Keccak(1344, 256, input_bytes, 0x1F).hash(output_byte_len)

def shake_256(input_bytes, output_byte_len):
    return Keccak(1088, 512, input_bytes, 0x1F).hash(output_byte_len)

def sha3_224(input_bytes):
    return Keccak(1152, 448, input_bytes, 0x06).hash(224 // 8)

def sha3_256(input_bytes):
    return Keccak(1088, 512, input_bytes, 0x06).hash(256 // 8)

def sha3_384(input_bytes):
    return Keccak( 832, 768, input_bytes, 0x06).hash(384 // 8)

def sha3_512(input_bytes):
    return Keccak(576, 1024, input_bytes, 0x06).hash(512 // 8)

def tests():
    import hashlib
    names = ['sha3_224', 'sha3_256', 'sha3_384', 'sha3_512', 'shake_128', 'shake_256']
    def test_str(s):
        s = s.encode()
        hashlib.sha3_224(b'')
        for func in ('sha3_224', 'sha3_256', 'sha3_384', 'sha3_512'):
            our = eval(f"{func}(s)")
            ans = eval(f"hashlib.{func}(s)").digest()
            assert our == ans, f'{func}({s})'

    test_str('')
    test_str('The quick brown fox jumps over the lazy dog')
    test_str('The quick brown fox jumps over the lazy dog.')
    print("Tests passed successfully")

def keccak_main():
    from_file = input("Choose file: ")
    with open(from_file, 'rb') as ff:
        fff = ff.read()
    return sha3_256(fff)

if __name__ == "__main__":
    tests()
    from_file = input("Choose file: ")
    with open(from_file, 'rb') as ff:
        fff = ff.read()
    h = sha3_256(fff)
    print(f"Hash value is {hex(int.from_bytes(h, 'big'))[2:]}")

