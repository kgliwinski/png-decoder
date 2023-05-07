import png_class as png
import cv2 as cv

cat = png.Png('pictures/cat.png')
print(cat.get_chunk_types())

encrypted = png.EncryptedPng('pictures/cat.png')
encrypted.build_png_from_chunks('.tmp/encrypted.png')
print(encrypted.get_chunk_types())
img = cv.imread('.tmp/encrypted.png')
cv.imshow('Encrypted', img)

cv.waitKey(0)


