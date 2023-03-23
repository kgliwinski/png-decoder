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
        if (self.chunk_type == 'IHDR'):
            self.__class__ = IHDR
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

    def get_chunk_type(self) -> str:
        """
        Get chunk type :D
        """
        return self.chunk_type


class IHDR(Chunk):
    img_data = {
        "width": int,
        "height": int,
        "bit_depth": int,
        "color_type": int,
        "color_type_str": str,
        "compression_method": int,
        "filter_method": int,
        "interlace_method": int
    }

    def __init__(self) -> None:
        pass

    def process_img_data(self) -> bool:
        """
        Processes the image data from raw bytes to img_data values,
        as well as determines decoded color_type, checks if given bit_depth
        is allowed with this color_type
        """
        self.img_data["width"] = int.from_bytes(self.chunk_data[0:4], 'big')
        self.img_data["height"] = int.from_bytes(self.chunk_data[4:8], 'big')
        self.img_data["bit_depth"] = int(self.chunk_data[8])
        self.img_data["color_type"] = int(self.chunk_data[9])
        self.img_data["compression_method"] = int(self.chunk_data[10])
        self.img_data["filter_method"] = int(self.chunk_data[11])
        self.img_data["interlace_method"] = int(self.chunk_data[12])
        if not self.color_type_to_str():
            return False


    def get_img_data(self) -> dict:
        return self.img_data

    def color_type_to_str(self) -> bool:
        color_num = self.img_data["color_type"]
        if color_num == 0:
            self.img_data["color_type_str"] = "Greyscale"
        elif color_num == 2:
            self.img_data["color_type_str"] = "Truecolour"
        elif color_num == 3:
            self.img_data["color_type_str"] = "Indexed-colour"
        elif color_num == 4:
            self.img_data["color_type_str"] = "Greyscale_with_alpha"
        elif color_num == 6:
            self.img_data["color_type_str"] = "Truecolour_with_alpha"
        else:
            log.error(
                "ERROR: Color code from IHDR is wrong and equals %d", color_num)
            return False
        return True
