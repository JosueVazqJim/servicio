import pytesseract as tess
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
import re
import os

# Configuración de Tesseract
tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def cargar_correcciones(ruta_correcciones):
    correcciones = {}
    with open(ruta_correcciones, 'r', encoding='utf-8') as file:
        lineas = file.readlines()
    
    clave = None
    for linea in lineas:
        linea = linea.strip()
        if linea.startswith('"') and linea.endswith('"'):  # Es una clave
            clave = linea.strip('"')
        elif clave and linea:
            variantes = linea.split(',')
            for variante in variantes:
                correcciones[variante] = clave
    return correcciones

def aplicar_correcciones(archivo_salida, correcciones):
    try:
        with open(archivo_salida, 'r', encoding='utf-8') as file:
            contenido = file.read()
    except UnicodeDecodeError:
        with open(archivo_salida, 'r', encoding='ISO-8859-1') as file:
            contenido = file.read()

    for erroneo, correcto in correcciones.items():
        contenido = re.sub(rf'\b{re.escape(erroneo)}\b', correcto, contenido)

    with open(archivo_salida, 'w', encoding='utf-8') as file:
        file.write(contenido)

def detectar_titulo(image):
    titulo = image[0: 60, 0: 1330]
    gris = cv2.cvtColor(titulo, cv2.COLOR_BGR2GRAY)
    threshold_img = cv2.threshold(gris, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    gris = cv2.GaussianBlur(gris, (5, 5), 0)
    titulo_extraido = tess.image_to_string(threshold_img, lang="spa").strip()
    return titulo_extraido

def extraer_id_paciente(titulo):
    match = re.search(r"/\s*(\d{6})\s*/", titulo)
    return match.group(1) if match else None

def invertir_colores(imagen):
    return cv2.bitwise_not(imagen)

def verificar_texto(texto, image, archivo_expediente):
    patron = r"^[^/]+ / [^/]+ / [^/]+ / [^/]+$"

    if re.match(patron, texto):
        with open(archivo_expediente, 'a', encoding='utf-8') as my_file:
            my_file.write("\n" + ("*" * 100) + "\n")
            my_file.write(texto + "\n")
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (5, 5), 0)
            edges = cv2.Canny(gray, 50, 150)
            contornos, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            array_textos = []
            copy = image.copy()

            contornos_filtrados = []
            for contorno in contornos:
                epsilon = 0.02 * cv2.arcLength(contorno, True)
                approx = cv2.approxPolyDP(contorno, epsilon, True)
                if len(approx) == 4:
                    x, y, w, h = cv2.boundingRect(approx)
                    if w < 20 or h < 20 or h / w > 20:
                        continue
                    contornos_filtrados.append((x, y, w, h))

            if len(contornos_filtrados) == 3:
                for x, y, w, h in contornos_filtrados:
                    cv2.rectangle(copy, (x, y), (x + w, y + h), (255, 255, 255), -1)
                    cuadro_recortado = image[y:y + h, x:x + w]
                    cuadro_negativo = invertir_colores(cuadro_recortado)
                    gray = cv2.cvtColor(cuadro_negativo, cv2.COLOR_BGR2GRAY)
                    enhanced = cv2.convertScaleAbs(gray, alpha=2.5, beta=5)
                    pil_image = Image.fromarray(enhanced)
                    sharpened = pil_image.filter(ImageFilter.SHARPEN)
                    texto_extraido = tess.image_to_string(sharpened, lang='spa').strip()
                    if texto_extraido:
                        array_textos.append(texto_extraido)

            if len(contornos_filtrados) > 3:
                for x, y, w, h in contornos_filtrados:
                    cv2.rectangle(copy, (x, y), (x + w, y + h), (255, 255, 255), -1)
                    cuadro_recortado = image[y:y + h, x:x + w]
                    imagen_pil = Image.fromarray(cuadro_recortado)
                    enhancer = ImageEnhance.Contrast(imagen_pil)
                    imagen_pil = enhancer.enhance(1.1)
                    imagen_pil = imagen_pil.filter(ImageFilter.SHARPEN)
                    texto_extraido = tess.image_to_string(imagen_pil, lang='spa').strip()
                    if texto_extraido:
                        array_textos.append(texto_extraido)

            x, y, w, h = 0, 60, 1230, 645
            copy = copy[y:y + h, x:x + w]
            imagen_pil = Image.fromarray(copy)
            enhancer = ImageEnhance.Contrast(imagen_pil)
            imagen_pil = enhancer.enhance(1.1).filter(ImageFilter.SHARPEN)
            texto = tess.image_to_string(imagen_pil, lang='spa')

            my_file.write(texto + '\n')
            for item in reversed(array_textos):
                my_file.write(item + '\n\n')

def procesar_carpeta(carpeta, ruta_correcciones, carpeta_expedientes):
    archivos = sorted([f for f in os.listdir(carpeta) if f.startswith("frame") and f.endswith(".jpg")],
                      key=lambda x: int(re.search(r"\d+", x).group()))

    for archivo in archivos:
        ruta_imagen = os.path.join(carpeta, archivo)
        image = cv2.imread(ruta_imagen)
        x, y, w, h = 0, 180, 1230, 645
        image = image[y:y + h, x:x + w]
        titulo = detectar_titulo(image)

        id_paciente = extraer_id_paciente(titulo)
        if id_paciente:
            archivo_expediente = os.path.join(carpeta_expedientes, f"{id_paciente}.txt")
            print(f"Procesando: {archivo} para paciente {id_paciente}")
            verificar_texto(titulo, image, archivo_expediente)

    correcciones = cargar_correcciones(ruta_correcciones)
    for expediente in os.listdir(carpeta_expedientes):
        ruta_expediente = os.path.join(carpeta_expedientes, expediente)
        aplicar_correcciones(ruta_expediente, correcciones)

    nueva_carpeta = os.path.join(os.path.dirname(carpeta), f"{os.path.basename(carpeta)} (LISTO)")
    os.rename(carpeta, nueva_carpeta)

def main():
    ruta_base = r"D:\DOCUMENTOS\VirtualEnvPy\dataScience\source\Servicio\ServicioF\frame_extraction"
    ruta_correcciones = r"D:\DOCUMENTOS\VirtualEnvPy\dataScience\source\Servicio\ServicioF\correccion.txt"
    carpeta_expedientes = "expedientes"

    if not os.path.exists(carpeta_expedientes):
        os.makedirs(carpeta_expedientes)

    carpetas = [os.path.join(ruta_base, carpeta) for carpeta in os.listdir(ruta_base) 
                if os.path.isdir(os.path.join(ruta_base, carpeta)) and "(LISTO)" not in carpeta]

    for carpeta in sorted(carpetas):
        procesar_carpeta(carpeta, ruta_correcciones, carpeta_expedientes)

if __name__ == "__main__":
    main()
