import png_class as png
import cv2 as cv
import logging as log
import sys

log.basicConfig(
    format='%(levelname)s {%(pathname)s:%(lineno)d} %(asctime)s %(message)s', level=log.ERROR)
cat = png.Png('pictures/cat.png')
# print(cat.get_chunk_types())

ENCRYPTED_ECB_PATH = '.tmp/encrypted_ecb.png'
DECRYPTED_ECB_PATH = '.tmp/decrypted_ecb.png'
ENCRYPTED_CFB_PATH = '.tmp/encrypted_cfb.png'
DECRYPTED_CFB_PATH = '.tmp/decrypted_cfb.png'
ENCRYPTED_AES_ECB_PATH = '.tmp/encrypted_aes_ecb.png'

if __name__ == '__main__':
    argc = len(sys.argv)
    
    if argc == 2:
        original_png_path = sys.argv[1]
        print(original_png_path)
    else:
        log.error('Usage: python3 main.py <path_to_png_file>')
        sys.exit(1)

    # encrypted = png.EncryptedPng(original_png_path)
    # private_key = encrypted.encrypt_ecb(ENCRYPTED_ECB_PATH)

    # pubic_key, private_key = encrypted.return_keys()

    # decrypted = png.EncryptedPng(ENCRYPTED_ECB_PATH, private_key=private_key)
    # decrypted.decrypt_ecb(DECRYPTED_ECB_PATH)

    # enc = cv.imread(ENCRYPTED_ECB_PATH)
    # dec = cv.imread(DECRYPTED_ECB_PATH)
    # cv.imshow('Encrypted', enc)
    # cv.imshow('Decrypted', dec)

    encrypted_cfb = png.EncryptedPng(original_png_path)
    iv, public_key, private_key = encrypted_cfb.encrypt_cfb(ENCRYPTED_CFB_PATH)

    decrypted_cfb = png.EncryptedPng(ENCRYPTED_CFB_PATH, public_key=public_key, private_key=private_key)
    decrypted_cfb.decrypt_cfb(DECRYPTED_CFB_PATH, iv)

    enc = cv.imread(ENCRYPTED_CFB_PATH)
    dec = cv.imread(DECRYPTED_CFB_PATH)
    cv.imshow('Encrypted cfb', enc)
    cv.imshow('Decrypted cfb', dec)

    # encrypted_aes = png.EncryptedPng(original_png_path)
    # encrypted.encrypt_aes_ecb(ENCRYPTED_AES_ECB_PATH, public_key=pubic_key)

    # enc = cv.imread(ENCRYPTED_AES_ECB_PATH)
    # cv.imshow('Encrypted external', enc)

    cv.waitKey(0)
