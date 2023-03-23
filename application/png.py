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

        log.info("Read signature:\n %s", self.signature)
        return len(self.signature)

    def read_chunks(self):
        while self.file_png.peek() != b'':
            tmp = chunk.Chunk(self.file_png)
            self.chunks.append(tmp)

    def get_chunk_types(self) -> list:
        return [chunk.get_chunk_type() for chunk in self.chunks]
    
    def process_header(self) -> bool:
        chunk_types = self.get_chunk_types()
        index = chunk_types.index("IHDR")
        ret = self.chunks[index].process_hdr_data()
        log.debug(f"Printing IHDR dictionary: {self.chunks[index].get_hdr_data()}")
        if ret is False:
            log.error("IHDR processing gone wrong!")
            return False
        else:
            log.info("Header chunk processing OK")
        return True
    
    def process_palette(self) -> bool:
        chunk_types = self.get_chunk_types()
        index = chunk_types.index("PLTE")
        ret = self.chunks[index].process_plte_data()
        if ret is False:
            log.error("PLTE processing gone wrong!")
            return False
        else:
            log.info("Palette chunk processing OK")
        return True
    
    def process_ending(self) -> bool:
        chunk_types = self.get_chunk_types()
        index = chunk_types.index('IEND')
        ret = self.chunks[index].process_iend_data()
        if ret is False:
            log.error("IEND processing gone wrong!")
            return False
        else:
            log.info("Ending chunk processing OK")
        return True

