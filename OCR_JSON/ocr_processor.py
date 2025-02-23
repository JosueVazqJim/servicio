import os
from texto_a_json.creador_vector import TextoJson
from extraccion_texto.tratador_ocr import TratadorOCR

class OCRProcessor:
    def __init__(self, ruta_videos, ruta_destino, ruta_correciones):
        """
        Inicializa la clase OCRProcessor.

        Args:
            ruta_videos (str): Ruta donde se encuentran los videos a procesar.
            ruta_destino (str): Ruta donde se guardarán los archivos .txt y .json.

        Attributes:
            ruta_videos (str): Ruta donde se encuentran los videos a procesar.
            ruta_destino (str): Ruta donde se guardarán los archivos .txt y .json.
            tratadorOCR (TratadorOCR): Instancia de la clase TratadorOCR para extraer texto de los videos.
            convertidor (TextoJson): Instancia de la clase TextoJson para convertir archivos .txt a .json
        """
        self.ruta_videos = ruta_videos
        self.ruta_destino = ruta_destino
        self.tratadorOCR = TratadorOCR(ruta_correciones) # Suponiendo que esta clase existe
        self.convertidor = TextoJson()

    def renombrar_videos(self):
        """
        Renombra los videos en la ruta dada en un orden ascendente de números.
        """
        # Obtener la lista de archivos de video en la ruta
        archivos_videos = [archivo for archivo in os.listdir(self.ruta_videos) if archivo.endswith('.mp4')]
        
        # Ordenar los archivos de video
        archivos_videos.sort()

        # Renombrar los archivos de video
        for indice, archivo_video in enumerate(archivos_videos):
            nuevo_nombre = f"video_{indice + 1}.mp4"
            ruta_actual = os.path.join(self.ruta_videos, archivo_video)
            nueva_ruta = os.path.join(self.ruta_videos, nuevo_nombre)
            os.rename(ruta_actual, nueva_ruta)

    def procesar_videos(self):
        """
        Procesa los videos en la ruta dada, genera archivos .txt y los convierte a JSON.
        """
        # Obtener la lista de archivos de video en la ruta
        archivos_videos = [archivo for archivo in os.listdir(self.ruta_videos) if archivo.endswith('.mp4')]

        for archivo_video in archivos_videos:
            # Extraer el nombre del video sin la extensión
            nombre_video = os.path.splitext(archivo_video)[0]

            # Crear una carpeta para los archivos .txt, frames y json del video
            carpeta_video_destino = os.path.join(self.ruta_destino, nombre_video)
            os.makedirs(carpeta_video_destino, exist_ok=True)

            # Ruta completa del video
            ruta_video = os.path.join(self.ruta_videos, archivo_video)

            # Extraer texto del video y guardar en archivos .txt
            self.tratadorOCR.set_rutas(ruta_video, carpeta_video_destino)
            ruta_txt = self.tratadorOCR.procesar_video()

            # Obtener la lista de archivos .txt generados
            archivos_txt = [f for f in os.listdir(ruta_txt) if f.endswith('.txt')]

            # Crear una carpeta para los archivos .json del video
            ruta_json_video = os.path.join(carpeta_video_destino, 'vectores')
            os.makedirs(ruta_json_video, exist_ok=True)

            # # Convertir cada archivo .txt a JSON
            # for archivo_txt in archivos_txt:
            #     clave = os.path.splitext(archivo_txt)[0]
            #     ruta_txt = os.path.join(ruta_txt, archivo_txt) # Ruta del archivo .txt
            #     ruta_json = os.path.join(ruta_json_video, f"{clave}.json") # Ruta del archivo .json

            #     if not os.path.exists(ruta_json):  # Evitar reprocesamiento
            #         self.convertidor.setNombreArchivo(ruta_txt)  # Cargar el archivo .txt
            #         self.convertidor.convertir_txt_json(ruta_json)  # Convertir a JSON y guardar
            #         print(f"Archivo {ruta_json} creado.")