import logging as log
import png
import cv2 as cv
import gui
from PyQt6.QtWidgets import QApplication
import sys

log.basicConfig(format='%(asctime)s %(message)s', level=log.DEBUG)
ex_png = png.Png('spiderman.png')

print(ex_png.read_signature())
ex_png.read_chunks()

# img = cv.imread('cat.png')
# cv.imshow('Cat', img)

# cv.waitKey(0)

print(ex_png)
ex_png.process_header()
ex_png.process_palette()
ex_png.process_ending()

app = QApplication(sys.argv)
main_window = gui.MainWindow()
main_window.show()
sys.exit(app.exec())