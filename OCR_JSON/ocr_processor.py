import os
from texto_a_json.creador_vector import TextoJson

class OCRProcessor:
    def __init__(self, ruta_videos, ruta_destino):
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
        self.tratadorOCR = TratadorOCR() # Suponiendo que esta clase existe
        self.convertidor = TextoJson()

    def procesar_videos(self):
        """
        Procesa los videos en la ruta dada, genera archivos .txt y los convierte a JSON.
        """
        # Obtener la lista de archivos de video en la ruta
        archivos_videos = [archivo for archivo in os.listdir(self.ruta_videos) if archivo.endswith('.mp4')]

        for archivo_video in archivos_videos:
            # Extraer el nombre del video sin la extensión
            nombre_video = os.path.splitext(archivo_video)[0]

            # Crear una carpeta para los archivos .txt del video
            ruta_txt_video = os.path.join(self.ruta_destino, nombre_video, 'expedientes')
            os.makedirs(ruta_txt_video, exist_ok=True)

            # Ruta completa del video
            ruta_video = os.path.join(self.ruta_videos, archivo_video)

            # Extraer texto del video y guardar en archivos .txt
            self.tratadorOCR.setRutas(ruta_video, ruta_txt_video)
            self.tratadorOCR.procesar_video()  # Suponiendo que este método existe en ExtraccionTexto

            # Obtener la lista de archivos .txt generados
            archivos_txt = [f for f in os.listdir(ruta_txt_video) if f.endswith('.txt')]

            # Crear una carpeta para los archivos .json del video
            ruta_json_video = os.path.join(self.ruta_destino, nombre_video, 'vectores')
            os.makedirs(ruta_json_video, exist_ok=True)

            # Convertir cada archivo .txt a JSON
            for archivo_txt in archivos_txt:
                clave = os.path.splitext(archivo_txt)[0]
                ruta_txt = os.path.join(ruta_txt_video, archivo_txt) # Ruta del archivo .txt
                ruta_json = os.path.join(ruta_json_video, f"{clave}.json") # Ruta del archivo .json

                if not os.path.exists(ruta_json):  # Evitar reprocesamiento
                    self.convertidor.setNombreArchivo(ruta_txt)  # Cargar el archivo .txt
                    self.convertidor.convertir_txt_json(ruta_json)  # Convertir a JSON y guardar