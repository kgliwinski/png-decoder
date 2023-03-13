import logging as log
# import numpy as np

"""
https://iter.ca/post/png/
"""


class Png:
    signature = []
    header = {
        "length": [],
        "type": [],
        "data": [],
        "crc32": []
    }
    trailer = {
        "length" : [],
        "type" : [],
        "crc32": []
    }
    bytes = []
    # file_png = ''

    def __init__(self, file_png_name: str):
        self.file_png = open(file_png_name, 'rb')

    def __del__(self):
        if not self.file_png.closed:
            self.file_png.close()

    def __str__(self) -> str:
        return f"{len(self.signature)}"

    def get_signature(self):
        byte = b'0x00'
        while (byte := self.file_png.read(1)):
            self.signature.append(byte)
            if byte == b'\n':
                break
        log.debug("Read signature:\n %s\n", self.signature)
        return len(self.signature)

    def get_header(self):
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
        log.debug("Read header:\n %s\n", self.header)

    def get_trailer(self):
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
        log.debug("Read trailer:\n %s\n", self.trailer)
