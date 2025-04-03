import re
import os

def corregir_ec(texto):
    # Buscar el diagnóstico
    diagnostico_match = re.search(r'Diagnóstico:.*?EC ([IVXLCDM]+[A-Z]*)', texto)
    
    if not diagnostico_match:
        return texto
    
    ec_correcto = diagnostico_match.group(1)  # Extrae el EC correcto
    
    # Buscar la extensión del tumor
    extension_match = re.search(r'(Extensión del tumor:\n\n.*?EC )([IVXLCDM]+[A-Z]*)', texto)
    
    if extension_match:
        ec_detectado = extension_match.group(2)  # Extrae el EC detectado
        if ec_detectado != ec_correcto:
            # Reemplazar el EC incorrecto por el correcto
            texto = texto.replace(f'EC {ec_detectado}', f'EC {ec_correcto}', 1)
    
    return texto

def procesar_expedientes(carpeta):
    for archivo in os.listdir(carpeta):
        if archivo.endswith(".txt"):
            ruta_archivo = os.path.join(carpeta, archivo)
            with open(ruta_archivo, "r", encoding="utf-8") as f:
                texto = f.read()
            
            texto_corregido = corregir_ec(texto)
            
            with open(ruta_archivo, "w", encoding="utf-8") as f:
                f.write(texto_corregido)

def cargar_correcciones(archivo_correccion):
    correcciones = {}
    if not os.path.exists(archivo_correccion):
        print(f"El archivo de correcciones '{archivo_correccion}' no existe.")
        return correcciones
    
    with open(archivo_correccion, "r", encoding="utf-8") as f:
        clave = None
        for linea in f:
            linea = linea.strip()
            if linea.startswith("\"") and linea.endswith("\""):
                clave = linea.strip('"')
            elif clave and linea:
                for palabra in linea.split(','):
                    correcciones[palabra] = clave
    return correcciones

def corregir_lineas_en_txt(carpeta, archivo_correccion):
    correcciones = cargar_correcciones(archivo_correccion)
    patron = re.compile(r"(-\s*)(G\S*)\s*(P\S*)\s*(C\S*)\s*(A\S*)(.*)")
    
    for archivo in os.listdir(carpeta):
        ruta_archivo = os.path.join(carpeta, archivo)
        if os.path.isfile(ruta_archivo) and archivo.endswith(".txt"):
            with open(ruta_archivo, "r", encoding="utf-8") as f:
                lineas = f.readlines()
            
            with open(ruta_archivo, "w", encoding="utf-8") as f:
                for linea in lineas:
                    coincidencia = patron.search(linea)
                    if coincidencia:
                        partes = [coincidencia.group(1)] + [
                            correcciones.get(coincidencia.group(i), coincidencia.group(i)) for i in range(2, 6)
                        ] + [coincidencia.group(6)]
                        nueva_linea = " ".join(partes) + "\n"
                    else:
                        nueva_linea = linea
                    
                    # Aplicar correcciones solo a palabras completas o unidas a signos/puntuaciones
                    for palabra_incorrecta, palabra_correcta in correcciones.items():
                        nueva_linea = re.sub(rf'(?<!\w){re.escape(palabra_incorrecta)}(?!\w)', palabra_correcta, nueva_linea)
                    
                    f.write(nueva_linea)

def main():
    # Llamada a la función con la carpeta 'expedientes' y el archivo 'correccion.txt'
    corregir_lineas_en_txt("expedientes", "correccion.txt")

    # Ejecutar la corrección en la carpeta "expedientes"
    procesar_expedientes("expedientes")

if __name__ == "__main__":
    main()