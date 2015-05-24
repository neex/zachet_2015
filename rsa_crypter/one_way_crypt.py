from Crypto.PublicKey import RSA
import random
import midcrypt

class Cryptor(object):
    def __init__(self, n = None, e = None, mk = None):
        self.n = n
        self.e = e
        self.mk = mk
        if n == None:
            self.gen_new_n()

        if e == None:
            self.gen_new_e()

        if mk == None:
            self.gen_new_mk()

    def gen_new_n(self):
        RSAkey = RSA.generate(1024)
        self.n = RSAkey.key.n


    def gen_new_e(self):
        new_e = random.randint(1, self.n//3) * 2 + 1
        self.e = new_e

    def gen_new_mk(self):
        self.mk = bytearray(6)
        for i in xrange(6):
            self.mk[i] = random.randrange(0, 256)
        self.mk = bytes(self.mk)


    def do_encrypt(self, message):
        if len(message) != 16:
            raise ValueError("len(message) must be 16")

        crypted_text = midcrypt.midcrypt(self.mk, message)
        crypted_num = int(crypted_text.encode("hex"), 16)
        print crypted_num
        after_rsa = pow(crypted_num, self.e, self.n)
        return "n = {}\ne = {}\ncrypted = {}\n".format(self.n, self.e, after_rsa)
            


