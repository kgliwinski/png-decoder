"""
https://iter.ca/post/png/
https://www.w3.org/TR/png/
https://www.nayuki.io/page/png-file-chunk-inspector
"""
import logging as log
import chunk_class as chunk
import matplotlib.pyplot as plt
import numpy as np
import cv2 as cv
from encryption import rsa2048
import png
import zlib


class Png:
    """
    Contains the PNG file signature and chunkss
    """

    def __init__(self, file_png_name: str):
        self.file_png_name = file_png_name
        try:
            self.file_png = open(file_png_name, 'rb')
        except:
            log.error("Failed to open file %s", file_png_name)
            raise Exception("File error")
        self.signature = []
        self.chunks = []
        self.ancilliary_dict = {}
        self.read_signature()
        self.read_chunks()
        self.read_after_iend_data()
        self.process_header()
        self.process_idat()
        self.process_palette()
        self.process_ending()
        self.process_gama()
        self.process_chrm()
        self.process_bkgd()
        self.process_srgb()
        self.process_hist()
        self.process_exif()
        # if self.assert_chunks() is False:
        # log.error("Chunk assertion failed!")
        # raise Exception("Chunk assertion failed!")
        log.info("Ancilliary dictionary: %s", self.ancilliary_dict)

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
            if tmp.get_chunk_type() == 'IEND':
                break

    def read_after_iend_data(self):
        self.after_iend_data = b''
        while self.file_png.peek() != b'':
            self.after_iend_data += self.file_png.read(1)

    def get_signature(self) -> bytes:
        return self.signature

    def get_chunk_types(self) -> list:
        return [chunk.get_chunk_type() for chunk in self.chunks]

    def get_ancilliary_dict(self) -> dict:
        return self.ancilliary_dict

    def get_all_idat_chunks(self) -> list:
        return [chunk for chunk in self.chunks if chunk.get_chunk_type() == 'IDAT']

    def get_ihdr_chunk(self) -> chunk.Chunk:
        return [chunk for chunk in self.chunks if chunk.get_chunk_type() == 'IHDR'][0]

    def get_after_iend_data(self) -> bytes:
        return self.after_iend_data

    def check_if_plte_exists(self) -> bool:
        return 'PLTE' in self.get_chunk_types()

    def assert_chunks(self) -> bool:
        """
        Checks if all chunks are valid
        """
        for chunk in self.chunks:
            print("Asserting chunk: ", chunk.get_chunk_type())
            if chunk.assert_chunk() is False:
                log.error("Chunk %s is invalid!", chunk.get_chunk_type())
                return False
        return True

    def process_header(self) -> bool:
        chunk_types = self.get_chunk_types()
        index = chunk_types.index("IHDR")
        ret = self.chunks[index].process_hdr_data()
        log.debug(
            f"Printing IHDR dictionary: {self.chunks[index].get_hdr_data()}")
        if ret is False:
            log.error("IHDR processing gone wrong!")
            return False
        else:
            log.info("Header chunk processing OK")
        return True

    def process_palette(self) -> bool:
        chunk_types = self.get_chunk_types()
        try:
            index = chunk_types.index("PLTE")
        except:
            log.info("No PLTE section in this image!")
            return False
        ret = self.chunks[index].process_plte_data()
        if ret is False:
            log.error("PLTE processing gone wrong!")
            return False
        else:
            log.info("Palette chunk processing OK")
        return True

    def process_idat(self) -> bool:
        chunk_types = self.get_chunk_types()
        for i, type in enumerate(chunk_types):
            if type == 'IDAT':
                self.chunks[i].divide_chunk_into_sections()
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

    def process_gama(self) -> bool:
        chunk_types = self.get_chunk_types()
        try:
            index = chunk_types.index('gAMA')
        except:
            log.info("No gAMA section in this image!")
            return False
        ret = self.chunks[index].process_gama_data()
        if ret is False:
            log.error("gAMA processing gone wrong!")
            return False
        else:
            log.info("gAMA chunk processing OK")
        self.ancilliary_dict['gAMA'] = self.chunks[index].get_gama_data()
        return True

    def process_chrm(self) -> bool:
        chunk_types = self.get_chunk_types()
        try:
            index = chunk_types.index('cHRM')
        except:
            log.info("No cHRM section in this image!")
            return False
        ret = self.chunks[index].process_chrm_data()
        if ret is False:
            log.error("cHRM processing gone wrong!")
            return False
        else:
            log.info("cHRM chunk processing OK")
        self.ancilliary_dict['cHRM'] = self.chunks[index].get_chrm_data()
        return True

    def process_bkgd(self) -> bool:
        chunk_types = self.get_chunk_types()
        try:
            index = chunk_types.index('bKGD')
        except:
            log.info("No bKGD section in this image!")
            return False
        ret = self.chunks[index].process_bkgd_data()
        if ret is False:
            log.error("bKGD processing gone wrong!")
            return False
        else:
            log.info("bKGD chunk processing OK")
        self.ancilliary_dict['bKGD'] = self.chunks[index].get_bkgd_data()
        return True

    def process_srgb(self) -> bool:
        chunk_types = self.get_chunk_types()
        try:
            index = chunk_types.index('sRGB')
        except:
            log.info("No sRGB section in this image!")
            return False
        ret = self.chunks[index].process_srgb_data()
        if ret is False:
            log.error("sRGB processing gone wrong!")
            return False
        else:
            log.info("sRGB chunk processing OK")
        self.ancilliary_dict['sRGB'] = self.chunks[index].get_srgb_data()
        return True

    def process_exif(self) -> bool:
        chunk_types = self.get_chunk_types()
        try:
            index = chunk_types.index('eXIf')
        except:
            log.info("No eXIf section in this image!")
            return False
        ret = self.chunks[index].process_exif_data()
        if ret is False:
            log.error("eXIf processing gone wrong!")
            return False
        else:
            log.info("eXIf chunk processing OK")
        self.ancilliary_dict['eXIf'] = self.chunks[index].get_exif_data()
        return True

    def process_hist(self) -> bool:
        chunk_types = self.get_chunk_types()
        try:
            index = chunk_types.index('hIST')
        except:
            log.info("No hIST section in this image!")
            return False
        ret = self.chunks[index].process_hist_data()
        if ret is False:
            log.error("hIST processing gone wrong!")
            return False
        else:
            log.info("hIST chunk processing OK")
        self.ancilliary_dict['hIST'] = self.chunks[index].get_hist_data()
        return True

    def process_exif(self) -> bool:
        chunk_types = self.get_chunk_types()
        try:
            index = chunk_types.index('eXIf')
        except:
            log.info("No eXIf section in this image!")
            return False
        ret = self.chunks[index].process_exif_data()
        if ret is False:
            log.error("eXIf processing gone wrong!")
            return False
        else:
            log.info("eXIf chunk processing OK")
        self.ancilliary_dict['eXIf'] = self.chunks[index].get_exif_data()
        return True

    def get_all_chunk_numbers(self) -> dict:
        my_dict = {i: self.get_chunk_types().count(
            i) for i in self.get_chunk_types()}
        crit_chunks = ['IHDR', 'PLTE', 'IDAT', 'IEND']
        for i in crit_chunks:
            if i not in my_dict:
                my_dict[i] = 0

        return my_dict

    def check_critical_chunk_numbers(self) -> bool:
        chunk_num_dict = self.get_all_chunk_numbers()
        if 'IHDR' not in chunk_num_dict or chunk_num_dict['IHDR'] != 1:
            log.error(
                "Wrong number of IHDR chunks in image: is %d, should be 1", chunk_num_dict['IHDR'])
            return False
        elif chunk_num_dict['IEND'] != 1:
            log.error(
                "Wrong number of IEND chunks in image: is %d, should be 1", chunk_num_dict['IEND'])
            return False
        elif chunk_num_dict['IDAT'] <= 0:
            log.error(
                "Wrong number of IDAT chunks in image: is %d, should be at least 1", chunk_num_dict['IDAT'])
            return False
        elif 'PLTE' in chunk_num_dict and chunk_num_dict['PLTE'] > 1:
            return False
        return True

    def get_header(self) -> chunk or None:
        chunk_types = self.get_chunk_types()
        index = chunk_types.index("IHDR")
        return self.chunks[index]

    def get_plte(self) -> chunk:
        chunk_types = self.get_chunk_types()
        try:
            index = chunk_types.index("PLTE")
        except:
            log.info("No PLTE section in this image!")
            return None
        return self.chunks[index]

    def get_exif(self) -> chunk.Chunk:
        chunk_types = self.get_chunk_types()
        try:
            index = chunk_types.index("eXIf")
        except:
            log.info("No eXIf section in this image!")
            return None
        return self.chunks[index]

    def get_fourier_transform(self, tmp_name: str = ".tmp/temp", save: bool = False):
        """ Print FFT of an image (shows magnitude and phase)
            Compare original image and inverted fft of original image (checks transformation)
        """
        img = cv.imread(self.file_png_name, 0)
        fourier = np.fft.fft2(img)
        fourier_shifted = np.fft.fftshift(fourier)

        fourier_mag = np.asarray(
            20*np.log10(np.abs(fourier_shifted)), dtype=np.uint8)
        fourier_phase = np.asarray(np.angle(fourier_shifted), dtype=np.uint8)

        plt.rcParams['figure.figsize'] = [4, 3]
        plt.rcParams['figure.dpi'] = 200

        f1 = plt.figure(1)  # show source image and FFT
        plt.subplot(131), plt.imshow(img, cmap='gray')

        plt.title('Input Image'), plt.xticks([]), plt.yticks([])

        plt.subplot(132), plt.imshow(fourier_mag, cmap='gray')
        plt.title('FFT Magnitude'), plt.xticks([]), plt.yticks([])

        plt.subplot(133), plt.imshow(fourier_phase, cmap='gray')
        plt.title('FFT Phase'), plt.xticks([]), plt.yticks([])

        if save:
            plt.savefig(tmp_name + "_spectrum.png", dpi=2000)

        f2 = plt.figure(2)  # comapare source image and inverted fft
        fourier_inverted = np.fft.ifft2(fourier)

        plt.subplot(121), plt.imshow(img, cmap='gray')
        plt.title('Input Image'), plt.xticks([]), plt.yticks([])
        plt.subplot(122), plt.imshow(np.asarray(
            fourier_inverted, dtype=np.uint8), cmap='gray')
        plt.title('Inverted Image'), plt.xticks([]), plt.yticks([])
        if save:
            plt.savefig(tmp_name + "_inverted.png", dpi=200)

        return (tmp_name + "_spectrum.png", tmp_name + "_inverted.png")

    def get_png_data_size(self) -> int:
        return sum([i.get_chunk_size() for i in self.chunks])

    def get_ancilliary_chunks(self) -> list:
        chunk_types = self.chunks
        ancilliary_chunks = []
        for i in chunk_types:
            if i.get_chunk_type() not in ['IHDR', 'PLTE', 'IDAT', 'IEND']:
                ancilliary_chunks.append(i)
                log.info("Found ancilliary chunk: %s", i.get_chunk_type())
        return ancilliary_chunks

    def build_png_from_chunks(self, file_name: str) -> bool:
        with open(file_name, 'wb') as f:
            f.write(bytes(self.get_signature()))
            log.info("Signature: %s", self.get_signature())
            for i in self.chunks:
                f.write(i.all_chunk_data_to_bytes())

                # log.info("Chunk type: %s", i.get_chunk_type())
        return True

    def get_first_idat_chunk_index(self) -> int:
        chunk_types = self.get_chunk_types()
        return chunk_types.index('IDAT')

    def replace_idat_chunks(self, new_idat_chunks: list) -> bool:
        """ Replaces IDAT chunks with new ones
            If there are no IDAT chunks, returns false
        """
        chunk_types = self.get_chunk_types()
        if 'IDAT' in chunk_types:
            first_idat_index = self.get_first_idat_chunk_index()
            self.chunks = self.chunks[:first_idat_index] + \
                new_idat_chunks + \
                self.chunks[first_idat_index+len(new_idat_chunks):]
        else:
            return False

        return True


