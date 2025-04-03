import cv2
import os
import numpy as np
import pytesseract
import re
import shutil

def eliminar_frames_similares(folder, similitud_umbral=5):
    """Elimina frames similares dentro de una carpeta."""
    frames = sorted([f for f in os.listdir(folder) if f.endswith('.jpg')], key=lambda x: int(re.search(r'\d+', x).group()))
    if not frames:
        return
    
    for i in range(len(frames) - 1, 0, -1):  # Recorremos de atrás hacia adelante
        frame_actual = os.path.join(folder, frames[i])
        frame_anterior = os.path.join(folder, frames[i - 1])

        img_actual = cv2.imread(frame_actual, cv2.IMREAD_GRAYSCALE)
        img_anterior = cv2.imread(frame_anterior, cv2.IMREAD_GRAYSCALE)

        if img_actual is None or img_anterior is None:
            continue

        diferencia = np.mean(cv2.absdiff(img_anterior, img_actual))

        if diferencia < similitud_umbral:  # Si la diferencia es pequeña, eliminamos el frame más reciente
            os.remove(frame_actual)
            print(f"Eliminado {frame_actual} por ser similar a {frame_anterior}")

def main():
    # Configurar Tesseract
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    # Directorios
    video_folder = "Videos"
    output_folder = "frame_extraction"
    processed_folder = "procesado"

    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(processed_folder, exist_ok=True)

    videos = [f for f in os.listdir(video_folder) if f.endswith(('.mp4', '.avi', '.mov'))]

    for video in videos:
        video_path = os.path.join(video_folder, video)

        # Obtener el siguiente número de carpeta
        existing_folders = sorted([int(re.match(r'^(\d+)', f).group(1)) for f in os.listdir(output_folder) if re.match(r'^\d+', f)])
        next_folder_num = 1
        for num in existing_folders:
            if num == next_folder_num:
                next_folder_num += 1
            else:
                break

        video_output_folder = os.path.join(output_folder, str(next_folder_num))
        os.makedirs(video_output_folder, exist_ok=True)

        new_video_name = f"{next_folder_num}.mp4"
        new_video_path = os.path.join(video_folder, new_video_name)
        os.rename(video_path, new_video_path)

        cam = cv2.VideoCapture(new_video_path)
        currentframe = 0
        previous_frame = None
        last_saved_frame = None
        threshold = 5
        white_threshold = 200
        similarity_threshold = 5
        text_threshold = 200
        
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
        cv2.destroyAllWindows()

        # Llamar a la función para eliminar frames similares después de la extracción
        eliminar_frames_similares(video_output_folder, similitud_umbral=5)

        # Mover el video procesado a la carpeta "procesado"
        processed_video_path = os.path.join(processed_folder, new_video_name)
        shutil.move(new_video_path, processed_video_path)

if __name__ == "__main__":
    main()
