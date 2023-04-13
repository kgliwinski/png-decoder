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
        self.process_header()
        self.process_palette()
        self.process_ending()
        self.process_gama()
        self.process_chrm()
        self.process_bkgd()
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

    def get_signature(self) -> bytes:
        return self.signature

    def get_chunk_types(self) -> list:
        return [chunk.get_chunk_type() for chunk in self.chunks]

    def get_ancilliary_dict(self) -> dict:
        return self.ancilliary_dict

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
                log.info("Updated CRC for chunk %s", i.get_chunk_type())
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

    def build_png_from_chunks(self, file_name: str) -> bool:
        with open(file_name, 'wb') as f:
            f.write(bytes(self.get_signature()))
            log.info("Signature: %s", self.get_signature())
            for i in self.chunks:
                f.write(i.all_chunk_data_to_bytes())

                log.info("Chunk type: %s", i.get_chunk_type())
        return True

    def get_deleted_chunks_number(self) -> int:
        return len(self.anomized_chunks)

    def get_deleted_chunks_list(self) -> list:
        return self.anomized_chunks

    def get_png_data_size(self) -> int:
        return super().get_png_data_size() - self.get_crc_saved_bytes()
