import numpy as np
import sympy
import random

# https://github.com/Vipul97/des
# https://www.techtarget.com/searchsecurity/definition/Electronic-Code-Book
# https://en.wikipedia.org/wiki/RSA_(cryptosystem)
 

class rsa2048:
    def __init__(self, chunks_to_encrypt : list, public_key : tuple = None, private_key : tuple = None): 
        """ 
        # Chunk RSA2048 encryption
        User can provide public_key and private_key or generate new ones.
        ## Args:
            - png_type (png.Png): png object
            - public_key (tuple, optional): Defaults to None. (n, e)
            - private_key (tuple, optional): Defaults to None. (n, d)
        """        
        if public_key is None:
            p = sympy.randprime(2**1023, 2**1024-1)
            q = sympy.nextprime(p)
            n = p * q
            phi = (p - 1) * (q - 1)
            e = sympy.randprime(2**15, 2**16-1)
            while sympy.gcd(e, phi) != 1 and e >= phi:
                e = sympy.randprime(2**15, 2**16-1)
            self.public_key = (n, e)
        else:
            self.public_key = public_key
        
        if private_key is None:
            d = sympy.mod_inverse(e, phi)
            self.private_key = (n, d)
        else:
            self.private_key = private_key

        self.chunks_to_encrypt = chunks_to_encrypt
    
    def get_public_key(self) -> tuple:
        """ Returns public key"""
        return self.public_key
    
    def get_private_key(self) -> tuple:
        """ Returns private key"""
        return self.private_key
    
    def encrypt_chunk(self, chunk : bytes) -> bytes:
        """ 
        # Encrypt chunk
        ## Args:
            - chunk (bytes): chunk to encrypt
        ## Returns:
            - bytes: encrypted chunk
        """        
        chunk_int = int.from_bytes(chunk, byteorder='big')
        encrypted_chunk_int : int = pow(chunk_int, self.public_key[1], self.public_key[0])
        encrypted_chunk = encrypted_chunk_int.to_bytes(256, byteorder='big')
        return encrypted_chunk

    def encrypt_all_chunks(self) -> list:
        """ 
        # Encrypt all chunks
        ## Returns:
            - list: list of encrypted chunks
        """        
        self.encrypted_chunks = []
        for chunk in self.chunks_to_encrypt:
            self.encrypted_chunks.append(self.encrypt_chunk(chunk))
        return self.encrypted_chunks
    
    def decrypt_chunk(self, chunk : bytes) -> bytes:
        """ 
        # Decrypt chunk
        ## Args:
            - chunk (bytes): chunk to decrypt
        ## Returns:
            - bytes: decrypted chunk
        """        
        chunk_int = int.from_bytes(chunk, byteorder='big')
        decrypted_chunk_int = pow(chunk_int, self.private_key[1], self.private_key[0])
        decrypted_chunk = decrypted_chunk_int.to_bytes(256, byteorder='big')
        return decrypted_chunk
    
    def decrypt_all_chunks(self) -> list:
        """ 
        # Decrypt all chunks
        ## Returns:
            - list: list of decrypted chunks
        """        
        decrypted_chunks = []
        for chunk in self.chunks_to_encrypt:
            decrypted_chunks.append(self.decrypt_chunk(chunk))
        return decrypted_chunks
    
    def get_encrypted_chunks(self) -> list:
        """ 
        # Get all chunks
        ## Returns:
            - list: list of all chunks
        """        
        return self.encrypted_chunks
    
