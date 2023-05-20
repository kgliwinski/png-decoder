import png_class as png
import cv2 as cv
import logging as log

log.basicConfig(
    format='%(levelname)s {%(pathname)s:%(lineno)d} %(asctime)s %(message)s', level=log.ERROR)
cat = png.Png('pictures/cat.png')
# print(cat.get_chunk_types())


encrypted = png.EncryptedPng('pictures/dice.png')
private_key = encrypted.encrypt_rsa_2048()

decrypted = png.EncryptedPng('.tmp/encrypted.png', private_key = private_key)
decrypted.decrypt_rsa_2048()
# print(encrypted.get_chunk_types(), original.get_chunk_types())
enc = cv.imread('.tmp/encrypted.png')
dec = cv.imread('.tmp/decrypted.png')
cv.imshow('Encrypted', enc)
cv.imshow('Decrypted', dec)

cv.waitKey(0)


