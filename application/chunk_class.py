import logging as log

class Chunk:
    """
    Class for representing base chunks in PNG format:
    - 4 bytes: Length of chunk
    - 4 bytes: Type of chunk, i.e. IHDR, PLTE, IDAT
    - Length bytes: Chunk data
    - 4 bytes: CRC32
    """
    LENGTH_FIELD_LEN = 4
    TYPE_FIELD_LEN = 4
    CRC_FIELD_LEN = 4

    def __init__(self, file_ptr) -> None:
        self.file_ptr = file_ptr
        byte = b'0x00'
        length = self.file_ptr.read(4)
        log.debug(length)
        type = self.file_ptr.read(4)
        log.debug(type)
        