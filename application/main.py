import png_class
import logging as log

log.basicConfig(format='%(asctime)s %(message)s', level=log.INFO)
png = png_class.Png('cat.png')

png.get_signature()
