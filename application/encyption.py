import numpy as np
import sympy
import random

# https://github.com/Vipul97/des
# https://www.techtarget.com/searchsecurity/definition/Electronic-Code-Book

class EncryptionRSA2048:
    def __init__(self):
        self.p = sympy.randprime(2**1023, 2**1024-1)
        self.q = sympy.nextprime(self.p)
