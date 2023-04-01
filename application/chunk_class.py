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
        if (self.chunk_type == 'IHDR'):
            self.__class__ = IHDR
        elif (self.chunk_type == 'PLTE'):
            self.__class__ = PLTE
        elif (self.chunk_type == 'IEND'):
            self.__class__ = IEND

    def read_length(self):
        """
        Gets the length of Chunk - first 4 bytes of chunk
        self.chunk_length is an int created from big-endian representation of
        consecutive bytes
        """

        length = self.file_ptr.read(self.LENGTH_FIELD_LEN)

        # log.debug(length)
        self.chunk_length = int.from_bytes(length, 'big', signed=False)
        log.info("Chunk length: %d", self.chunk_length)

    def read_chunk_type(self):
        """
        Gets the type of chunk - str of 4 letters after chunk_length
        self.chunk_type is the decoding of the second 4 bytes to ascii
        """
        chunk_type = b''

        chunk_type = self.file_ptr.read(self.TYPE_FIELD_LEN)
        # log.debug(chunk_type)
        self.chunk_type = chunk_type.decode('ascii')
        log.info("Chunk type: %s", self.chunk_type)

    def read_data(self):
        """
        Gets the data (chunk_length bytes after chunk_type), and stores
        it in the self.chunk_data list
        """
        data = self.file_ptr.read(self.chunk_length)
        self.chunk_data = data
        # log.info("Chunk data: %s", data)

    def read_crc32(self):
        """
        Gets the last 4 bytes of the chunk, which is the crc32
        self.crc32_value is the unsigned int as big endian 
        representation of the last 4 bytes
        """
        crc32 = self.file_ptr.read(self.CRC_FIELD_LEN)

        # log.debug(crc32)
        self.crc32_value = int.from_bytes(crc32, 'big')
        log.info("Chunk crc32: %d", self.crc32_value)

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
    hdr_data = {
        "width": int,
        "height": int,
        "bit_depth": int,
        "color_type": int,
        "color_type_str": str(None),
        "compression_method": int,
        "filter_method": int,
        "interlace_method": int
    }

    def __init__(self) -> None:
        pass

    def process_hdr_data(self) -> bool:
        """
        Processes the image data from raw bytes to hdr_data values,
        as well as determines decoded color_type, checks if given bit_depth
        is allowed with this color_type
        """
        self.hdr_data["width"] = int.from_bytes(self.chunk_data[0:4], 'big')
        self.hdr_data["height"] = int.from_bytes(self.chunk_data[4:8], 'big')
        self.hdr_data["bit_depth"] = int(self.chunk_data[8])
        self.hdr_data["color_type"] = int(self.chunk_data[9])
        self.hdr_data["compression_method"] = int(self.chunk_data[10])
        self.hdr_data["filter_method"] = int(self.chunk_data[11])
        self.hdr_data["interlace_method"] = int(self.chunk_data[12])
        if not self.color_type_to_str():
            return False
        if not self.check_bit_depth_by_color_type():
            return False

    def get_hdr_data(self) -> dict:
        return self.hdr_data

    def color_type_to_str(self) -> bool:
        """
        Sets hdr_data["color_type_str"] based on the color_type int

        Returns:
        True if possible to give str name, False otherwise
        """
        color_num = self.hdr_data["color_type"]
        if color_num == 0:
            self.hdr_data["color_type_str"] = "Greyscale"
        elif color_num == 2:
            self.hdr_data["color_type_str"] = "Truecolour"
        elif color_num == 3:
            self.hdr_data["color_type_str"] = "Indexed-colour"
        elif color_num == 4:
            self.hdr_data["color_type_str"] = "Greyscale_with_alpha"
        elif color_num == 6:
            self.hdr_data["color_type_str"] = "Truecolour_with_alpha"
        else:
            log.error(
                "ERROR: Color code from IHDR is wrong and equals %d", color_num)
            return False
        return True

    def check_bit_depth_by_color_type(self) -> bool:
        color_num = self.hdr_data["color_type"]
        b_d = self.hdr_data["bit_depth"]
        if color_num == 0 and b_d in (1, 2, 4, 8, 16):
            return True
        elif color_num == 3 and b_d in (1, 2, 4, 8):
            return True
        elif color_num in (2, 4, 6) and b_d in (8, 16):
            return True
        else:
            log.error(
                "ERROR: Given bit depth (%d) is not allowed when color_type is %s (%d)", self.hdr_data["bit_depth"], self.hdr_data["color_type_str"], self.hdr_data["color_type"])
            return False


class PLTE(Chunk):
    plte_data = []

    def __init__(self) -> None:
        pass

    def process_plte_data(self) -> None:
        if self.chunk_length % 3 != 0:
            return False
        for i in range(0, self.chunk_length, 3):
            self.plte_data.append(
                (self.chunk_data[i], self.chunk_data[i+1], self.chunk_data[i+2]))
        log.info(
            f"Printing the palette list of RGB tuples: {self.plte_data}, of length {len(self.plte_data)}")
        
    def get_plte_data(self) -> list:
        return self.plte_data


class IEND(Chunk):

    def __init__(self) -> None:
        pass

    def process_iend_data(self) -> bool:
        if self.chunk_length != 0:
            log.error(
                "ERROR: IEND should be of length 0, but its length is %d", self.chunk_length)
            return False
        return True
