import logging as log
import png_class as png
# import cv2 as cv
import gui
from PyQt6.QtWidgets import QApplication, QTabWidget
from matplotlib.backends.backend_qt import FigureCanvasQT as FigureCanvas, QtCore, QtWidgets
import sys

if __name__ == '__main__':
    log.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=11)
    # ex_png : png.Png = png.Png('cat.png')

    # print(ex_png.read_signature())
    # ex_png.read_chunks()

    # img = cv.imread('cat.png')
    # cv.imshow('Cat', img)

    # cv.waitKey(0)

    # print(ex_png)
    # print(ex_png.get_all_chunk_numbers())
    # print(ex_png.check_critical_chunk_numbers())
    app = QtWidgets.QApplication(sys.argv)
    main_window = gui.MainWindow()
    main_window.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
    main_window.show()
    sys.exit(app.exec())
