from ocr_processor import OCRProcessor

def main():
    ocr_processor = OCRProcessor(r"D:\DOCUMENTOS\VirtualEnvPy\dataScience\source\Servicio\OCR_JSON\videos", r"D:\DOCUMENTOS\VirtualEnvPy\dataScience\source\Servicio\OCR_JSON\destino", r"D:\DOCUMENTOS\VirtualEnvPy\dataScience\source\Servicio\OCR_JSON\extraccion_texto\correccion.txt")
    ocr_processor.procesar_videos()

if __name__ == "__main__":
    main()