class AnomizedPng(Png):
    def __init__(self, file_png_name: str):
        super().__init__(file_png_name)
        self.anomized_chunks = []
        self.crc_saved_bytes = 0
        self.remove_aucilliary_chunks()
        self.update_crcs()
        log.info("%s", self.__str__())
        log.info("Anomized PNG created")

    def __str__(self) -> str:
        return super().__str__() + "Anomized chunks: " + str(self.anomized_chunks)

    def remove_aucilliary_chunks(self) -> bool:
        chunk_types = self.get_chunk_types()
        for i in chunk_types:
            if i not in ['IHDR', 'PLTE', 'IDAT', 'IEND']:
                self.anomized_chunks.append(i)
                self.remove_chunk(i)
        log.info("Removed %d chunks from image", len(self.anomized_chunks))
        return True

    def update_crcs(self) -> bool:
        for i in self.chunks:
            if i.replace_crc(b'pppp') == True:
                self.crc_saved_bytes += chunk.Chunk.CRC_FIELD_LEN
                log.debug("Updated CRC for chunk %s", i.get_chunk_type())
            else:
                log.error("Failed to update CRC for chunk %s",
                          i.get_chunk_type())
        return True

    def get_crc_saved_bytes(self) -> int:
        return self.crc_saved_bytes

    def remove_chunk(self, chunk_type: str) -> bool:
        chunk_types = self.get_chunk_types()
        try:
            index = chunk_types.index(chunk_type)
        except:
            log.info("No %s section in this image!", chunk_type)
            return False
        self.chunks.pop(index)
        return True

    def get_deleted_chunks_number(self) -> int:
        return len(self.anomized_chunks)

    def get_deleted_chunks_list(self) -> list:
        return self.anomized_chunks

    def get_png_data_size(self) -> int:
        return super().get_png_data_size() - self.get_crc_saved_bytes()


