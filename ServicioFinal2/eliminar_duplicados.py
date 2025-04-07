import cv2
import os
import numpy as np
import pytesseract
import re
from difflib import SequenceMatcher
from langdetect import detect

ENGLISH_KEYWORDS = ['the', 'and', 'is', 'in', 'on', 'with', 'for', 'by', 'from', 'at', 'this', 'that', 'it', 'an', 'as', 'be', 'are', 'was', 'were', 'to', 'of', 'a', 'we', 'you', 'they', 'he', 'she', 'can', 'which', 'older', 'patients', 'but', 'required', 'avoid', 'febrile', 'neutropenia', 'combined', 'regimen', 'documented']

def calcular_similitud(imagen1, imagen2):
    """Calcula la diferencia media absoluta entre dos imágenes."""
    return np.mean(cv2.absdiff(imagen1, imagen2))

def texto_similar(texto1, texto2, umbral=0.7):
    """Verifica si dos textos son similares usando la relación de longitud y caracteres iguales."""
    return SequenceMatcher(None, texto1, texto2).ratio() >= umbral

def es_ingles(texto, min_palabras=100):
    """Determina si un texto está en inglés usando detección automática de idioma."""
    try:
        idioma = detect(texto)
        if idioma == 'en':
            return True
    except:
        pass
    palabras = re.findall(r'\b\w+\b', texto.lower())
    palabras_en = sum(1 for palabra in palabras if palabra in ENGLISH_KEYWORDS)
    print(f"Palabras en inglés detectadas: {palabras_en}/{len(palabras)}")
    return palabras_en >= min_palabras

def eliminar_frames_duplicados(carpeta, similitud_umbral=5, umbral_texto=0.7):
    """Elimina frames similares dentro de una carpeta considerando el contenido textual."""
    frames = sorted([f for f in os.listdir(carpeta) if f.endswith('.jpg')], key=lambda x: int(re.search(r'\d+', x).group()))
    if not frames:
        return
    
    i = 0
    while i < len(frames):
        frame1_path = os.path.join(carpeta, frames[i])
        img1 = cv2.imread(frame1_path, cv2.IMREAD_GRAYSCALE)
        if img1 is None:
            i += 1
            continue
        
        texto1 = pytesseract.image_to_string(img1).strip()
        # Se ha eliminado la condición para eliminar frames en inglés
        
        j = i + 1
        while j < len(frames):
            frame2_path = os.path.join(carpeta, frames[j])
            img2 = cv2.imread(frame2_path, cv2.IMREAD_GRAYSCALE)
            if img2 is None:
                j += 1
                continue
            
            diferencia = calcular_similitud(img1, img2)
            if diferencia < similitud_umbral:
                texto2 = pytesseract.image_to_string(img2).strip()
                if texto_similar(texto1, texto2, umbral_texto):
                    os.remove(frame2_path)
                    print(f"Eliminado {frame2_path} por similitud visual y textual con {frame1_path}")
                    frames.pop(j)
                    continue
            j += 1
        i += 1

def procesar_todas_las_carpetas(frame_extraction_folder):
    """Procesa todas las carpetas dentro de 'frame_extraction' eliminando frames duplicados."""
    carpetas = sorted([f for f in os.listdir(frame_extraction_folder) if os.path.isdir(os.path.join(frame_extraction_folder, f))])
    
    for carpeta in carpetas:
        carpeta_path = os.path.join(frame_extraction_folder, carpeta)
        print(f"Procesando carpeta: {carpeta_path}")
        eliminar_frames_duplicados(carpeta_path)

def main():
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    frame_extraction_folder = "frame_extraction"
    procesar_todas_las_carpetas(frame_extraction_folder)
    
if __name__ == "__main__":
    main()
