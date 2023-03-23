import png
import logging as log

log.basicConfig(format='%(asctime)s %(message)s', level=log.DEBUG)
png = png.Png('cat.png')

print(png.get_signature())
png.get_chunks()
