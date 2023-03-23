import logging as log
import png
import cv2 as cv

log.basicConfig(format='%(asctime)s %(message)s', level=log.DEBUG)
ex_png = png.Png('cat.png')

print(ex_png.read_signature())
ex_png.read_chunks()

img = cv.imread('cat.png')
# cv.imshow('Cat', img)

# cv.waitKey(0)

print(ex_png)
ex_png.process_header()