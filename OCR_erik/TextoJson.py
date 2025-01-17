import json
import re

class TextoJson:
    def __init__(self, archivo):
        self.archivo = archivo
        self.data = {
            "informacion_paciente": {},
            "residencia_origen": {},
            "informacion_general": {},
            "diagnostico": {},
            "antecedentes_familiares": {},
            "habitos_estilo_vida": {},
            "historial_medico": {},
            "historia_personal": {},
            "comorbilidades": []
        }

        self.secciones = {
            "informacion_paciente": ["clave", "id", "edad", "medico_tratante"],
            "informacion_general": ["origen", "residencia", "ocupacion", "ss"],
            "diagnostico": ["diagnostico"],
            "antecedentes_familiares": ["ahf"],
            "habitos_estilo_vida": [],
            "historial_medico": [],
            "historia_personal": [],
            "comorbilidades": []
        }

    def procesar(self):
        with open(self.archivo, 'r', encoding='utf-8') as file:
            contenido = file.readlines()

        contenido = [linea.strip() for linea in contenido if linea.strip()]

        seccion_actual = None

        # Procesar las líneas del contenido
        for linea in contenido:
            linea = linea.strip().lower()
            print(linea)  
            
            # Capturar información personal
            match_id = re.match(r'^(gacmc)\s*/\s*(.+?)\s*/\s*(\d+\s*años)\s*/\s*(.*)$', linea)
            if match_id:
                self.data["informacion_paciente"]["clave"] = match_id.group(1).strip()
                self.data["informacion_paciente"]["id"] = match_id.group(2).strip()
                self.data["informacion_paciente"]["edad"] = match_id.group(3).strip()
                self.data["informacion_paciente"]["medico_tratante"] = match_id.group(4).strip()
                continue

        self.imprimir()

            
    def guardar_json(self, salida):
        with open(salida, 'w', encoding='utf-8') as file:
            json.dump(self.data, file, indent=4, ensure_ascii=False)

    def imprimir(self):
        print(json.dumps(self.data, indent=4, ensure_ascii=False))

# Ejemplo de uso
archivo_entrada = "D:\DOCUMENTOS\VirtualEnvPy\dataScience\source\Servicio\OCR_erik\TextoExtraido2.txt"  # Archivo de entrada con el texto
archivo_salida = "resultado.json"  # Archivo JSON de salida

procesador = TextoJson(archivo_entrada)
procesador.procesar()
# procesador.guardar_json(archivo_salida)