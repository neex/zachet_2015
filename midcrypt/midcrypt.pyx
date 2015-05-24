cdef extern from "midcrypt_cpp.h":
    void midcrypt_cpp "midcrypt" (unsigned char key[6], unsigned char in_[16], unsigned char out[16])

def midcrypt(key, text):
    cdef:
          unsigned char crypted_c[16]
          unsigned char plain_c[16]
          unsigned char key_c[6]
          int i
    if not isinstance(key, bytes) or not isinstance(text, bytes):
        raise ValueError("key and text must be bytes")

    if len(key) != 6:
        raise ValueError("len(key) must be equal 6")

    if len(text) != 16:
        raise ValueError("len(text) must be equal 16")


    for i in xrange(6):
        key_c[i] = ord(key[i])

    for i in xrange(16):
        plain_c[i] = ord(text[i])

    midcrypt_cpp(key_c, plain_c, crypted_c)

    crypted = bytearray(16)
    for i in xrange(16):
        crypted[i] = crypted_c[i]

    return bytes(crypted)
