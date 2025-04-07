import Videos
import OCR_Final
import procesar_expedientes
import eliminar_duplicados
import postprocesamiento

print("Ejecutando Videos.py...")
Videos.main()

print("Ejecutando eliminar_duplicados.py...")
eliminar_duplicados.main()

print("Ejecutando OCR_Final.py...")
OCR_Final.main()

print("Ejecutando postprocesamiento.py...")
postprocesamiento.main()

print("Ejecutando procesar_expedientes.py...")
procesar_expedientes.main()
