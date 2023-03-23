import png_class
import logging as log

log.basicConfig(format='%(asctime)s %(message)s', level=log.DEBUG)
png = png_class.Png('cat.png')

print(png.get_signature())
print(png.get_header())
# png.get_trailer()

print(png.process_signature())