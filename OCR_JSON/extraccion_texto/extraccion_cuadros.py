import cv2
import os
import numpy as np
import pytesseract
import re

class ExtraccionCuadros:
    """
    Clase para extraer cuadros de un video y guardarlos como imágenes.
    Por el momento, solo extrae frames de un video de grabacion de reunion
    de Zoom, con una resolucion de 1152x952.
    """

    def __init__(self):
        """
        Inicializa la clase Extraccion

        Atributos:
            ruta_videos (str): Ruta donde se encuentran los videos a procesar.
            ruta_frames (str): Ruta donde se guardarán los frames extraídos.
        """
        try:
            # Suponiendo que Tesseract está instalado en la ruta por defecto en Windows
            # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

            # si es en linux
            pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
        except Exception as e:
            print(f"Error al configurar Tesseract: {e}")

        self.ruta_video = None
        self.ruta_frames = None

    def set_ruta_video(self, ruta_video):
        """
        Establece la ruta donde se encuentran los videos a procesar.

        Args:
            ruta_videos (str): Ruta donde se encuentran los videos a procesar.
        """
        self.ruta_video = os.path.normpath(ruta_video)

    def set_ruta_frames(self, ruta_frames):
        """
        Establece la ruta donde se guardarán los frames extraídos.

        Args:
            ruta_frames (str): Ruta donde se guardarán los frames extraídos.
        """
        self.ruta_frames = os.path.normpath(ruta_frames)

    def extraer_cuadros(self):
        """
        Extrae cuadros de un video dado y los guarda como imágenes.
        """

        if not self.ruta_video or not self.ruta_frames:
            print("Las rutas de video y frames deben estar establecidas.")
            return

        video_output_folder = self.ruta_frames  # Carpeta de salida
        os.makedirs(video_output_folder, exist_ok=True)  # Asegurar que la carpeta de salida existe

        # Procesar el video
        cam = cv2.VideoCapture(self.ruta_video)
        currentframe = 0
        previous_frame = None
        last_saved_frame = None
        threshold = 5
        white_threshold = 200
        similarity_threshold = 10
        text_threshold = 300

        while True:
            ret, frame = cam.read()
            if not ret:
                break

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if currentframe == 0:
                name = f'{video_output_folder}/frame{currentframe}.jpg'
                cv2.imwrite(name, frame)
                currentframe += 1
                last_saved_frame = gray_frame
            elif previous_frame is not None:
                diff = cv2.absdiff(previous_frame, gray_frame)
                mean_diff = np.mean(diff)
                white_ratio = np.mean(gray_frame > white_threshold) * 100

                similarity_mean = np.mean(cv2.absdiff(last_saved_frame, gray_frame)) if last_saved_frame is not None else float('inf')

                if mean_diff > threshold and white_ratio > 10 and similarity_mean > similarity_threshold:
                    text = pytesseract.image_to_string(gray_frame)
                    if len(text.strip()) > text_threshold:
                        name = f'{video_output_folder}/frame{currentframe}.jpg'
                        cv2.imwrite(name, frame)
                        currentframe += 1
                        last_saved_frame = gray_frame

            previous_frame = gray_frame

        cam.release()

    def __limpiar_rutas(self):
        """
        Restaura las rutas de video y frames a su estado original.
        """
        self.ruta_video = None
        self.ruta_frames = None

    def procesar_video(self, ruta_video, ruta_frames):
        """
        Procesa el video dado y extrae los cuadros.
        """
        self.set_ruta_video(ruta_video)
        self.set_ruta_frames(ruta_frames)
        print(f"Procesando video {self.ruta_video}...")
        print(f"Extrayendo cuadros en {self.ruta_frames}...")
        self.extraer_cuadros()
        self.__limpiar_rutas()

# def main():
#     extractor = ExtraccionCuadros()
#     extractor.procesar_video(r"D:\DOCUMENTOS\VirtualEnvPy\dataScience\source\Servicio\ServicioF\Videos\1.mp4", r"D:\DOCUMENTOS\VirtualEnvPy\dataScience\source\Servicio\ServicioF\Videos\frames")

# if __name__ == "__main__":
#     main()