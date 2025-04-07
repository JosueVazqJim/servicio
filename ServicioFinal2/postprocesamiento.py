import re
import os

def corregir_diagnostico(carpeta):
    keywords = [
        "Comorbilidades:",
        "Ocupación:",
        "Seguridad social:",
        "AHF oncológicos:",
        "Cirugías:"
    ]
    
    for archivo in os.listdir(carpeta):
        if archivo.endswith(".txt"):
            ruta_archivo = os.path.join(carpeta, archivo)
            with open(ruta_archivo, "r", encoding="utf-8") as f:
                lineas = f.readlines()
            
            nuevas_lineas = []
            i = 0
            while i < len(lineas):
                linea_actual = lineas[i].strip()
                if linea_actual == "NO HAY DGT":
                    # Buscar si hay alguna palabra clave en las próximas 20 líneas
                    encontrado = any(
                        any(keyword in lineas[j] for keyword in keywords)
                        for j in range(i + 1, min(i + 21, len(lineas)))
                    )
                    if encontrado:
                        # Saltar la línea "NO HAY DGT"
                        i += 1
                        # Conservar líneas vacías si las hay
                        while i < len(lineas) and lineas[i].strip() == "":
                            nuevas_lineas.append(lineas[i])
                            i += 1
                        if i < len(lineas):
                            linea_con_texto = lineas[i].strip()
                            nuevas_lineas.append(f"Diagnóstico: {linea_con_texto}\n")
                            i += 1  # evitar que esta línea vuelva a ser procesada
                        continue
                    else:
                        nuevas_lineas.append(lineas[i])
                        i += 1
                else:
                    nuevas_lineas.append(lineas[i])
                    i += 1
            
            with open(ruta_archivo, "w", encoding="utf-8") as f:
                f.writelines(nuevas_lineas)

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
    # Nueva expresión regular:
    # - Captura opcional del guion y espacios al inicio.
    # - Cada token (G, P, C, A) se captura con la posibilidad de tener dígitos o la letra O.
    # - La parte "A" puede tener un carácter extra que se captura en el grupo "extra".
    # - Se acepta que entre G y P no exista espacio (caso "GOPO...") o que haya espacios.
    patron = re.compile(
        r"^(?P<pref>-\s*)?"                           # opcional guion y espacios iniciales
        r"(?P<G>G(?:\d+|O))"                          # G: "G" seguido de dígitos o "O"
        r"(?P<P>P(?:\d+|O))"                          # P: "P" seguido de dígitos o "O"
        r"\s*"                                       # espacios opcionales
        r"(?P<C>C(?:\d+|O))"                          # C: "C" seguido de dígitos o "O"
        r"\s*"                                       # espacios opcionales
        r"(?P<A>A(?:\d+|O))"                          # A: "A" seguido de dígitos o "O"
        r"(?P<extra>[A-Z])?"                          # posible carácter extra (ej. D)
        r"(?P<rest>.*)$"                             # resto de la línea (comentarios u otro)
    )
    
    for archivo in os.listdir(carpeta):
        ruta_archivo = os.path.join(carpeta, archivo)
        if os.path.isfile(ruta_archivo) and archivo.endswith(".txt"):
            with open(ruta_archivo, "r", encoding="utf-8") as f:
                lineas = f.readlines()
            
            with open(ruta_archivo, "w", encoding="utf-8") as f:
                for linea in lineas:
                    # Se quitan espacios a los extremos para evitar problemas con la regex
                    match = patron.match(linea.strip())
                    if match:
                        pref = match.group("pref") or ""
                        G = match.group("G")
                        P = match.group("P")
                        C = match.group("C")
                        A = match.group("A")
                        extra = match.group("extra") or ""
                        rest = match.group("rest")
                        
                        # Aplicar las correcciones específicas del diccionario a cada token
                        G = correcciones.get(G, G)
                        P = correcciones.get(P, P)
                        C = correcciones.get(C, C)
                        A = correcciones.get(A, A)
                        
                        # Reconstruir la línea agregando un espacio entre A y el extra, si existe
                        extra = f" {extra}" if extra else ""
                        nueva_linea = f"{pref}{G} {P} {C} {A}{extra}{rest}\n"
                    else:
                        nueva_linea = linea
                    
                    # Aplicar correcciones adicionales en caso de coincidencias parciales
                    for palabra_incorrecta, palabra_correcta in correcciones.items():
                        nueva_linea = re.sub(rf'(?<!\w){re.escape(palabra_incorrecta)}(?!\w)', palabra_correcta, nueva_linea)
                    
                    f.write(nueva_linea)

def main():
    # Primero se corrige el diagnóstico en cada expediente
    corregir_diagnostico("expedientes")
    # Luego se corrigen las líneas con la estructura de "G P C A..."
    corregir_lineas_en_txt("expedientes", "correccion.txt")
    # Por último se aplica la corrección de EC en cada expediente
    procesar_expedientes("expedientes")

if __name__ == "__main__":
    main()
