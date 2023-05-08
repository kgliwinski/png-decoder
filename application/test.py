import png_class as png
import cv2 as cv
import logging as log

log.basicConfig(
    format='%(levelname)s {%(pathname)s:%(lineno)d} %(asctime)s %(message)s', level=log.INFO)
cat = png.Png('pictures/spiderman.png')
print(cat.get_chunk_types())

encrypted = png.EncryptedPng('pictures/spiderman.png')
encrypted.build_png_from_chunks('.tmp/encrypted.png')
print(encrypted.get_chunk_types())
img = cv.imread('.tmp/encrypted.png')
cv.imshow('Encrypted', img)

cv.waitKey(0)


