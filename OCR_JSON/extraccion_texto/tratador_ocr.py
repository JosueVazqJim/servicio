import pytesseract as tess
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
import re
import os
from .extraccion_cuadros import ExtraccionCuadros

class TratadorOCR:
    """
    Clase para extraer texto de imágenes y videos.
    Funciona en conjunto con la clase ExtraccionCuadros
    """

    def __init__(self, ruta_correrciones):
        try:
            tess.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        except Exception as e:
            print(f"Error al configurar Tesseract: {e}")

        self.ruta_video = None
        self.ruta_destino = None
        self.ruta_correcciones = ruta_correrciones
        self.ruta_frames = None
        self.ruta_txt = None
        self.extractor = ExtraccionCuadros()

    def set_rutas(self, ruta_video, ruta_destino):
        """
        Establece las rutas del video a procesar y de los archivos .txt.

        Args:
            ruta_video (str): Ruta del video a procesar.
            ruta_destino (str): Ruta donde se guardarán los archivos .txt y frames.
        """
        self.ruta_video = ruta_video
        self.ruta_destino = ruta_destino
        self.ruta_frames = os.path.join(ruta_destino, "frames")
        self.ruta_txt = os.path.join(ruta_destino, "expedientes")

        # Crear carpetas si no existen
        os.makedirs(self.ruta_frames, exist_ok=True)
        os.makedirs(self.ruta_txt, exist_ok=True)

    def __extraer_frames(self):
        """
        Extrae frames del video y los guarda como imágenes.
        """
        if not self.ruta_video or not self.ruta_frames:
            print("Las rutas de video y frames deben estar establecidas.")
            return
        
        self.extractor.procesar_video(self.ruta_video, self.ruta_frames)

    def __cargar_correcciones(self):
        """
        Carga las correcciones de texto desde un archivo de texto.
        """
        if not self.ruta_correcciones:
            print("La ruta de correcciones no está establecida.")
            return {}

        correcciones = {}
        with open(self.ruta_correcciones, 'r', encoding='utf-8') as file:
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

    def __aplicar_correcciones(self, archivo_salida, correcciones):
        """
        Aplica correcciones de texto a un archivo de salida.

        Args:
            archivo_salida (str): Ruta del archivo de salida.
            correcciones (dict): Diccionario de correcciones.
        """
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


    def __detectar_titulo(self, image):
        """
        Detecta el título en una imagen.

        Args:
            image (numpy.ndarray): Imagen en formato numpy array.

        Returns:
            str: Texto extraído del título.
        """
        titulo = image[0: 60, 0: 1330]
        gris = cv2.cvtColor(titulo, cv2.COLOR_BGR2GRAY)
        threshold_img = cv2.threshold(gris, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        gris = cv2.GaussianBlur(gris, (5, 5), 0)
        titulo_extraido = tess.image_to_string(threshold_img, lang="spa").strip()
        return titulo_extraido

    def __extraer_id_paciente(self, titulo):
        """
        Extrae el ID del paciente del título.

        Args:
            titulo (str): Texto del título.

        Returns:
            str: ID del paciente.
        """
        match = re.search(r"/\s*(\d{6})\s*/", titulo)
        return match.group(1) if match else None

    def __invertir_colores(self, imagen):
        """
        Invierte los colores de una imagen.

        Args:
            imagen (numpy.ndarray): Imagen en formato numpy array.

        Returns:
            numpy.ndarray: Imagen con colores invertidos.
        """
        return cv2.bitwise_not(imagen)

    def __verificar_texto(self, texto, image, archivo_expediente):
        """
        Verifica y procesa el texto extraído de una imagen.

        Args:
            texto (str): Texto extraído.
            image (numpy.ndarray): Imagen en formato numpy array.
            archivo_expediente (str): Ruta del archivo de expediente.
        """
        patron = r"^[^/]+ / [^/]+ / [^/]+ / [^/]+$"

        if re.match(patron, texto):
            with open(archivo_expediente, 'a', encoding='utf-8') as my_file:
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
                        cuadro_negativo = self.__invertir_colores(cuadro_recortado)
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

    def procesar_carpeta(self):
        """
        Procesa todos los frames en la carpeta de frames y genera los expedientes.
        """
        if not self.ruta_frames or not self.ruta_txt:
            print("Las rutas de frames y expedientes deben estar establecidas.")
            return

        archivos = sorted([f for f in os.listdir(self.ruta_frames) if f.startswith("frame") and f.endswith(".jpg")],
                        key=lambda x: int(re.search(r"\d+", x).group()))

        correcciones = self.__cargar_correcciones()

        for archivo in archivos:
            ruta_imagen = os.path.join(self.ruta_frames, archivo)
            image = cv2.imread(ruta_imagen)
            x, y, w, h = 0, 180, 1230, 645
            image = image[y:y + h, x:x + w]
            titulo = self.__detectar_titulo(image)

            id_paciente = self.__extraer_id_paciente(titulo)
            if id_paciente:
                archivo_expediente = os.path.join(self.ruta_txt, f"{id_paciente}.txt")
                print(f"Procesando: {archivo} para paciente {id_paciente}")
                self.__verificar_texto(titulo, image, archivo_expediente)

        for expediente in os.listdir(self.ruta_txt):
            ruta_expediente = os.path.join(self.ruta_txt, expediente)
            self.__aplicar_correcciones(ruta_expediente, correcciones)

        # nueva_carpeta = os.path.join(os.path.dirname(self.ruta_frames), f"{os.path.basename(self.ruta_frames)} (LISTO)")
        # os.rename(self.ruta_frames, nueva_carpeta)

    def procesar_video(self):
        """
        Procesa el video, extrae los frames y genera los expedientes.

        Returns:
            str: Ruta de la carpeta con los expedientes
        """
        self.__extraer_frames()
        self.procesar_carpeta()
        return self.ruta_txt

# # Ejemplo de uso
# if __name__ == "__main__":
#     tratador = TratadorOCR(r"D:\DOCUMENTOS\VirtualEnvPy\dataScience\source\Servicio\OCR_JSON\extraccion_texto\correccion.txt")
#     tratador.set_rutas(ruta_video=r"D:\DOCUMENTOS\VirtualEnvPy\dataScience\source\Servicio\ServicioF\Videos\1.mp4", ruta_destino=r"D:\DOCUMENTOS\VirtualEnvPy\dataScience\source\Servicio\ServicioF\Videos\destino")
#     ruta = tratador.procesar_video()
#     print(f"Expedientes generados en: {ruta}")