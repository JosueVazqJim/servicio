from ocr_processor import OCRProcessor

def main():
    ocr_processor = OCRProcessor("ruta_videos", "ruta_destino")
    ocr_processor.procesar_videos()

if __name__ == "__main__":
    main()