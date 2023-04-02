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
        self.read_signature()
        self.read_chunks()
        self.process_header()
        self.process_palette()
        self.process_ending()

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

        plt.rcParams['figure.figsize'] = [4,3]
        plt.rcParams['figure.dpi'] = 200

        f1 = plt.figure(1)  # show source image and FFT
        plt.subplot(131), plt.imshow(img, cmap='gray')

        plt.title('Input Image'), plt.xticks([]), plt.yticks([])

        plt.subplot(132), plt.imshow(fourier_mag, cmap='gray')
        plt.title('FFT Magnitude'), plt.xticks([]), plt.yticks([])

        plt.subplot(133), plt.imshow(fourier_phase, cmap='gray')
        plt.title('FFT Phase'), plt.xticks([]), plt.yticks([])
        
        if save:
            plt.savefig(tmp_name + "_spectrum.png", dpi = 2000)
        
        f2 = plt.figure(2)  # comapare source image and inverted fft
        fourier_inverted = np.fft.ifft2(fourier)

        plt.subplot(121), plt.imshow(img, cmap='gray')
        plt.title('Input Image'), plt.xticks([]), plt.yticks([])
        plt.subplot(122), plt.imshow(np.asarray(
            fourier_inverted, dtype=np.uint8), cmap='gray')
        plt.title('Inverted Image'), plt.xticks([]), plt.yticks([])
        if save:
            plt.savefig(tmp_name + "_inverted.png", dpi = 2000)

        return (tmp_name + "_spectrum.png", tmp_name + "_inverted.png")