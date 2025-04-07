import os
from TextoJson import TextoJson

def main():
    # Directorios
    carpeta_txt = "expedientes"
    carpeta_json = "jsons"

    # Crear la carpeta de salida si no existe
    os.makedirs(carpeta_json, exist_ok=True)

    # Obtener la lista de archivos en la carpeta de expedientes
    archivos_txt = [f for f in os.listdir(carpeta_txt) if f.endswith(".txt")]

    procesador = TextoJson()
    procesados = 0  # Contador de archivos procesados

    for archivo in archivos_txt:
        ruta_txt = os.path.join(carpeta_txt, archivo)

        # Si el archivo ya tiene (LISTO), saltarlo
        if "(LISTO)" in archivo:
            continue

        # Definir la ruta del archivo JSON de salida
        ruta_json = os.path.join(carpeta_json, archivo.replace(".txt", ".json"))

        print(f"Procesando: {archivo}...")

        # Convertir el TXT a JSON
        procesador.convertir_txt_json(ruta_txt, carpeta_json)

        # Renombrar el archivo TXT original con (LISTO)
        nuevo_nombre = archivo.replace(".txt", " (LISTO).txt")
        os.rename(ruta_txt, os.path.join(carpeta_txt, nuevo_nombre))

        print(f"{archivo} procesado y guardado en {ruta_json}\n")
        procesados += 1

    # Mensaje si no se procesó ningún archivo
    if procesados == 0:
        print("No se encontraron nuevos expedientes para procesar.")
    else:
        print(f"Procesamiento completado. Se procesaron {procesados} expedientes.")

if __name__ == "__main__":
    main()
