import cv2
import os
import numpy as np
import pytesseract
import unicodedata

# Configurar Tesseract (asegúrate de que esté instalado y en el PATH del sistema)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Función para normalizar nombres de carpetas eliminando caracteres especiales
def normalize_folder_name(name):
    return ''.join(
        c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn'
    )

# Cargar el video
video_name = "D:\DOCUMENTOS\VirtualEnvPy\dataScience\source\Servicio\OCR_erik\ExtraccionImagenes\Zoom Reunión 2023-08-29 07-46-55.mp4"
cam = cv2.VideoCapture(video_name)

# Crear carpeta de destino para las imágenes extraídas
output_folder = r"D:\DOCUMENTOS\VirtualEnvPy\dataScience\source\Servicio\OCR_erik\ExtraccionImagenes\cuadros"
video_base_name = os.path.splitext(os.path.basename(video_name))[0]
normalized_folder_name = normalize_folder_name(video_base_name)  # Normalizar el nombre del video
video_folder = os.path.join(output_folder, normalized_folder_name)

if not os.path.exists(video_folder):
    os.makedirs(video_folder)

# Variables iniciales
currentframe = 0
previous_frame = None
last_saved_frame = None
threshold = 5  # Umbral para detectar cambios significativos de iluminación
white_threshold = 200  # Umbral para determinar predominancia de blanco
similarity_threshold = 10  # Umbral para considerar frames como similares
text_threshold = 300  # Cantidad mínima de caracteres detectados para guardar el frame

while True:
    ret, frame = cam.read()

    if not ret:
        break

    # Convertir el frame actual a escala de grises para análisis de iluminación
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if currentframe == 0:
        # Guardar siempre el primer frame
        name = os.path.join(video_folder, f'frame{currentframe}.jpg')
        print(f'Creating... {name}')
        cv2.imwrite(name, frame)
        currentframe += 1
        last_saved_frame = gray_frame

    elif previous_frame is not None:
        # Calcular la diferencia absoluta entre el frame actual y el anterior
        diff = cv2.absdiff(previous_frame, gray_frame)

        # Calcular la media de la diferencia para determinar el nivel de cambio
        mean_diff = np.mean(diff)

        # Comprobar si el color blanco prevalece en el frame
        white_ratio = np.mean(gray_frame > white_threshold) * 100

        # Verificar similitud con el último frame guardado
        if last_saved_frame is not None:
            similarity_diff = cv2.absdiff(last_saved_frame, gray_frame)
            similarity_mean = np.mean(similarity_diff)
        else:
            similarity_mean = float('inf')  # Forzar guardado si no hay referencia previa

        if mean_diff > threshold and white_ratio > 10 and similarity_mean > similarity_threshold:
            # Detectar texto en el frame
            text = pytesseract.image_to_string(gray_frame)
            if len(text.strip()) > text_threshold:  # Comprobar si hay suficiente texto
                # Guardar frame si cumple con los criterios
                name = os.path.join(video_folder, f'frame{currentframe}.jpg')
                print(f'Creating... {name}')
                cv2.imwrite(name, frame)
                currentframe += 1
                last_saved_frame = gray_frame
            else:
                print(f'Skipping frame {currentframe} - insufficient text detected')

    # Actualizar el frame anterior
    previous_frame = gray_frame

# Liberar recursos
cam.release()
# cv2.destroyAllWindows()
