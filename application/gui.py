
import cv2
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QWidget, QVBoxLayout, QHBoxLayout, QComboBox
from PyQt6.QtGui import QImage, QPixmap
from PyQt6 import QtCore
import png_class as png
from chunk_class import IHDR
import glob
# from os import listdir

class MainWindow(QMainWindow):
    
    IMG_HEIGHT = 400
    IMG_WIDTH = 600

    png_type : png = None
    
    def __init__(self):
        super().__init__()

        # Create widgets
        self.png_input_label = QLabel("PNG path")
        self.png_input_field = QComboBox(self)
        self.png_input_field.setGeometry(QtCore.QRect(10, 10, 150, 30))
        self.png_input_field.setEditable(True)
        self.png_input_field.setPlaceholderText("Select PNG file or type path")
        
        # Populate dropdown list with options
        for file in glob.iglob('**/*.png', recursive=True):
            # if file[-4:].casefold() == '.png'.casefold():
            self.png_input_field.addItem(file)

        self.display_image_label = QLabel()
        self.display_image_label.setFixedSize(self.IMG_WIDTH, self.IMG_HEIGHT)
        self.display_image_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.width_label = QLabel("Width:")
        self.width_field = QLineEdit()
        self.width_field.setReadOnly(True)  # set field as editable
        self.height_label = QLabel("Height:")
        self.height_field = QLineEdit()
        self.height_field.setReadOnly(True)  # set field as editable
        self.bit_depth_label = QLabel("Bit depth:")
        self.bit_depth_field = QLineEdit()
        self.bit_depth_field.setReadOnly(True)  # set field as editable
        self.color_type_label = QLabel("Color type:")
        self.color_type_field = QLineEdit()
        self.color_type_field.setReadOnly(True)  # set field as editable
        self.compression_method_label = QLabel("Compression method:")
        self.compression_method_field = QLineEdit()
        self.compression_method_field.setReadOnly(
            True)  # set field as editable
        self.filter_method_label = QLabel("Filter method:")
        self.filter_method_field = QLineEdit()
        self.filter_method_field.setReadOnly(True)  # set field as editable
        self.interlace_method_label = QLabel("Interlace method:")
        self.interlace_method_field = QLineEdit()
        self.interlace_method_field.setReadOnly(True)  # set field as editable
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
        main_layout = QVBoxLayout()
        main_layout.addLayout(ihdr_layout)
        main_layout.addWidget(self.submit_button)
        main_layout.addWidget(self.display_image_label)

        # Set main layout
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def display_image_and_hdr_data(self):
        self.png_path = self.png_input_field.currentText()
        print(self.png_path)
        # Load image with OpenCV
        image = cv2.imread(self.png_path)

        # Display image
        if image is not None:
            if self.png_type is not None:
                self.png_type = None
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            height, width, channel = image.shape
            bytes_per_channel = channel * (image.dtype.itemsize)
            qimage = QImage(image.data, width, height, bytes_per_channel * width, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qimage)
            pixmap = pixmap.scaled(self.IMG_WIDTH, self.IMG_HEIGHT, aspectRatioMode=QtCore.Qt.AspectRatioMode.KeepAspectRatio)
            self.display_image_label.setPixmap(pixmap)
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
        except:
            self.png_input_label.setText("PNG Path: Invalid file name!")
            pass

        

    def update_fields_from_header(self, hdr : IHDR):
        data = hdr.get_hdr_data()
        self.width_field.setText(str(data["width"]))
        self.height_field.setText(str(data["height"]))
        self.bit_depth_field.setText(str(data["bit_depth"]))
        self.color_type_field.setText(str(data["color_type_str"]))
        self.compression_method_field.setText(str(data["compression_method"]))
        self.filter_method_field.setText(str(data["filter_method"]))
        self.interlace_method_field.setText(str(data["interlace_method"]))
