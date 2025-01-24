import pytesseract as tess
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np

# Configuramos la ruta de Tesseract
#tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Crear archivo txt
my_file = open('/home/josuevj/Documents/uni/servicio/sources/OCR_erik/TextoExtraido3.txt', 'w', encoding='utf-8')

# Leer la imagen con OpenCV
image = cv2.imread('/home/josuevj/Documents/uni/servicio/sources/OCR_erik/pruebaNueva.jpg')
titulo = image[0: 55, 0: 1330]

# Recortar la región de interés
x, y, w, h = 10, 120, 1230, 750  # Coordenadas y dimensiones del recorte quitando lo de zoom
recorte = image 

# Escalar la imagen recortada
escala = 1.5  # Escalar al 110% de tamaño
width = int(recorte.shape[1] * escala)
height = int(recorte.shape[0] * escala)
recorte = cv2.resize(recorte, (width, height), interpolation=cv2.INTER_CUBIC)
cv2.imwrite('/home/josuevj/Documents/uni/servicio/sources/OCR_erik/recorteimagen.jpg', recorte)

# Escalar el titulo recortado
escala = 1  # Escalar al 110% de tamaño
width = int(titulo.shape[1] * escala)
height = int(titulo.shape[0] * escala)
titulo = cv2.resize(titulo, (width, height), interpolation=cv2.INTER_CUBIC)

##guardamos el titulo
cv2.imwrite('/home/josuevj/Documents/uni/servicio/sources/OCR_erik/titulo2.jpg', titulo)

# Conversión a escala de grises
gray = cv2.cvtColor(recorte, cv2.COLOR_BGR2GRAY)

# Solo para el ID (Título)
gris = cv2.cvtColor(titulo, cv2.COLOR_BGR2GRAY)
threshold_img = cv2.threshold(gris, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU) [1]
gris = cv2.GaussianBlur(gris, (5, 5), 0)
titulo_extraido = tess.image_to_string(threshold_img, lang="spa")
print(titulo_extraido)

# Escribir el texto extraído en el archivo txt
my_file.write(titulo_extraido + '\n')

# Reducción de ruido
gray = cv2.GaussianBlur(gray, (5, 5), 0)

# Detectar bordes
edges = cv2.Canny(gray, 50, 150)
cv2.imwrite('/home/josuevj/Documents/uni/servicio/sources/OCR_erik/bordes.jpg', edges)

# Encontrar contornos en la imagen
contornos, jerarquia = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Buscar contornos
for contorno in contornos:
    # Aproximar el contorno a un polígono
    epsilon = 0.02 * cv2.arcLength(contorno, True)
    approx = cv2.approxPolyDP(contorno, epsilon, True)

    # Si el contorno tiene 4 lados
    if len(approx) == 4:
        x, y, w, h = cv2.boundingRect(approx)

        # Recortar el área del cuadro detectado
        cuadro_recortado = recorte[y:y + h, x:x + w]

        # Convertir la imagen a imagen PIL para ajustar el contraste
        imagen_pil = Image.fromarray(cuadro_recortado)

        # Aumentar el contraste de la imagen
        enhancer = ImageEnhance.Contrast(imagen_pil)
        imagen_pil = enhancer.enhance(2.2)  # Incrementar el contraste

        # Aumentar la nitidez de la imagen
        imagen_pil = imagen_pil.filter(ImageFilter.SHARPEN)

        # Aplicar OCR a la imagen
        texto_extraido = tess.image_to_string(imagen_pil, lang='spa')
        print(texto_extraido + '\n**************')

        # Posprocesamiento para corregir errores comunes
        texto_extraido = texto_extraido.replace("lodo", "Iodo").replace(" ll", " II").replace(" lA", " IA")
        my_file.write(texto_extraido + '\n')

# Cerrar el archivo
my_file.close()