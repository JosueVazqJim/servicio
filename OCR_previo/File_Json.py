import json
import re

# Función para procesar el contenido del archivo
def procesamiento(archivo_txt, archivo_json):
    try:
        with open(archivo_txt, 'r', encoding='utf-8') as file:
            contenido = file.readlines()
    except UnicodeDecodeError:
        # Si hay un error de codificación UTF-8, intentar con otra codificación
        with open(archivo_txt, 'r', encoding='ISO-8859-1') as file:
            contenido = file.readlines()

    # Unir líneas divididas por saltos de línea pero que forman parte de la misma frase
    texto = re.sub(r'\n(?=[a-zA-Z])', ' ', texto)

    # Separar por secciones de texto
    lineas = texto.splitlines()

    # Limpiar las líneas y eliminar líneas vacías
    contenido = [linea.strip() for linea in contenido if linea.strip()]

    # Crear un diccionario para almacenar la información
    data = {
        "informacion_personal": {},
        "diagnostico": {},
        "antecedentes_familiares": {},
        "historial_medico": {},
        "comorbilidades": []
    }

    # Procesar las líneas del contenido
    for linea in contenido:
        # Capturar información personal
        match_id = re.match(r'^(GACMC\s*/\s*(.+?)\s*/\s*(\d+\s*años)\s*/\s*(.*))$', linea)
        if match_id:
            data["informacion_personal"]["ID"] = match_id.group(1).strip()
            data["informacion_personal"]["Nombre"] = match_id.group(2).strip()
            data["informacion_personal"]["Edad"] = match_id.group(3).strip()
            data["informacion_personal"]["Titulo"] = match_id.group(4).strip()
            continue

        # Capturar información de residencia
        match_residencia = re.match(r'^Originaria y residente:\s*(.*)', linea)
        if match_residencia:
            data["informacion_personal"]["Residencia"] = match_residencia.group(1).strip()
            continue

        # Capturar ocupación
        match_ocupacion = re.match(r'^Ocupación:\s*(.*)', linea)
        if match_ocupacion:
            data["informacion_personal"]["Ocupacion"] = match_ocupacion.group(1).strip()
            continue

        # Capturar seguridad social
        match_seguridad = re.match(r'^Seguridad social:\s*(.*)', linea)
        if match_seguridad:
            data["informacion_personal"]["Seguridad_social"] = match_seguridad.group(1).strip()
            continue

        # Capturar diagnóstico
        match_diagnostico = re.match(r'^Diagnóstico:\s*(.*)', linea)
        if match_diagnostico:
            data["diagnostico"]["Diagnostico"] = match_diagnostico.group(1).strip()
            continue

        # Capturar antecedentes familiares
        match_ahf = re.match(r'^AHF oncológicos:\s*(.*)', linea)
        if match_ahf:
            data["antecedentes_familiares"]["AHF"] = match_ahf.group(1).strip()
            continue

        # Capturar información de historial médico
        match_historial = re.match(r'^-?\s*(.*)', linea)
        if match_historial:
            if "Cirugías" in linea:
                data["historial_medico"]["Cirugias"] = linea.split(":")[1].strip()
            else:
                # Agregar comorbilidades
                data["comorbilidades"].append(match_historial.group(1).strip())

    # Guardar el diccionario como JSON
    with open(archivo_json, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)


# Ejemplo de uso
ruta_txt = '/home/josuevj/Documents/uni/servicio/sources/OCR_previo/out/OCR_Borders/TextoExtraido2.txt'  # Reemplaza con la ruta de tu archivo
ruta_json = '/home/josuevj/Documents/uni/servicio/sources/OCR_previo/out/File_json/archivo3.json'  # Nombre del archivo JSON a crear
procesamiento(ruta_txt, ruta_json)