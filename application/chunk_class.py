"""
Contains the chunk class as well as child classes for 
several "special" chunks
"""
import logging as log
from typing import List, Dict, Tuple, Union


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
        elif (self.chunk_type == 'IDAT'):
            self.__class__ = IDAT
        elif (self.chunk_type == 'PLTE'):
            self.__class__ = PLTE
        elif (self.chunk_type == 'IEND'):
            self.__class__ = IEND
        elif (self.chunk_type == 'gAMA'):
            self.__class__ = gAMA
        elif (self.chunk_type == 'cHRM'):
            self.__class__ = cHRM
        elif (self.chunk_type == 'sRGB'):
            self.__class__ = sRGB
        elif (self.chunk_type == 'eXIf'):
            self.__class__ = eXIf
        elif (self.chunk_type == 'bKGD'):
            self.__class__ = bKGD
        elif (self.chunk_type == 'hIST'):
            self.__class__ = hIST

    def read_length(self):
        """
        Gets the length of Chunk - first 4 bytes of chunk
        self.chunk_length is an int created from big-endian representation of
        consecutive bytes
        """

        self.raw_length = self.file_ptr.read(self.LENGTH_FIELD_LEN)

        # log.debug(length)
        self.chunk_length = int.from_bytes(
            self.raw_length, 'big', signed=False)
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
        self.crc32 = self.file_ptr.read(self.CRC_FIELD_LEN)

        # log.debug(crc32)
        self.crc32_value = int.from_bytes(self.crc32, 'big')
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

    def get_chunk(self) -> bytes:
        """
        Get chunk data :D
        """

        return self.chunk_data

    def all_chunk_data_to_bytes(self) -> bytes:
        """
        Returns all chunk data as bytes
        """
        return self.raw_length + self.chunk_type.encode('ascii') + self.chunk_data + self.crc32_value.to_bytes(self.CRC_FIELD_LEN, 'big')

    def get_chunk_size(self) -> int:
        """
        Get chunk size :D
        """
        return self.chunk_length + self.LENGTH_FIELD_LEN + self.TYPE_FIELD_LEN + self.CRC_FIELD_LEN

    def replace_crc(self, new_crc: bytes) -> bool:
        """
        Replaces the current crc32 value with a new one
        """
        if len(new_crc) != self.CRC_FIELD_LEN:
            return False
        self.crc32 = new_crc
        return True
    
    def replace_chunk_data(self, new_data : bytes) -> bool:
        """
        Replaces the current chunk data with a new one
        """
        self.chunk_data = new_data
        return True


class IDAT(Chunk):
    
    def __init__(self, file_ptr) -> None:
        pass

    def encrypt_data_rsa2048(self, public_key: bytes) -> bool:
        """
        Encrypts the data of the chunk with RSA 2048
        """
        pass
    

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


class gAMA(Chunk):
    def __init__(self) -> None:
        pass

    def process_gama_data(self) -> bool:
        if self.chunk_length != 4:
            log.error(
                "ERROR: gAMA should be of length 4, but its length is %d", self.chunk_length)
            return False
        self.gamma = float(int.from_bytes(self.chunk_data, 'big')) / 100000
        log.info(f"Gamma value: {self.gamma}")
        return True

    def get_gama_data(self) -> float:
        return self.gamma


