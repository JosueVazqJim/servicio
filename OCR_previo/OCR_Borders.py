import pytesseract as tess
from PIL import Image
import cv2
import numpy as np

# configuramos la ruta de Tesseract
##tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Leeo la imagen con opencv
image = cv2.imread('/home/josuevj/Documents/uni/servicio/sources/images/prueba.jpg')

x, y, w, h = 10, 120, 1230, 750  # coordenadas y dimensiones del recorte
#recorte = image[y:y+h, x:x+w]  # guardo la imagen recortada
recorte = image


# convercion a escala de grises
gray = cv2.cvtColor(recorte, cv2.COLOR_BGR2GRAY)

# reduccion de ruido
gray = cv2.GaussianBlur(gray, (5, 5), 0)

# detectamos bordes, edges es una imagen binaria donde muestra los bordes con color blanco
edges = cv2.Canny(gray, 50, 150)
cv2.imwrite('bordes_detectados.png', edges)

# encontrar contornos en la imagen, contornos es una lista que guarda coordenadas de los contornos
# como x, y de los puntos que forman el contorno y jerarquia es una lista que guarda la jerarquia de 
# los contornos en caso que un contorno este dentro de otro
contornos, jerarquia = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# crear archivo txt
my_file = open('''/home/josuevj/Documents/uni/servicio/sources/OCR_previo/out/OCR_Borders/TextoExtraido2.txt''', 'w')

# buscar contornos
for contorno in contornos:
    # aproximando el contorno a un polígono
    epsilon = 0.02 * cv2.arcLength(contorno, True)
    approx = cv2.approxPolyDP(contorno, epsilon, True)

    # el contorno tiene 4 lados
    if len(approx) == 4:
        x, y, w, h = cv2.boundingRect(approx)

        # recortar el área del cuadro detectado
        cuadro_recortado = recorte[y:y + h, x:x + w]

        # convirtiendo la imagen a imagen PIL para pasarlo a Tesseract
        imagen_pil = Image.fromarray(cuadro_recortado)

        # aplicar OCR a la imagen
        texto_extraido = tess.image_to_string(imagen_pil, lang='spa')

        # escribir el texto extraido en el documento txt
        my_file.write(texto_extraido + '\n')

# Cerrar el archivo
my_file.close()