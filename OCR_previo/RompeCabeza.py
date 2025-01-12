import re
import json

def CrearJson(txt):
    a = 1
    lineas = txt.splitlines() #divido el texto en lineas
    data = {}
    i = 0
    linea_new = None

    while i < len(lineas):
        linea_actual = lineas[i].strip()
        #linea actual esta vacia
        if linea_actual.strip() == '':
            i+=1
        #nos aseguramos de no estar en ultima linea del documento
        elif i < len(lineas) - 1:
            siguiente_linea = lineas[i + 1].strip()
            # si la linea siguiente esta vacia
            if siguiente_linea == '':
                if ':' in linea_actual: #si hay dos puntos en la linea actual
                    partes = linea_actual.split(':', 1) #cortamos la linea actual en dos partes
                    #despues de los puntos hay algo
                    if partes[1].strip(): #verificamos si tenemos texto de lado derecho de los puntos #partes = linea_actual.split(':', 1)
                        clave_actual = partes[0].strip()  # Asignar lo que está a la izquierda de los dos puntos como clave
                        valor_actual = partes[1].strip()  # Asignar lo que está a la derecha como valor
                        data[clave_actual] = valor_actual
                        i += 1
                    else:
                        i+=1

                else:
                    data["detalles" + str(a)] = linea_actual
                    a+=1
                    i+=1
            elif ':' in siguiente_linea:
                if ':' in linea_actual:
                    partes = linea_actual.split(':', 1)  # cortamos la linea actual en dos partes
                    # despues de los puntos hay algo
                    if partes[1].strip():  # verificamos si tenemos texto de lado derecho de los puntos
                        clave_actual = partes[0].strip()  #partes = linea_actual.split(':', 1) esta linea hiba antes de esta otra
                        valor_actual = partes[1].strip()
                        data[clave_actual] = valor_actual
                        i += 1

                    else: #añadir que hacer en caso de tener los dos puntos pero nada de lado derecho
                        clave_actual = linea_actual.split()
                        valor_actual = ""
                        data[clave_actual] = valor_actual
                        i+=1

                else:
                    data["detalles" + str(a)] = linea_actual
                    a += 1
                    i += 1

            elif ':' in linea_actual:
                linea_new = linea_actual + " " + siguiente_linea
                i+=1

            else:
                linea_new = linea_new + " " + siguiente_linea
                lineaSigui_Sigui = lineas[i + 2].strip()
                if lineaSigui_Sigui == '' or ':' in lineaSigui_Sigui:
                    partes = linea_new.split(':', 1)
                    clave_actual = partes[0].strip()  # partes = linea_actual.split(':', 1) esta linea hiba antes de esta otra
                    valor_actual = partes[1].strip()
                    data[clave_actual] = valor_actual
                    linea_new=None
                    i += 2
                else:
                    i+1
        i+=1
    return data

archivotxt = '/home/josuevj/Documents/uni/servicio/sources/OCR_previo/out/OCR_Borders/TextoExtraido2.txt'

# leyendo el contenido del archivo de texto
with open(archivotxt, 'r', encoding='latin-1') as file:
    texto = file.read()

# llamado de la funcion
resultado = CrearJson(texto)

# creando el archivo JSON
with open('/home/josuevj/Documents/uni/servicio/sources/OCR_previo/out/Rompecabezas/AutomaticRC1.json', 'w', encoding='utf-8') as json_file:
    json.dump(resultado, json_file, ensure_ascii=False, indent=4)