class cHRM(Chunk):
    def __init__(self) -> None:
        pass

    def process_chrm_data(self) -> bool:
        if self.chunk_length != 32:
            log.error(
                "ERROR: cHRM should be of length 32, but its length is %d", self.chunk_length)
            return False
        self.white_point_x = float(int.from_bytes(
            self.chunk_data[0:4], 'big')) / 100000
        self.white_point_y = float(int.from_bytes(
            self.chunk_data[4:8], 'big')) / 100000
        self.red_x = float(int.from_bytes(
            self.chunk_data[8:12], 'big')) / 100000
        self.red_y = float(int.from_bytes(
            self.chunk_data[12:16], 'big')) / 100000
        self.green_x = float(int.from_bytes(
            self.chunk_data[16:20], 'big')) / 100000
        self.green_y = float(int.from_bytes(
            self.chunk_data[20:24], 'big')) / 100000
        self.blue_x = float(int.from_bytes(
            self.chunk_data[24:28], 'big')) / 100000
        self.blue_y = float(int.from_bytes(
            self.chunk_data[28:32], 'big')) / 100000
        log.info(
            f"White point x: {self.white_point_x}, y: {self.white_point_y}")
        log.info(f"Red x: {self.red_x}, y: {self.red_y}")
        log.info(f"Green x: {self.green_x}, y: {self.green_y}")
        log.info(f"Blue x: {self.blue_x}, y: {self.blue_y}")
        return True

    def get_chrm_data(self) -> dict:
        return {"white_point_x": self.white_point_x, "white_point_y": self.white_point_y, "red_x": self.red_x, "red_y": self.red_y, "green_x": self.green_x, "green_y": self.green_y, "blue_x": self.blue_x, "blue_y": self.blue_y}


class bKGD(Chunk):
    def __init__(self) -> None:
        pass

    def process_bkgd_data(self) -> bool:
        if self.chunk_length not in (1, 2, 6):
            log.error(
                "ERROR: bKGD should be of length 2 or 6, but its length is %d", self.chunk_length)
            return False
        if self.chunk_length == 1:
            self.background = self.chunk_data[0]
            log.info(f"Background color: {self.background}")
        elif self.chunk_length == 2:
            self.background = int.from_bytes(self.chunk_data, 'big')
            log.info(f"Background color: {self.background}")
        else:
            self.background = (int.from_bytes(self.chunk_data[0:2], 'big'),
                               int.from_bytes(self.chunk_data[2:4], 'big'),
                               int.from_bytes(self.chunk_data[4:6], 'big'))
            log.info(f"Background color: {self.background}")
        return True

    def get_bkgd_data(self) -> Union[int, tuple]:
        return self.background


class sRGB(Chunk):
    def __init__(self) -> None:
        pass

    def process_srgb_data(self) -> bool:
        if self.chunk_length != 1:
            log.error(
                "ERROR: sRGB should be of length 1, but its length is %d", self.chunk_length)
            return False
        self.rendering_intent = int.from_bytes(self.chunk_data, 'big')
        log.info(f"Rendering intent: {self.rendering_intent}")
        return True

    def get_srgb_data(self) -> int:
        return self.rendering_intent


class hIST(Chunk):
    def __init__(self) -> None:
        pass

    def process_hist_data(self) -> bool:
        if self.chunk_length % 2 != 0:
            log.error(
                "ERROR: hIST should be of even length, but its length is %d", self.chunk_length)
            return False
        self.histogram = []
        for i in range(0, self.chunk_length, 2):
            self.histogram.append(int.from_bytes(
                self.chunk_data[i:i+2], 'big'))
        log.info(f"Printing the histogram list: {self.histogram}")
        return True

    def get_hist_data(self) -> list:
        return self.histogram


class eXIf(Chunk):
    def __init__(self) -> None:
        pass

    def process_exif_data(self) -> bool:
        if self.chunk_length <= 0:
            log.error(
                "ERROR: eXIF should be of length at least 6, but its length is %d", self.chunk_length)
            return False
        self.exif_endian = self.chunk_data[0:2]
        if self.exif_endian != b'II' and self.exif_endian != b'MM':
            log.error(
                "ERROR: eXIF should start with II or MM, but it starts with %s", self.exif_endian)
            return False
        elif self.exif_endian == b'II':
            self.exif_endian_str = 'Little endian'
        else:
            self.exif_endian_str = 'Big endian'

        self.exif_fourty_two = int.from_bytes(self.chunk_data[2:4], 'big')
        if self.exif_fourty_two != 42:
            log.error(
                "ERROR: eXIF should have 42 as the next two bytes, but it has %d", self.exif_fourty_two)
            return False
        print(
            f"Exif endian: {self.exif_endian_str}, Exif data: {self.exif_fourty_two}")
        return True

    def get_exif_data(self) -> dict:
        return {"exif_endian": self.exif_endian_str, "exif_fourty_two": self.exif_fourty_two}
