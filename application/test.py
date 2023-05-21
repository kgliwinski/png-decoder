import png_class as png
import cv2 as cv
import logging as log

log.basicConfig(
    format='%(levelname)s {%(pathname)s:%(lineno)d} %(asctime)s %(message)s', level=log.ERROR)
cat = png.Png('pictures/cat.png')
# print(cat.get_chunk_types())


# encrypted = png.EncryptedPng('pictures/dice.png')
# private_key = encrypted.encrypt_ecb('.tmp/encrypted_ecb.png')

# decrypted = png.EncryptedPng('.tmp/encrypted_ecb.png', private_key = private_key)
# decrypted.decrypt_ecb('.tmp/decrypted_ecb.png')

# enc = cv.imread('.tmp/encrypted_ecb.png')
# dec = cv.imread('.tmp/decrypted_ecb.png')
# cv.imshow('Encrypted', enc)
# cv.imshow('Decrypted', dec)

encrypted_cfb = png.EncryptedPng('pictures/dice.png')
iv = encrypted_cfb.encrypt_decrypt_cfb('.tmp/encrypted_cfb.png')

decrypted_cfb = png.EncryptedPng('.tmp/encrypted_cfb.png')
decrypted_cfb.encrypt_decrypt_cfb('.tmp/decrypted_cfb.png', iv)

enc = cv.imread('.tmp/encrypted_cfb.png')
dec = cv.imread('.tmp/decrypted_cfb.png')
cv.imshow('Encrypted cfb', enc)
cv.imshow('Decrypted cfb', dec)

cv.waitKey(0)


