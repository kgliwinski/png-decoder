"""
https://iter.ca/post/png/
https://www.w3.org/TR/PNG-chunk.Chunks.html
"""
import logging as log
import chunk


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
        self.chunks.append(chunk.Chunk(self.file_png))

    def get_chunks(self):
        while self.file_png.peek() is not b'':
            try:
                self.chunks.append(chunk.Chunk(self.file_png))
            except:
                print("Everything was read")
                break
