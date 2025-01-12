from PIL import Image

import pytesseract

# Simple image to string
print(pytesseract.image_to_string(Image.open('''/home/josuevj/Documents/uni/servicio/
                                             sources/images/example_01.webp''')))
