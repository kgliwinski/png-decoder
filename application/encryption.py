import numpy as np
import sympy
import random
import chunk_class as chunk
import logging as log
import zlib
# https://github.com/Vipul97/des
# https://www.techtarget.com/searchsecurity/definition/Electronic-Code-Book
# https://en.wikipedia.org/wiki/RSA_(cryptosystem)


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

        self.ENCRYPT_BLOCK_SIZE = self.key_size // 8
        self.ENCRYPT_BLOCK_SIZE_SUBTRACT = self.ENCRYPT_BLOCK_SIZE - 1

        self.chunks_to_encrypt = chunks_to_encrypt
        self.encrypted_pixels = []

    def get_public_key(self) -> tuple:
        """ Returns public key"""
        return self.public_key

    def get_private_key(self) -> tuple:
        """ Returns private key"""
        return self.private_key

    def get_encrypted_pixels(self) -> bytes:
        """ Returns encrypted pixels"""
        return self.encrypted_pixels

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

            encrypted_data += encrypted_block[0:
                                              self.ENCRYPT_BLOCK_SIZE_SUBTRACT]
            extra_data += encrypted_block[self.ENCRYPT_BLOCK_SIZE_SUBTRACT:]
            self.encrypted_pixels += encrypted_block[0:self.ENCRYPT_BLOCK_SIZE_SUBTRACT]
            # self.encrypted_pixels += encrypted_block[0:self.ENCRYPT_BLOCK_SIZE]

        # chunk_to_encrypt.replace_idat_data(encrypted_data)
        return extra_data

    def encrypt_all_chunks_ECB(self):
        """ 
        # Encrypt all chunks
        ## Returns:
            - list: list of encrypted chunks
        """
        self.encrypted_chunks = []
        self.extra_bytes = b''

        all_idat_data = b''
        for chunk_to_encrypt in self.chunks_to_encrypt:
            all_idat_data += chunk_to_encrypt.get_chunk()

        data_to_encrypt = zlib.decompress(all_idat_data)

        extra_bytes_part = self.encrypt_ECB(data_to_encrypt)
        self.extra_bytes += extra_bytes_part
        print(len(self.encrypted_pixels))
        return self.encrypted_chunks, self.extra_bytes

    def decrypt_chunk(self, chunk: chunk.Chunk) -> chunk.Chunk:
        """ 
        # Decrypt chunk
        ## Args:
            - chunk (bytes): chunk to decrypt
        ## Returns:
            - bytes: decrypted chunk
        """
        chunk_int = int.from_bytes(chunk.get_chunk(), byteorder='big')
        decrypted_chunk_int = pow(
            chunk_int, self.private_key[1], self.private_key[0])
        chunk.replace_chunk_data(decrypted_chunk_int.to_bytes(
            self.ENCRYPT_BLOCK_SIZE, byteorder='big'))
        return chunk

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

    def get_extra_bytes(self) -> bytes:
        """ 
        # Get extra data
        ## Returns:
            - bytes: extra data
        """
        return self.extra_bytes
