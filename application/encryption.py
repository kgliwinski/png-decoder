import numpy as np
import sympy
import random
import chunk_class as chunk
import logging as log
import os
# https://github.com/Vipul97/des
# https://www.techtarget.com/searchsecurity/definition/Electronic-Code-Book
# https://en.wikipedia.org/wiki/RSA_(cryptosystem)
# https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation

class rsa2048:

    def __init__(self, chunks_to_encrypt: list, key_size: int = 1024, public_key: tuple = None, private_key: tuple = None):
        """ 
        # Chunk RSA2048 encryption
        User can provide public_key and private_key or generate new ones.
        ## Args:
            - png_type (png.Png): png object
            - public_key (tuple, optional): Defaults to None. (n, e)
            - private_key (tuple, optional): Defaults to None. (n, d)
        """

        self.key_size = key_size
        prime_size = key_size // 2
        if public_key is None:
            p = sympy.randprime(2**(prime_size - 1), 2**prime_size-1)
            q = sympy.randprime(2**(prime_size - 1), 2**prime_size-1)
            while p == q:
                q = sympy.randprime(2**(prime_size - 1), 2**prime_size-1)
            n = p * q
            phi = (p - 1) * (q - 1)
            e = sympy.randprime(2**(self.key_size - 1), 2**self.key_size)
            while sympy.gcd(e, phi) != 1 and e >= phi:
                e = sympy.randprime(2**(self.key_size - 1), 2**self.key_size)
            self.public_key = (n, e)
        else:
            self.public_key = public_key

        if private_key is None:
            d = sympy.mod_inverse(e, phi)
            self.private_key = (n, d)
        else:
            self.private_key = private_key

        self.ENCRYPT_BLOCK_SIZE = self.key_size // 8
        self.ENCRYPT_BLOCK_SIZE_SUBTRACT = self.ENCRYPT_BLOCK_SIZE - 1
        self.ENCRYPT_BLOCK_SIZE_CFB = 16

        self.chunks_to_encrypt = chunks_to_encrypt
        self.encrypted_pixels = []
        self.extra_bytes = b''

    def get_public_key(self) -> tuple:
        """ Returns public key"""
        return self.public_key

    def get_private_key(self) -> tuple:
        """ Returns private key"""
        return self.private_key

    def get_encrypted_pixels(self) -> bytes:
        """ Returns encrypted pixels"""
        return self.encrypted_pixels

    def get_decrypted_pixels(self) -> bytes:
        """ Returns decrypted pixels"""
        return self.decrypted_pixels

    # encrypt chunk using the Electronic codebook (ECB) mode
    def encrypt_ECB(self, data_to_encrypt: bytes):
        """ 
        # Encrypt chunk
        ## Args:
            - chunk (bytes): chunk to encrypt
        ## Returns:
            - bytes: encrypted chunk
        """

        encrypted_data = b''
        extra_data = b''

        data_to_encrypt_blocks = [data_to_encrypt[i:i + self.ENCRYPT_BLOCK_SIZE_SUBTRACT]
                                  for i in range(0, len(data_to_encrypt), self.ENCRYPT_BLOCK_SIZE_SUBTRACT)]

        for data_to_encrypt_block in data_to_encrypt_blocks:
            encrypted_int: int = pow(int.from_bytes(data_to_encrypt_block, byteorder='big'),
                                     self.public_key[1], self.public_key[0])
            encrypted_block = encrypted_int.to_bytes(
                self.ENCRYPT_BLOCK_SIZE, byteorder='big')

            if len(data_to_encrypt_block) < self.ENCRYPT_BLOCK_SIZE_SUBTRACT:
                self.encrypted_pixels += encrypted_block[0:len(
                    data_to_encrypt_block)]
                # self.extra_bytes += encrypted_block[len(data_to_encrypt_block):]
            else:
                self.encrypted_pixels += encrypted_block[0:
                                                         self.ENCRYPT_BLOCK_SIZE_SUBTRACT]
                extra_data += encrypted_block[self.ENCRYPT_BLOCK_SIZE_SUBTRACT:]

        return extra_data

    def encrypt_all_data_ECB(self, data_to_encrypt: bytes):
        """ 
        # Encrypt all chunks
        ## Returns:
            - list: list of encrypted chunks
        """
        self.encrypted_chunks = []
        self.extra_bytes = b''
        self.encrypted_pixels = []

        self.extra_bytes = self.encrypt_ECB(data_to_encrypt)
        # print(self.extra_bytes)
        # print(len(self.encrypted_pixels))
        return self.encrypted_chunks, self.extra_bytes

    def decrypt_ECB(self, data_to_decrypt: bytes):
        """ 
        # Decrypt chunk
        ## Args:
            - chunk (bytes): chunk to decrypt
        ## Returns:
            - bytes: decrypted chunk
        """
        decrypted_data = b''

        data_to_decrypt_blocks = [data_to_decrypt[i:i + self.ENCRYPT_BLOCK_SIZE]
                                  for i in range(0, len(data_to_decrypt), self.ENCRYPT_BLOCK_SIZE)]

        print(len(data_to_decrypt_blocks))
        for data_to_decrypt_block in data_to_decrypt_blocks:
            decrypted_int: int = pow(int.from_bytes(data_to_decrypt_block, byteorder='big'),
                                     self.private_key[1], self.private_key[0])

            if (len(data_to_decrypt_block) < self.ENCRYPT_BLOCK_SIZE):
                decrypted_data += decrypted_int.to_bytes(
                    len(data_to_decrypt_block), byteorder='big')
            else:
                decrypted_block = decrypted_int.to_bytes(
                    self.ENCRYPT_BLOCK_SIZE_SUBTRACT, byteorder='big')
                decrypted_data += decrypted_block

        return decrypted_data

    def decrypt_all_data_ECB(self, data_to_decrypt: bytes, extra_data: bytes):
        """ 
        # Decrypt all chunks
        ## Args:
            - encrypted_png_object (png.Png): encrypted png object
        ## Returns:
            - png.Png: decrypted png object
        """
        self.decrypted_chunks = []
        self.decrypted_pixels = []

        # insert extra data[i] to every ENCRYPT_BLOCK_SIZE_SUBTRACT byte
        data_to_decrypt_joined = b''
        # extra data not read
        for j, i in enumerate(range(0, len(data_to_decrypt), self.ENCRYPT_BLOCK_SIZE_SUBTRACT)):
            if j < len(extra_data):
                data_to_decrypt_joined += data_to_decrypt[i:i +
                                                          self.ENCRYPT_BLOCK_SIZE_SUBTRACT]
                data_to_decrypt_joined += extra_data[j:j+1]
            else:
                data_to_decrypt_joined += data_to_decrypt[i:i +
                                                          self.ENCRYPT_BLOCK_SIZE_SUBTRACT]

        # data_to_decrypt = zlib.decompress(all_idat_data)
        self.decrypted_pixels = self.decrypt_ECB(data_to_decrypt_joined)

        return self.decrypted_pixels

    def encrypt_block_CFB(self, data_to_encrypt_block, iv):
        """
        Output feedback encryption
        """
        encrypted_block = b''
        for i in range(len(data_to_encrypt_block)):
            encrypted_block += bytes([data_to_encrypt_block[i] ^ iv[i]])
        return encrypted_block

    def encrypt_CFB(self, data_to_encrypt: bytes, iv: bytes = None):
        """
        Output feedback encryption
        """
        # divide data into blocks
        data_to_encrypt_blocks = [data_to_encrypt[i:i + self.ENCRYPT_BLOCK_SIZE_CFB]
                                    for i in range(0, len(data_to_encrypt), self.ENCRYPT_BLOCK_SIZE_CFB)]
        
        # generate random IV
        if iv is None:
            iv = os.urandom(self.ENCRYPT_BLOCK_SIZE_CFB)

        original_iv = iv
        
        # self.encrypted_pixels += iv

        # encrypt blocks
        for data_to_encrypt_block in data_to_encrypt_blocks:
            encrypted_block = self.encrypt_block_CFB(data_to_encrypt_block, iv)
            self.encrypted_pixels += encrypted_block
            iv = encrypted_block
        
        return original_iv, self.encrypted_pixels
    
    def encrypt_all_data_CFB(self, data_to_encrypt: bytes, iv: bytes = None):
        """ 
        # Encrypt all chunks
        ## Returns:
            - list: list of encrypted chunks
        """
        self.encrypted_chunks = []
        self.extra_bytes = b''
        self.encrypted_pixels = []

        iv, self.encrypted_pixels = self.encrypt_CFB(data_to_encrypt, iv)
        # print(self.extra_bytes)
        # print(len(self.encrypted_pixels))
        return iv, self.encrypted_pixels
    
    def decrypt_block_CFB(self, encrypted_block, iv):
        """
        Decrypt a single block using CFB mode
        """
        decrypted_block = b''
        for i in range(len(encrypted_block)):
            decrypted_byte = encrypted_block[i] ^ iv[i]
            decrypted_block += bytes([decrypted_byte])
            
        iv = decrypted_block  # Update IV for next iteration
        return decrypted_block


    def decrypt_all_data_CFB(self, encrypted_data, iv):
        """
        Decrypt all blocks of encrypted data using CFB mode
        """
        decrypted_data = b''

        # Divide encrypted data into blocks
        encrypted_blocks = [encrypted_data[i:i + self.ENCRYPT_BLOCK_SIZE_CFB]
                            for i in range(0, len(encrypted_data), self.ENCRYPT_BLOCK_SIZE_CFB)]

        # Decrypt blocks
        for encrypted_block in encrypted_blocks:
            decrypted_block = self.decrypt_block_CFB(encrypted_block, iv)
            decrypted_data += decrypted_block
            iv = encrypted_block  # Use the encrypted block as IV for the next iteration

        return decrypted_data


    def get_encrypted_chunks(self) -> list:
        """ 
        # Get all chunks
        ## Returns:
            - list: list of all chunks
        """
        return self.encrypted_chunks

    def get_decrypted_chunks(self) -> list:
        """ 
        # Get all chunks
        ## Returns:
            - list: list of all chunks
        """
        return self.decrypted_chunks

    def get_extra_bytes(self) -> bytes:
        """ 
        # Get extra data
        ## Returns:
            - bytes: extra data
        """
        # print(self.extra_bytes)
        return self.extra_bytes
