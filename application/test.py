import png_class as png
import cv2 as cv

encrypted = png.EncryptedPng('pictures/cat.png')
encrypted.build_png_from_chunks('.tmp/encrypted.png')
img = cv.imread('.tmp/encrypted.png')
cv.imshow('Encrypted', img)

cv.waitKey(0)


