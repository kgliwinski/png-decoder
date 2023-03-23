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

        self.get_length()
        self.get_chunk_type()
        self.get_data()
        self.get_crc32()

    def get_length(self):

        length = self.file_ptr.read(4)

        log.debug(length)
        self.chunk_length = int.from_bytes(length, 'big', signed=False)
        log.debug(self.chunk_length)

    def get_chunk_type(self):
        chunk_type = b''

        chunk_type = self.file_ptr.read(4)
        log.debug(chunk_type)
        self.chunk_type = chunk_type.decode('ascii')
        log.debug(self.chunk_type)

    def get_data(self):

        data = self.file_ptr.read(self.chunk_length)
        log.debug(data)
        self.chunk_data = data

    def get_crc32(self):

        crc32 = self.file_ptr.read(4)

        log.debug(crc32)
        self.crc_32_value = int.from_bytes(crc32, 'big')
        log.debug(self.crc_32_value)
