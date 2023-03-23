import logging as log
from chunk_class import *
# import numpy as np

"""
https://iter.ca/post/png/
https://www.w3.org/TR/PNG-Chunks.html
"""


def dictionary_len(my_dict: dict) -> int:
    return sum([len(x) for x in my_dict.values()])


class Png:
    signature = []
    chunks = list(Chunk)

    def __init__(self, file_png_name: str):
        try:
            self.file_png = open(file_png_name, 'rb')
        except:
            print("Failed to open file %s" % file_png_name)

    def __del__(self):
        if not self.file_png.closed:
            self.file_png.close()

    def __str__(self) -> str:
        return f"{len(self.signature)}"

    def get_signature(self) -> int:
        byte = b'0x00'
        while (byte := self.file_png.read(1)):
            self.signature.append(byte)
            if byte == b'\n':
                break
        log.debug("Read signature:\n %s", self.signature)
        return len(self.signature)

    def get_header(self) -> int:
        while (byte := self.file_png.read(1)):
            self.header["length"].append(byte)
            if byte == b'\n':
                break
        while (byte := self.file_png.read(1)):
            self.header["type"].append(byte)
            if byte == b'\n':
                break
        while (byte := self.file_png.read(1)):
            self.header["data"].append(byte)
            if byte == b'\n':
                break
        while (byte := self.file_png.read(1)):
            self.header["crc32"].append(byte)
            if byte == b'\n':
                break
        log.debug("Read header:\n %s", self.header)
        return dictionary_len(self.header)

    def get_data(self):
        pass

    def get_trailer(self) -> int:
        while (byte := self.file_png.read(1)):
            self.trailer["length"].append(byte)
            if byte == b'\n':
                break
        while (byte := self.file_png.read(1)):
            self.trailer["type"].append(byte)
            if byte == b'\n':
                break
        while (byte := self.file_png.read(1)):
            self.trailer["crc32"].append(byte)
            if byte == b'\n':
                break
        log.debug("Read trailer:\n %s", self.trailer)
        return dictionary_len(self.trailer)

    def process_signature(self) -> str:
        sign = ""
        for i in self.signature[1:5]:
            sign = sign + i.decode('ascii')
        return sign

    def process_header(self):
        pass
