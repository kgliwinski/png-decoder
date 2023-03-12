import numpy as np

FILE_PATH = 'cat.png'

signature = []
header = []
bytes = []

tmp = []
i = 0
with open(FILE_PATH, 'rb') as png:
    while (byte := png.read(1)):
        tmp.append(byte)
        if byte == b'\n' and i == 0:
            signature = tmp.copy()
            i += 1
            tmp.clear()


print(len(signature))
print(signature)
print(bytes[:30])

# with os.read(file):
