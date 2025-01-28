import pytesseract as tess
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
import re

def detectar_titulo(titulo):
    titulo = image[0: 60, 0: 1330]
    # Solo para el ID (Título)
    gris = cv2.cvtColor(titulo, cv2.COLOR_BGR2GRAY)
    threshold_img = cv2.threshold(gris, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    gris = cv2.GaussianBlur(gris, (5, 5), 0)
    titulo_extraido = tess.image_to_string(threshold_img, lang="spa")
    
    return titulo_extraido

def verificar_texto(texto, image):
    # Expresión regular para verificar el formato
    patron = r"^[^/]+ / [^/]+ / [^/]+ / [^/]+$"
    
    if re.match(patron, texto):
        my_file.write(ID)
        # Conversión a escala de grises
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Reducción de ruido
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        # Detectar bordes
        edges = cv2.Canny(gray, 50, 150)

        # Encontrar contornos en la imagen
        contornos, jerarquia = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Array para guardar los textos extraídos
        array_textos = []

        copy = image.copy()

        # Buscar contornos y eliminar las áreas detectadas
        for contorno in contornos:
            # Aproximar el contorno a un polígono
            epsilon = 0.02 * cv2.arcLength(contorno, True)
            approx = cv2.approxPolyDP(contorno, epsilon, True)

            # Si el contorno tiene 4 lados
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(approx)

                # Filtrar contornos pequeños que podrían ser letras como 'l'
                if w < 20 or h < 20 or h / w > 20:  # Ajustar criterios según necesidad
                    continue

                # Eliminar el área del cuadro detectado (rellenarlo con blanco)
                cv2.rectangle(copy, (x, y), (x + w, y + h), (255, 255, 255), -1)

                # Convertir el área recortada a imagen PIL para OCR
                cuadro_recortado = image[y:y + h, x:x + w]
                imagen_pil = Image.fromarray(cuadro_recortado)

                # Aumentar el contraste de la imagen
                enhancer = ImageEnhance.Contrast(imagen_pil)
                imagen_pil = enhancer.enhance(1.1)  # Incrementar el contraste

                # Aumentar la nitidez de la imagen
                imagen_pil = imagen_pil.filter(ImageFilter.SHARPEN)

                # Aplicar OCR a la imagen
                texto_extraido = tess.image_to_string(imagen_pil, lang='spa').strip()

                # Reemplazar doble salto de línea (\n\n) con un único salto de línea (\n)
                texto_extraido = texto_extraido.replace('\n\n', '\n')

                # Guardar el texto no vacío en el array
                if texto_extraido:  # Solo agregar si no está vacío
                    array_textos.append(texto_extraido)


        # Recortar la región de interés
        x, y, w, h = 0, 60, 1230, 645  # Coordenadas y dimensiones del recorte
        copy = copy[y:y + h, x:x + w]  # Guardar la imagen recortada

        imagen_pil = Image.fromarray(copy)

        # Aumentar el contraste de la imagen
        enhancer = ImageEnhance.Contrast(imagen_pil)
        imagen_pil = enhancer.enhance(1.1)  # Incrementar el contraste

        # Aumentar la nitidez de la imagen
        imagen_pil = imagen_pil.filter(ImageFilter.SHARPEN)

        imagen_pil.show()

        texto = tess.image_to_string(imagen_pil, lang='spa')
        my_file.write(texto + '\n')


        # Imprimir el array con los textos extraídos
        for item in reversed(array_textos):
            my_file.write(item + '\n\n')
    else:
        image = image[0: 620, 0: 1330]
        imagen_pil = Image.fromarray(image)

        # Aumentar el contraste de la imagen
        enhancer = ImageEnhance.Contrast(imagen_pil)
        imagen_pil = enhancer.enhance(1)  # Incrementar el contraste

        # Aumentar la nitidez de la imagen
        imagen_pil = imagen_pil.filter(ImageFilter.SHARPEN)
        
        imagen_pil.show()

        texto = tess.image_to_string(imagen_pil, lang='spa')
        my_file.write(texto + '\n')

# Configuramos la ruta de Tesseract
tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Crear archivo txt
my_file = open('D:\DOCUMENTOS\VirtualEnvPy\dataScience\source\Servicio\OCR_erik\ExtraccionTexto\TextoExtraido4.txt', 'w', encoding='utf-8')

# Leer la imagen con OpenCV
image = cv2.imread(r'D:\DOCUMENTOS\VirtualEnvPy\dataScience\source\Servicio\OCR_erik\ExtraccionImagenes\cuadros\Zoom Reunion 2023-08-29 07-46-55\frame2.jpg')

# Recortar la región de interés
x, y, w, h = 0, 180, 1230, 645  # Coordenadas y dimensiones del recorte
image = image[y:y + h, x:x + w]  # Guardar la imagen recortada

# Escribir el texto extraído en el archivo txt
ID = detectar_titulo(image)
print(ID)
verificar_texto(ID, image)

# Cerrar el archivo
my_file.close()