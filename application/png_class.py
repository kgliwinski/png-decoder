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
    chunks = []

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

        self.signature = self.file_png.read(8)

        log.debug("Read signature:\n %s", self.signature)
        return len(self.signature)

    def get_header(self) -> int:
        self.chunks.append(Chunk(self.file_png))
        # log.debug("Read header:\n %s", self.header)
        # return dictionary_len(self.header)

    def get_chunks(self):
        while(self.file_png.peek() is not b''):
            try:
                self.chunks.append(Chunk(self.file_png))
            except:
                print("Everything was read")
                break
