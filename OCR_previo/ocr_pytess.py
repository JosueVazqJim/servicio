import pytesseract as tess
from PIL import Image
import cv2

#tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

image = cv2.imread('/home/josuevj/Documents/uni/servicio/sources/images/prueba.jpg')

#cv2.imshow('Imagen original', image)

x, y, w, h = 10, 120, 1230, 750
recorte = image[y:y+h, x:x+w]

#lineas de codigo que muestran la imagen recortada
#cv2.imshow('Imagen recortada', recorte)
#cv2.waitKey(0)

#convirtiendo imagen a grises
gray = cv2.cvtColor(recorte, cv2.COLOR_BGR2GRAY)
#eliminamos ruido
gray = cv2.GaussianBlur(gray, (5,5), 0)
#aplicamos binarizacion
#binary_img = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
#                                   cv2.THRESH_BINARY, 11, 2)

imagen_pil = Image.fromarray(gray)

txt = tess.image_to_string(imagen_pil, lang='spa')
#lineas de codigo modiicadas
#txt = tess.image_to_string(my_image)
#imprime el resultado de hacer ocr en la imagen
#print(txt)

#creacion del archivo donde alamcenaremos el texto convertido
my_file=open('''/home/josuevj/Documents/uni/servicio/sources/OCR_previo/out/ocr_pytess/SoloConGrises.txt''', 'w')
my_file.write(txt + '\n')
my_file.close()

#cerrar ventanas, descomentar cuando se muestre alguna imagen
#cv2.destroyAllWindows()
