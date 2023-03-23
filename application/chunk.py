"""
Contains the chunk class as well as child classes for 
several "special" chunks
"""
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
        """
        Initiates and reads all values for the class:
        - Chunk length (int)
        - Chunk type (str)
        - Chunk data (bytes)
        - Chunk crc32 (int)
        """
        self.file_ptr = file_ptr

        self.read_length()
        self.read_chunk_type()
        self.read_data()
        self.read_crc32()

    def read_length(self):
        """
        Gets the length of Chunk - first 4 bytes of chunk
        self.chunk_length is an int created from big-endian representation of
        consecutive bytes
        """

        length = self.file_ptr.read(self.LENGTH_FIELD_LEN)

        # log.debug(length)
        self.chunk_length = int.from_bytes(length, 'big', signed=False)
        log.debug("Chunk length: %d", self.chunk_length)

    def read_chunk_type(self):
        """
        Gets the type of chunk - str of 4 letters after chunk_length
        self.chunk_type is the decoding of the second 4 bytes to ascii
        """
        chunk_type = b''

        chunk_type = self.file_ptr.read(self.TYPE_FIELD_LEN)
        # log.debug(chunk_type)
        self.chunk_type = chunk_type.decode('ascii')
        log.debug("Chunk type: %s", self.chunk_type)

    def read_data(self):
        """
        Gets the data (chunk_length bytes after chunk_type), and stores
        it in the self.chunk_data list
        """
        data = self.file_ptr.read(self.chunk_length)
        self.chunk_data = data
        log.debug("Chunk data: %s", data)

    def read_crc32(self):
        """
        Gets the last 4 bytes of the chunk, which is the crc32
        self.crc32_value is the unsigned int as big endian 
        representation of the last 4 bytes
        """
        crc32 = self.file_ptr.read(self.CRC_FIELD_LEN)

        # log.debug(crc32)
        self.crc32_value = int.from_bytes(crc32, 'big')
        log.debug("Chunk crc32: %d", self.crc32_value)

    def get_length(self) -> int:
        """
        Get chunk length :D
        """
        return self.chunk_length

    def get_type(self) -> str:
        """
        Get chunk type :D
        """
        return self.chunk_type