class EncryptedPng(Png):
    def __init__(self, file_png_name: str, public_key=None, private_key=None):
        super().__init__(file_png_name)
        if self.assert_file() == False:
            exit(1)
        idat_chunks = self.get_all_idat_chunks()
        self.rsa_2048 = rsa2048(
            idat_chunks, public_key=public_key, private_key=private_key)
        # self.encrypt_ecb()
        # self.build_png_from_chunks(
        # ".tmp/encrypted.png", pixels=self.rsa_2048.get_encrypted_pixels())

    def __str__(self) -> str:
        return super().__str__() + "Encrypted PNG created"

    def assert_file(self) -> bool:
        if self.check_if_plte_exists() == True:
            log.error("Encryption does not support PLTE!")
            return False
        return True

    def encrypt_ecb(self, png_path_str: str):
        data_to_encrypt = self.get_and_prepare_data_to_process()
        self.rsa_2048.encrypt_all_data_ECB(data_to_encrypt)
        self.after_iend_data = self.rsa_2048.get_extra_bytes()
        self.build_png_from_chunks(png_path_str, pixels=self.rsa_2048.get_encrypted_pixels(),
                                   after_iend_data=self.rsa_2048.get_extra_bytes())
        return self.rsa_2048.get_private_key()

    def decrypt_ecb(self, png_path_str: str):
        extra_data = self.get_after_iend_data()
        data_to_decrypt = self.get_and_prepare_data_to_process()
        self.rsa_2048.decrypt_all_data_ECB(data_to_decrypt, extra_data)
        self.replace_idat_chunks(self.rsa_2048.get_decrypted_chunks())
        self.build_png_from_chunks(
            png_path_str, pixels=self.rsa_2048.get_decrypted_pixels(), after_iend_data=b'')

    def encrypt_cfb(self, png_path_str: str, iv: bytes = None):
        data_to_encrypt = self.get_and_prepare_data_to_process()
        iv, _ = self.rsa_2048.encrypt_all_data_CFB(data_to_encrypt, iv)
        self.after_iend_data = self.rsa_2048.get_extra_bytes()
        self.build_png_from_chunks(png_path_str, pixels=self.rsa_2048.get_encrypted_pixels(),
                                   after_iend_data=self.rsa_2048.get_extra_bytes())
        return iv

    def decrypt_cfb(self, png_path_str: str, iv: bytes):
        extra_data = self.get_after_iend_data()
        data_to_decrypt = self.get_and_prepare_data_to_process()
        decrypted_pixels = self.rsa_2048.decrypt_all_data_CFB(
            data_to_decrypt, iv)
        # self.replace_idat_chunks(self.rsa_2048.get_decrypted_chunks())
        self.build_png_from_chunks(
            png_path_str, pixels=decrypted_pixels, after_iend_data=b'')

    def encrypt_aes_ecb(self, png_path_str, public_key):
        data_to_encrypt = self.get_and_prepare_data_to_process()
        extra, data = self.rsa_2048.encrypt_all_data_AES_ECB(
            data_to_encrypt, public_key=public_key)
        self.build_png_from_chunks(png_path_str, pixels=data,
                                   after_iend_data=extra)

    def build_png_from_chunks(self, file_name: str, pixels, after_iend_data) -> bool:
        writer = self.get_png_writer()
        print(self.get_width(), self.get_height())
        row_width = self.get_width() * self.calculate_bytes_per_pixel()
        pixels_by_rows = [pixels[i:i+row_width]
                          for i in range(0, len(pixels), row_width)]
        for row in pixels_by_rows:
            if len(row) < row_width and type(row) == list:
                row.extend([0]*(row_width-len(row)))
        with open(file_name, 'wb') as f:
            writer.write(f, pixels_by_rows)
            # write after iend data as well
            f.write(after_iend_data)
        return True

    def get_png_writer(self) -> png.Writer:
        bytes_per_pixel = self.calculate_bytes_per_pixel()
        bit_depth = self.get_bit_depth()
        if bytes_per_pixel == 1:
            png_writer = png.Writer(
                self.get_width(), self.get_height(), greyscale=True, bitdepth=bit_depth)
        elif bytes_per_pixel == 2:
            png_writer = png.Writer(
                self.get_width(), self.get_height(), greyscale=True, alpha=True, bitdepth=bit_depth)
        elif bytes_per_pixel == 3:
            png_writer = png.Writer(
                self.get_width(), self.get_height(), greyscale=False, bitdepth=bit_depth)
        elif bytes_per_pixel == 4:
            png_writer = png.Writer(self.get_width(), self.get_height(),
                                    greyscale=False, alpha=True, bitdepth=bit_depth)
        else:
            png_writer = png.Writer(self.get_width(), self.get_height(),
                                    greyscale=False, alpha=True, bitdepth=bit_depth)
        return png_writer

    def get_bit_depth(self):
        # get the bit_depth from ihdr chunk
        return self.get_ihdr_chunk().get_hdr_data()["bit_depth"]

    def get_color_type(self):
        return self.get_ihdr_chunk().get_hdr_data()["color_type"]

    def get_width(self):
        return self.get_ihdr_chunk().get_hdr_data()["width"]

    def get_height(self):
        return self.get_ihdr_chunk().get_hdr_data()["height"]

    def calculate_bytes_per_pixel(self):
        color_type_to_bytes_per_pixel_ratio = {
            0: 1,
            2: 3,
            3: 1,
            4: 2,
            6: 4
        }
        return color_type_to_bytes_per_pixel_ratio[self.get_color_type()]

    def get_and_prepare_data_to_process(self):
        all_idat_data = b''
        for chunk_to_encrypt in self.get_all_idat_chunks():
            all_idat_data += chunk_to_encrypt.get_chunk()
        bytes_per_pixel = self.calculate_bytes_per_pixel()
        width = self.get_width()
        height = self.get_height()

        all_idat_data = zlib.decompress(all_idat_data)
        assert len(all_idat_data) == height * \
            (1 + width * bytes_per_pixel), "Corrupted data"

        return self.defilter_data(all_idat_data)

    def defilter_data(self, data_to_defilter: bytes):
        bytes_per_pixel = self.calculate_bytes_per_pixel()
        width = self.get_width()
        height = self.get_height()
        stride = width * bytes_per_pixel

        reconstructed_idat_data = b''

        def paeth_predictor(a, b, c):
            """The Paeth Predictor computes a simple linear function of the three neighboring pixels (left, above, upper left),
            then chooses as predictor the neighboring pixel closest to the computed value.
            This technique is due to Alan W. Paeth [1]."""
            p = a + b - c
            pa = abs(p - a)
            pb = abs(p - b)
            pc = abs(p - c)
            if pa <= pb and pa <= pc:
                Pr = a
            elif pb <= pc:
                Pr = b
            else:
                Pr = c
            return Pr

        def recon_a(r, c):
            return reconstructed_idat_data[r * stride + c - bytes_per_pixel] if c >= bytes_per_pixel else 0

        def recon_b(r, c):
            return reconstructed_idat_data[(r-1) * stride + c] if r > 0 else 0

        def recon_c(r, c):
            return reconstructed_idat_data[(r-1) * stride + c - bytes_per_pixel] if r > 0 and c >= bytes_per_pixel else 0

        i = 0
        # print(stride * height, len(data_to_defilter))
        for r in range(height):
            filter_type = data_to_defilter[i]
            i += 1
            for c in range(stride):
                filt_x = data_to_defilter[i]
                i += 1
                if filter_type == 0:  # None
                    recon_x = filt_x
                elif filter_type == 1:  # Sub
                    recon_x = filt_x + recon_a(r, c)
                elif filter_type == 2:  # Up
                    recon_x = filt_x + recon_b(r, c)
                elif filter_type == 3:  # Average
                    recon_x = filt_x + (recon_a(r, c) + recon_b(r, c)) // 2
                elif filter_type == 4:  # Paeth
                    recon_x = filt_x + \
                        paeth_predictor(
                            recon_a(r, c), recon_b(r, c), recon_c(r, c))
                else:
                    log.error(filter_type)
                    raise Exception('Invalid filter type')
                reconstructed_idat_data += bytes([recon_x & 0xFF])
                # print(i)
        return reconstructed_idat_data
    
    def return_keys(self):
        return self.rsa_2048.get_public_key(), self.rsa_2048.get_private_key()
