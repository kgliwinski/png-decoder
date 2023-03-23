import logging as log
import png

log.basicConfig(format='%(asctime)s %(message)s', level=log.DEBUG)
ex_png = png.Png('cat.png')

print(ex_png.read_signature())
ex_png.read_chunks()

print(ex_png)
