from AES_lib import AES128, gen_key


aes = AES128(gen_key())
s = "Олег is the best)"
sb = bytes(s, "utf-8")
chifertext = aes.encrypt(sb)
text = aes.decrypt(chifertext, len(sb)).decode() # len(sb), not len(s) - important for non-ASCII strings

print("s          =", s)
print("chifertext =", chifertext)
print("text       =", text)


# test memory leaks
# good if in task manager Python don't use increasing memory space
while True:
    AES128(gen_key())