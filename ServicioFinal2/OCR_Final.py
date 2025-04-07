import pytesseract as tess
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import re
import os
import numpy as np

# Configuración de Tesseract
tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def detectar_titulo(image):
    titulo = image[0: 70, 0: 1280]
    gris = cv2.cvtColor(titulo, cv2.COLOR_BGR2GRAY)
    threshold_img = cv2.threshold(gris, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    gris = cv2.GaussianBlur(gris, (5, 5), 0)
    titulo_extraido = tess.image_to_string(threshold_img, lang="spa").strip()
    # Agregar espacio después de la diagonal si está pegada con cualquier cosa
    titulo_extraido = re.sub(r"/(\S)", r"/ \1", titulo_extraido)  # Después
    # Agregar espacio antes de la diagonal si está pegada con cualquier cosa
    titulo_extraido = re.sub(r"(\S)/", r"\1 /", titulo_extraido)  # Antes
    return titulo_extraido

# Modificamos la parte donde se extrae el ID
def extraer_id_paciente(titulo):
    match = re.search(r"/\s*(\d{3,})\s*/", titulo)
    if match:
        return match.group(1)
    return None

def verificar_texto(texto, image, archivo_expediente):
    patron = r"^[^/]+ / [^/]+ / [^/]+ / [^/]+$"

    if re.match(patron, texto):
        with open(archivo_expediente, 'a+', encoding='utf-8') as my_file:
            my_file.seek(0)
            contenido = my_file.read()
            if not contenido.strip():
                my_file.write(texto + "\n")
            x, y, w, h = 0, 72, 1280, 720
            image = image[y:y + h, x:x + w]
            gray = cv2.GaussianBlur(image, (5, 5), 0)
            edges = cv2.Canny(gray, 50, 150)
            contornos, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            array_textos = []
            copy = gray.copy()

            contornos_filtrados = []
            for contorno in contornos:
                epsilon = 0.02 * cv2.arcLength(contorno, True)
                approx = cv2.approxPolyDP(contorno, epsilon, True)
                if len(approx) == 4:
                    x, y, w, h = cv2.boundingRect(approx)
                    if w < 20 or h < 20 or h / w > 20:
                        continue
                    contornos_filtrados.append((x, y, w, h))

            if len(contornos_filtrados) >= 1:
                for x, y, w, h in contornos_filtrados:
                    cv2.rectangle(copy, (x, y), (x + w, y + h), (255, 255, 255), -1)
                    cuadro_recortado = image[y:y + h, x:x + w]
                    alto, ancho = cuadro_recortado.shape[:2]
                    factor_escala = 3  # Puedes probar con valores entre 1.5 y 3

                    imagen_aumentada = cv2.resize(cuadro_recortado, (ancho * factor_escala, alto * factor_escala), interpolation=cv2.INTER_LANCZOS4)
                    
                    # Filtro de enfoque personalizado usando OpenCV
                    kernel_enfoque = np.array([[0, -1, 0],
                                                [-1, 5, -1],
                                                [0, -1, 0]])

                    # Aplicar el filtro de enfoque
                    imagen_enfocada = cv2.filter2D(imagen_aumentada, -1, kernel_enfoque)

                    # Convertir a formato PIL para usar Tesseract
                    imagen_pil = Image.fromarray(imagen_enfocada)
                    imagen_pil = imagen_pil.filter(ImageFilter.SHARPEN)
                    texto_extraido = tess.image_to_string(imagen_pil, lang='spa').strip()
                    if texto_extraido:
                        array_textos.append(texto_extraido)
                        
                # Se elimina el comentario anterior y se verifica si hay diagnóstico
                # Si hay 3 o más cuadros, se revisa la presencia de "Diagnóstico:" o "Diagnostico:" en el OCR del frame
                if len(contornos_filtrados) >= 3:
                    # Aquí se espera a extraer el texto completo del frame para poder validar
                    pass  # La validación se realizará después de extraer el OCR completo

            # Filtro de enfoque personalizado usando OpenCV para el OCR completo del frame
            kernel_enfoque = np.array([[0, -1, 0],
                                        [-1, 5, -1],
                                        [0, -1, 0]])

            # Aplicar el filtro de enfoque
            imagen_enfocada = cv2.filter2D(copy, -1, kernel_enfoque)

            # Convertir a formato PIL para usar Tesseract y aplicar filtro de nitidez
            imagen_pil = Image.fromarray(imagen_enfocada)
            imagen_pil = imagen_pil.filter(ImageFilter.SHARPEN)
            texto_completo = tess.image_to_string(imagen_pil, lang='spa')

            # Verificar si en un frame con 3 o más cuadros falta "Diagnóstico:" o "Diagnostico:"
            if len(contornos_filtrados) >= 3 and not re.search(r"Diagn[oó]stico:", texto_completo):
                my_file.write("NO HAY DGT\n")  # Nuevo mensaje agregado

            # Escribir el texto extraído del frame completo
            my_file.write(texto_completo + '\n')
            for item in reversed(array_textos):
                my_file.write(item + '\n\n')

def procesar_carpeta(carpeta, carpeta_expedientes):
    archivos = sorted([f for f in os.listdir(carpeta) if f.startswith("frame") and f.endswith(".jpg")],
                      key=lambda x: int(re.search(r"\d+", x).group()))

    id_pacientes_procesados = set()  # Conjunto para llevar registro de los IDs procesados

    for archivo in archivos:
        ruta_imagen = os.path.join(carpeta, archivo)
        image = cv2.imread(ruta_imagen)
        image = extract_slide(image)
        titulo = detectar_titulo(image)

        id_paciente = extraer_id_paciente(titulo)
        if id_paciente:
            archivo_expediente = os.path.join(carpeta_expedientes, f"{id_paciente}.txt")
            archivo_expediente_listo = os.path.join(carpeta_expedientes, f"{id_paciente} (LISTO).txt")
            
            # Si el expediente ya tiene "(LISTO)", lo renombramos para permitir agregar nueva información
            if os.path.exists(archivo_expediente_listo):
                print(f"Encontrado expediente {id_paciente} (LISTO), habilitándolo para nueva información...")
                os.rename(archivo_expediente_listo, archivo_expediente)

            # Agregar ID al conjunto para asegurarse de que se procese por separado
            if id_paciente not in id_pacientes_procesados:
                id_pacientes_procesados.add(id_paciente)
                print(f"Procesando: {archivo} para paciente {id_paciente}")
            
            verificar_texto(titulo, image, archivo_expediente)

    nueva_carpeta = os.path.join(os.path.dirname(carpeta), f"{os.path.basename(carpeta)} (LISTO)")
    os.rename(carpeta, nueva_carpeta)

def extract_slide(img, output_size=(1280, 720)):
    """Recorta la diapositiva detectando el área con el fondo más grande, ajusta proporciones y redimensiona."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Aplicar umbral para eliminar el fondo oscuro
    _, thresh = cv2.threshold(gray, 40, 255, cv2.THRESH_BINARY)
    
    # Encontrar contornos
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filtrar contornos grandes con proporciones rectangulares
    possible_slides = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = w / h
        area = cv2.contourArea(cnt)
        
        if 1.3 < aspect_ratio < 2 and area > 50000:  # Filtrar áreas grandes y rectangulares
            possible_slides.append((x, y, w, h))
    
    if not possible_slides:
        return cv2.resize(img, output_size)  # Si no se detecta nada, redimensionar la imagen original

    # Tomar el contorno más grande de los filtrados
    x, y, w, h = max(possible_slides, key=lambda b: b[2] * b[3])
    
    # Ajustar proporciones estándar (16:9 o 4:3)
    target_aspect_ratios = [16/9, 4/3]
    best_ratio = min(target_aspect_ratios, key=lambda r: abs((w / h) - r))
    
    if best_ratio == 16/9:
        new_h = int(w / 16 * 9)
    else:
        new_h = int(w / 4 * 3)
    
    # Centrar en la imagen original
    y_center = y + h // 2
    y = max(0, y_center - new_h // 2)
    h = min(img.shape[0] - y, new_h)
    
    # Recortar la diapositiva
    slide = img[y:y+h, x:x+w]
    
    # Redimensionar al tamaño estándar
    slide_resized = cv2.resize(slide, output_size)
    # Obtener los valores mínimo y máximo de la imagen
    alow = np.min(slide_resized)
    ahigh = np.max(slide_resized)
    amin, amax = 0, 255

    # Ajuste automático de contraste
    adjusted_image = amin + (slide_resized - alow) * ((amax - amin) / (ahigh - alow))
    adjusted_image = np.clip(adjusted_image, amin, amax).astype(np.uint8)
    
    return slide_resized

def main():
    ruta_base = "frame_extraction"
    carpeta_expedientes = "expedientes"

    if not os.path.exists(carpeta_expedientes):
        os.makedirs(carpeta_expedientes)

    carpetas = [os.path.join(ruta_base, carpeta) for carpeta in os.listdir(ruta_base) 
                if os.path.isdir(os.path.join(ruta_base, carpeta)) and "(LISTO)" not in carpeta]

    for carpeta in sorted(carpetas):
        procesar_carpeta(carpeta, carpeta_expedientes)

if __name__ == "__main__":
    main()
