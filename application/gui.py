
import cv2 as cv
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QTabWidget, QPlainTextEdit, QScrollArea
from PyQt6.QtGui import QImage, QPixmap
from PyQt6 import QtCore
import png_class as png
from chunk_class import IHDR, PLTE
import glob
from matplotlib.backends.backend_qt import FigureCanvasQT as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
# from os import listdir


class MainWindow(QMainWindow):

    IMG_HEIGHT = 400
    IMG_WIDTH = 800
    GRAPH_WIDTH_AND_HEIGHT = 400

    png_type: png = None

    def __init__(self):
        super().__init__()
        self.tab_widget = QTabWidget(self)
        self.setCentralWidget(self.tab_widget)

        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tab4 = QWidget()

        self.tab_widget.addTab(self.tab1, "IHDR and image")
        self.tab_widget.addTab(self.tab2, "PLTE")
        self.tab_widget.addTab(self.tab3, "FFT")
        self.tab_widget.addTab(self.tab4, "Ancilliary chunks")

        self.tab_widget.setTabBarAutoHide(True)

        self.create_ihdr_tab()
        self.create_plte_tab()
        self.create_fft_tab()
        self.create_ancilliary_chunks_tab()

        self.showMaximized()

    def create_ihdr_tab(self):
        # Create widgets
        self.png_input_label = QLabel("PNG path")
        self.png_input_field = QComboBox(self.tab1)
        self.png_input_field.setGeometry(QtCore.QRect(10, 10, 150, 30))
        self.png_input_field.setEditable(True)
        self.png_input_field.setPlaceholderText("Select PNG file or type path")

        # Populate dropdown list with options
        for file in glob.iglob('**/*.png', recursive=True):
            # if file[-4:].casefold() == '.png'.casefold():
            self.png_input_field.addItem(file)

        self.display_image_label = QLabel("Image preview")
        self.display_image_label.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignCenter)
        self.width_label = QLabel("Width:")
        self.width_field = QLineEdit(self.tab1)
        self.width_field.setReadOnly(True)
        self.height_label = QLabel("Height:")
        self.height_field = QLineEdit(self.tab1)
        self.height_field.setReadOnly(True)
        self.bit_depth_label = QLabel("Bit depth:")
        self.bit_depth_field = QLineEdit(self.tab1)
        self.bit_depth_field.setReadOnly(True)
        self.color_type_label = QLabel("Color type:")
        self.color_type_field = QLineEdit(self.tab1)
        self.color_type_field.setReadOnly(True)
        self.compression_method_label = QLabel("Compression method:")
        self.compression_method_field = QLineEdit(self.tab1)
        self.compression_method_field.setReadOnly(
            True)
        self.filter_method_label = QLabel("Filter method:")
        self.filter_method_field = QLineEdit(self.tab1)
        self.filter_method_field.setReadOnly(True)
        self.interlace_method_label = QLabel("Interlace method:")
        self.interlace_method_field = QLineEdit(self.tab1)
        self.interlace_method_field.setReadOnly(True)
        self.submit_button = QPushButton("Submit")

        # Create layout for the first column
        column1_layout = QVBoxLayout()
        column1_layout.addWidget(self.png_input_label)
        column1_layout.addWidget(self.png_input_field)
        column1_layout.addWidget(self.width_label)
        column1_layout.addWidget(self.width_field)
        column1_layout.addWidget(self.height_label)
        column1_layout.addWidget(self.height_field)
        column1_layout.addWidget(self.bit_depth_label)
        column1_layout.addWidget(self.bit_depth_field)

        # Create layout for the second column
        column2_layout = QVBoxLayout()
        column2_layout.addWidget(self.color_type_label)
        column2_layout.addWidget(self.color_type_field)
        column2_layout.addWidget(self.compression_method_label)
        column2_layout.addWidget(self.compression_method_field)
        column2_layout.addWidget(self.filter_method_label)
        column2_layout.addWidget(self.filter_method_field)
        column2_layout.addWidget(self.interlace_method_label)
        column2_layout.addWidget(self.interlace_method_field)
        self.submit_button.clicked.connect(self.display_image_and_hdr_data)

        # Create layout
        png_input_layout = QHBoxLayout()
        png_input_layout.addWidget(self.png_input_label)
        png_input_layout.addWidget(self.png_input_field)

        ihdr_layout = QVBoxLayout()
        ihdr_layout.addWidget(self.width_label)
        ihdr_layout.addWidget(self.width_field)
        ihdr_layout.addWidget(self.height_label)
        ihdr_layout.addWidget(self.height_field)
        ihdr_layout.addWidget(self.bit_depth_label)
        ihdr_layout.addWidget(self.bit_depth_field)
        ihdr_layout.addWidget(self.color_type_label)
        ihdr_layout.addWidget(self.color_type_field)
        ihdr_layout.addWidget(self.compression_method_label)
        ihdr_layout.addWidget(self.compression_method_field)
        ihdr_layout.addWidget(self.filter_method_label)
        ihdr_layout.addWidget(self.filter_method_field)
        ihdr_layout.addWidget(self.interlace_method_label)
        ihdr_layout.addWidget(self.interlace_method_field)

        # Create layout for the IHDR fields
        ihdr_layout = QHBoxLayout()
        ihdr_layout.addLayout(column1_layout)
        ihdr_layout.addLayout(column2_layout)

        # Create main layout
        tab1_layout = QVBoxLayout()
        tab1_layout.addLayout(ihdr_layout)
        tab1_layout.addWidget(self.submit_button)
        tab1_layout.addWidget(self.display_image_label)
        tab1_layout.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft)

        # Set main layout
        self.tab1.setLayout(tab1_layout)

    def create_plte_tab(self):
        self.palette_size_label = QLabel("Palette size:")
        self.palette_size_field = QLineEdit(self.tab2)
        self.palette_size_field.setReadOnly(True)
        self.palette_data_label = QLabel("Palette data:")
        self.palette_data_field = QPlainTextEdit(self.tab2)
        self.palette_data_field.lineWrapMode()
        self.palette_data_field.setReadOnly(True)

        tab2_layout = QVBoxLayout()
        tab2_layout.addWidget(self.palette_size_label)
        tab2_layout.addWidget(self.palette_size_field)
        tab2_layout.addWidget(self.palette_data_label)
        tab2_layout.addWidget(self.palette_data_field)
        tab2_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.tab2.setLayout(tab2_layout)

    def create_fft_tab(self):
        self.fft_original_image_darkscale_label = QLabel(
            "Original image darkscale:")
        # make it width size but height is dynamic
        self.fft_original_image_darkscale_label.setFixedSize(
            self.GRAPH_WIDTH_AND_HEIGHT, self.GRAPH_WIDTH_AND_HEIGHT)

        self.fft_original_image_darkscale_label.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignHCenter)

        self.fft_spectrum_label = QLabel("FFT spectrum:")
        self.fft_spectrum_label.setFixedSize(
            self.GRAPH_WIDTH_AND_HEIGHT, self.GRAPH_WIDTH_AND_HEIGHT)
        self.fft_spectrum_label.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignHCenter)

        self.fft_phase_label = QLabel("FFT phase:")
        self.fft_phase_label.setFixedSize(
            self.GRAPH_WIDTH_AND_HEIGHT, self.GRAPH_WIDTH_AND_HEIGHT)
        self.fft_phase_label.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignHCenter)

        self.fft_original_image_inverted_label = QLabel(
            "Original image inverted:")
        self.fft_original_image_inverted_label.setFixedSize(
            self.GRAPH_WIDTH_AND_HEIGHT, self.GRAPH_WIDTH_AND_HEIGHT)
        self.fft_original_image_inverted_label.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignHCenter)

        # fft as above for the inverted image
        self.fft_inverted_spectrum_label = QLabel(
            "FFT spectrum inverted:")
        self.fft_inverted_spectrum_label.setFixedSize(
            self.GRAPH_WIDTH_AND_HEIGHT, self.GRAPH_WIDTH_AND_HEIGHT)
        self.fft_inverted_spectrum_label.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignHCenter)

        self.fft_inverted_phase_label = QLabel("FFT phase inverted:")
        self.fft_inverted_phase_label.setFixedSize(
            self.GRAPH_WIDTH_AND_HEIGHT, self.GRAPH_WIDTH_AND_HEIGHT)
        self.fft_inverted_phase_label.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignHCenter)

        # create two horizontal layouts
        self.line_one = QHBoxLayout()
        self.line_one.addWidget(self.fft_original_image_darkscale_label)
        self.line_one.addWidget(self.fft_spectrum_label)
        self.line_one.addWidget(self.fft_phase_label)
        self.line_one.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignHCenter)

        self.line_two = QHBoxLayout()
        self.line_two.addWidget(self.fft_original_image_inverted_label)
        self.line_two.addWidget(self.fft_inverted_spectrum_label)
        self.line_two.addWidget(self.fft_inverted_phase_label)
        self.line_two.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignHCenter)
        
        tab3_layout = QVBoxLayout()
        tab3_layout.addLayout(self.line_one)
        tab3_layout.addLayout(self.line_two)
        tab3_layout.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignHCenter)

        self.tab3.setLayout(tab3_layout)

    def create_ancilliary_chunks_tab(self):
        self.gama_label = QLabel("gAMA:")
        self.gama_field = QPlainTextEdit(self.tab4)
        self.gama_field.setReadOnly(True)

        self.chrm_label = QLabel("cHRM:")
        self.chrm_field = QPlainTextEdit(self.tab4)
        self.chrm_field.setReadOnly(True)

        self.srgb_label = QLabel("bKGD:")
        self.srgb_field = QPlainTextEdit(self.tab4)
        self.srgb_field.setReadOnly(True)

        tab4_layout = QVBoxLayout()
        tab4_layout.addWidget(self.gama_label)
        tab4_layout.addWidget(self.gama_field)
        tab4_layout.addWidget(self.chrm_label)
        tab4_layout.addWidget(self.chrm_field)
        tab4_layout.addWidget(self.srgb_label)
        tab4_layout.addWidget(self.srgb_field)
        tab4_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.tab4.setLayout(tab4_layout)

    def display_image_and_hdr_data(self):
        self.png_path = self.png_input_field.currentText()
        print(self.png_path)
        # Load image with OpenCV
        image = cv.imread(self.png_path)

        # Display image
        if image is not None:
            if self.png_type is not None:
                self.png_type = None
            image = cv.cvtColor(image, cv.COLOR_BGR2RGB)
            height, width, channel = image.shape
            bytes_per_channel = channel * (image.dtype.itemsize)
            qimage = QImage(image.data, width, height,
                            bytes_per_channel * width, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qimage)
            pixmap = pixmap.scaled(self.IMG_WIDTH, self.IMG_HEIGHT,
                                   aspectRatioMode=QtCore.Qt.AspectRatioMode.KeepAspectRatio)
            self.display_image_label.setPixmap(pixmap)
            self.display_image_label.setAlignment(
                QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignHCenter)
            self.load_image_values()
        else:
            self.display_image_label.setText("Unable to load image")

    def load_image_values(self):
        try:
            self.png_type = png.Png(self.png_path)
            print(self.png_type)
            self.png_input_label.setText("PNG path:")
            hdr = self.png_type.get_header()
            self.update_fields_from_header(hdr)
            plte = self.png_type.get_plte()
            if plte is not None:
                self.update_fields_from_plte(plte)
            else:
                self.palette_size_field.setText("PLTE chunk not found")
                self.palette_data_field.setPlainText("None")
            self.update_fourier_transform()
        except:
            self.png_input_label.setText("PNG Path: Invalid file name!")
            pass

    def update_fields_from_header(self, hdr: IHDR):
        data = hdr.get_hdr_data()
        self.width_field.setText(str(data["width"]))
        self.height_field.setText(str(data["height"]))
        self.bit_depth_field.setText(str(data["bit_depth"]))
        self.color_type_field.setText(str(data["color_type_str"]))
        self.compression_method_field.setText(str(data["compression_method"]))
        self.filter_method_field.setText(str(data["filter_method"]))
        self.interlace_method_field.setText(str(data["interlace_method"]))

    def update_fields_from_plte(self, plte: PLTE):
        data = plte.get_plte_data()
        self.palette_size_field.setText(str(len(data)))
        palette_data = ''
        for dat in data:
            palette_data += str(dat) + '\n'

        self.palette_data_field.insertPlainText(str(palette_data))

    def update_fourier_transform(self):
        # plot a phase and magnintude spectrum using pyqtgraph
        img = cv.imread(self.png_path, cv.IMREAD_GRAYSCALE)
        pixmap = QPixmap.fromImage(QImage(img, img.shape[1], img.shape[0], img.strides[0],
                                          QImage.Format.Format_Grayscale8))
        pixmap = pixmap.scaled(self.GRAPH_WIDTH_AND_HEIGHT, self.GRAPH_WIDTH_AND_HEIGHT,
                               aspectRatioMode=QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        self.fft_original_image_darkscale_label.setPixmap(pixmap)

        f = np.fft.fft2(img)
        fshift = np.fft.fftshift(f)
        magnitude_spectrum = 20*np.log(np.abs(fshift))
        magnitude_spectrum = np.uint8(magnitude_spectrum)
        magnitude_spectrum = cv.cvtColor(magnitude_spectrum, cv.COLOR_GRAY2RGB)
        height, width, channel = magnitude_spectrum.shape
        bytes_per_channel = channel * (magnitude_spectrum.dtype.itemsize)
        qimage = QImage(magnitude_spectrum.data, width, height,
                        bytes_per_channel * width, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        pixmap = pixmap.scaled(self.GRAPH_WIDTH_AND_HEIGHT, self.GRAPH_WIDTH_AND_HEIGHT,
                               aspectRatioMode=QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        self.fft_spectrum_label.setPixmap(pixmap)
        # now plot the phase spectrum
        phase_spectrum = np.angle(fshift)
        phase_spectrum = np.uint8(phase_spectrum)
        phase_spectrum = cv.cvtColor(phase_spectrum, cv.COLOR_GRAY2RGB)
        height, width, channel = phase_spectrum.shape
        bytes_per_channel = channel * (phase_spectrum.dtype.itemsize)
        qimage = QImage(phase_spectrum.data, width, height,
                        bytes_per_channel * width, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        pixmap = pixmap.scaled(self.GRAPH_WIDTH_AND_HEIGHT, self.GRAPH_WIDTH_AND_HEIGHT,
                               aspectRatioMode=QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        self.fft_phase_label.setPixmap(pixmap)

        # invert the image colors in opencv
        img = cv.bitwise_not(img)
        pixmap = QPixmap.fromImage(QImage(img, img.shape[1], img.shape[0], img.strides[0],
                                          QImage.Format.Format_Grayscale8))
        pixmap = pixmap.scaled(self.GRAPH_WIDTH_AND_HEIGHT, self.GRAPH_WIDTH_AND_HEIGHT,
                               aspectRatioMode=QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        self.fft_original_image_inverted_label.setPixmap(pixmap)

        # magnitude of the inverted image
        f = np.fft.fft2(img)
        fshift = np.fft.fftshift(f)
        magnitude_spectrum = 20*np.log(np.abs(fshift))
        magnitude_spectrum = np.uint8(magnitude_spectrum)
        magnitude_spectrum = cv.cvtColor(magnitude_spectrum, cv.COLOR_GRAY2RGB)
        height, width, channel = magnitude_spectrum.shape
        bytes_per_channel = channel * (magnitude_spectrum.dtype.itemsize)
        qimage = QImage(magnitude_spectrum.data, width, height,
                        bytes_per_channel * width, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        pixmap = pixmap.scaled(self.GRAPH_WIDTH_AND_HEIGHT, self.GRAPH_WIDTH_AND_HEIGHT,
                                 aspectRatioMode=QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        self.fft_inverted_spectrum_label.setPixmap(pixmap)

        # phase of the inverted image
        phase_spectrum = np.angle(fshift)
        phase_spectrum = np.uint8(phase_spectrum)
        phase_spectrum = cv.cvtColor(phase_spectrum, cv.COLOR_GRAY2RGB)
        height, width, channel = phase_spectrum.shape
        bytes_per_channel = channel * (phase_spectrum.dtype.itemsize)
        qimage = QImage(phase_spectrum.data, width, height,
                        bytes_per_channel * width, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage)
        pixmap = pixmap.scaled(self.GRAPH_WIDTH_AND_HEIGHT, self.GRAPH_WIDTH_AND_HEIGHT,
                                 aspectRatioMode=QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        self.fft_inverted_phase_label.setPixmap(pixmap)
        


