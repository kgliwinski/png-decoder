"""
https://iter.ca/post/png/
https://www.w3.org/TR/PNG-chunk.Chunks.html
"""
import logging as log
import chunk


class Png:
    """
    Contains the PNG file signature and chunkss
    """
    signature = []
    chunks = []

    def __init__(self, file_png_name: str):
        try:
            self.file_png = open(file_png_name, 'rb')
        except:
            print("Failed to open file %s", file_png_name)

    def __del__(self):
        if not self.file_png.closed:
            self.file_png.close()

    def __str__(self) -> str:
        # ret = [chunk.get_type() for chunk in self.chunks]
        return f"{self.get_chunk_types()}"

    def read_signature(self) -> int:

        self.signature = self.file_png.read(8)

        log.debug("Read signature:\n %s", self.signature)
        return len(self.signature)

    def read_chunks(self):
        while self.file_png.peek() != b'':
            tmp = chunk.Chunk(self.file_png)
            self.chunks.append(tmp)

    def get_chunk_types(self) -> list:
        return [chunk.get_type() for chunk in self.chunks]
