import numpy as np
import sympy
import random

# https://github.com/Vipul97/des
# https://www.techtarget.com/searchsecurity/definition/Electronic-Code-Book
# https://pl.wikipedia.org/wiki/RSA_(kryptografia)


class EncryptionRSA2048:
    def __init__(self):
        self.p = sympy.randprime(2**1023, 2**1024-1)
        self.q = sympy.nextprime(self.p)
        self.n = self.p * self.q
        self.phi = (self.p - 1) * (self.q - 1)
        self.e = sympy.randprime(2**15, 2**16-1)
        while sympy.gcd(self.e, self.phi) != 1 and self.e >= self.phi:
            self.e = sympy.randprime(2**15, 2**16-1)
        self.d = sympy.mod_inverse(self.e, self.phi)

        self.public_key = (self.n, self.e)
        self.private_key = (self.n, self.d)
    
    def get_public_key(self) -> tuple:
        return self.public_key
    