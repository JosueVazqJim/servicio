import pytesseract as tess
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np

# Configuramos la ruta de Tesseract
tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Crear archivo txt
my_file = open('D:\DOCUMENTOS\VirtualEnvPy\dataScience\source\Servicio\OCR_erik\ExtraccionTexto\TextoExtraido2.txt', 'w', encoding='utf-8')

# Leer la imagen con OpenCV
image = cv2.imread(r'D:\DOCUMENTOS\VirtualEnvPy\dataScience\source\Servicio\OCR_erik\ExtraccionImagenes\cuadros\Zoom Reunion 2023-08-29 07-46-55\frame0.jpg')
titulo = image[180: 237, 0: 1330]
cv2.imwrite(r'D:\DOCUMENTOS\VirtualEnvPy\dataScience\source\Servicio\OCR_erik\ExtraccionTexto\tituloimagen.png', titulo)

# Recortar la región de interés
x, y, w, h = 2, 237, 1230, 650  # Coordenadas y dimensiones del recorte quitando lo de zoom
recorte = image[y:y + h, x:x + w]
cv2.imwrite(r'D:\DOCUMENTOS\VirtualEnvPy\dataScience\source\Servicio\OCR_erik\ExtraccionTexto\recorteimagen.png', recorte)

# Escalar la imagen recortada
escala = 1.1  # Escalar al 110% de tamaño
width = int(recorte.shape[1] * escala)
height = int(recorte.shape[0] * escala)
recorte = cv2.resize(recorte, (width, height), interpolation=cv2.INTER_CUBIC)

# Escalar el titulo recortado
escala = 1  # Escalar al 110% de tamaño
width = int(titulo.shape[1] * escala)
height = int(titulo.shape[0] * escala)
titulo = cv2.resize(titulo, (width, height), interpolation=cv2.INTER_CUBIC)

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

# Encontrar contornos en la imagen
contornos, jerarquia = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Crear una máscara inicial del tamaño de la imagen
mascara = np.zeros_like(gray)

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

        cv2.rectangle(mascara, (x, y), (x + w, y + h), (255), -1)  # Rellenar la máscara

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

# Invertir la máscara para obtener las áreas no cubiertas por recuadros
mascara_invertida = cv2.bitwise_not(mascara)

# Aplicar la máscara invertida a la imagen original
imagen_fuera_recuadros = cv2.bitwise_and(gray, gray, mask=mascara_invertida)

# Guardar la máscara
cv2.imwrite(r'D:\DOCUMENTOS\VirtualEnvPy\dataScience\source\Servicio\OCR_erik\ExtraccionTexto\mascara.png', imagen_fuera_recuadros)

# Convertir a imagen PIL para aplicar OCR
imagen_pil_fuera_recuadros = Image.fromarray(imagen_fuera_recuadros)

# Extraer texto de las áreas fuera de recuadros
texto_fuera_recuadros = tess.image_to_string(imagen_pil_fuera_recuadros, lang='spa')
print("Texto fuera de recuadros:\n", texto_fuera_recuadros)

# Escribir el texto extraído en el archivo
my_file.write(texto_fuera_recuadros)

# Cerrar el archivo
my_file.close()