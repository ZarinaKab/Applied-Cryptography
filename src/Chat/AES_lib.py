import ctypes as C

from random import randint


try:
    lib = C.CDLL('.\\AES_lib.dll', winmode=0x8)
except FileNotFoundError:
    lib = C.CDLL('.\\src\\Chat\\AES_lib.dll', winmode=0x8)

AES_KEY_LEN = 16
AES_BLOCK_LEN = 16

def gen_key(key = None):
    '''
        If key == None: generate new key
        else: set key values from list[int]
    '''
    res = (C.c_ubyte * AES_KEY_LEN)()
    for i in range(AES_KEY_LEN):
        res[i] = (randint(0, 255) if key == None else key[i])
    return res


class AES128(object):
    def __init__(self, key):
        ctor = lib.AES128_new
        ctor.restype = C.c_void_p
        ctor.argtypes = [C.POINTER(C.c_ubyte)]
        self.obj = ctor(key)

        fun = lib.AES128_encrypt
        fun.restype = None
        fun.argtypes = [C.c_void_p, C.c_char_p, C.c_size_t, C.c_char_p]
        self.enc = fun

        fun = lib.AES128_decrypt
        fun.restype = None
        fun.argtypes = [C.c_void_p, C.c_char_p, C.c_size_t, C.c_char_p]
        self.dec = fun

        fun = lib.AES128_delete
        fun.restype = None
        fun.argtypes = [C.c_void_p]
        self.delet = fun

    def encrypt(self, text):
        """
            text - bytes object only
        """
        text_len = len(text)
        chifertext_len = ((text_len + AES_BLOCK_LEN - 1) // AES_BLOCK_LEN) * AES_BLOCK_LEN
        res = C.create_string_buffer(chifertext_len)
        self.enc(self.obj, text, text_len, res)
        return res.raw
    
    def decrypt(self, chifertext):
        """
            chifertext - bytes object to  decrypt
        """
        chifertext_len = len(chifertext)
        res = C.create_string_buffer(len(chifertext))
        self.dec(self.obj, chifertext, chifertext_len, res)
        return res.raw

    def __del__(self):
        self.delet(self.obj)