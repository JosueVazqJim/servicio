import json
import re
import os
from limpiador_texto import LimpiezaTexto

class TextoJson:
    """
    Clase para procesar y estructurar texto médico en un formato JSON.

    Esta clase toma un archivo de texto con información médica, la procesa y la estructura
    en un formato JSON que incluye secciones como antecedentes personales, antecedentes familiares,
    estadía  tumoral, inmunohistoquímica tumoral, y tipo de cáncer.
    Basta con usar el metodo convertir_txt_json para convertir un archivo de texto a un archivo JSON.
    Se le pasa la ruta del archivo de texto y la ruta de destino donde se guardará el archivo JSON.

    Attributes:
        limpiador (LimpiezaTexto): Instancia de la clase LimpiezaTexto para procesar el texto.
        informacion (list): Lista de líneas de texto procesadas.
        data (dict): Diccionario que almacena la información estructurada en formato JSON.
        rutaTxt (str): Ruta del archivo de texto de entrada.
        rutaDestino (str): Ruta de la carpeta donde se guardarán los archivos JSON.
    """

    def __init__(self):
        """
        Inicializa la clase TextoJson.
        """
        self.rutaTxt = None
        self.rutaDestino = None
        self.limpiador = LimpiezaTexto()
        self.informacion = []
        self.data = {
            "antecedentes_personales": {},
            "antecedentes_familiares": {},
            "estadía_tumoral": {},
            "inmunohistoquímica_tumoral": {},
            "tipo": {},
        }
        self.mama = None

    def __limpiar_texto(self):
        """
        Limpia el texto de entrada utilizando la instancia de LimpiezaTexto.
        """
        self.informacion = self.limpiador.limpiar_archivo(self.rutaTxt)

    def setrutaTxt(self, rutaTxt):
        self.rutaTxt = rutaTxt

    def setrutaDestino(self, rutaDestino):
        self.rutaDestino = rutaDestino

    import re

    def __detector_pezones(self):
        """
        Establece el lado de la mama del caso actual.
        Solo considera las mamas afectadas por cáncer, basándose en las secciones de diagnóstico,
        extensión del tumor o biología tumoral.
        """
        mama_izquierda_flag = False
        mama_derecha_flag = False

        # Palabras clave que indican las secciones relevantes
        secciones_relevantes = ["diagnóstico", "extensión del tumor", "biología tumoral", "mama"]

        # Añadir patrón flexible para "mama con lesiones"
        patron_mama_lesiones = re.compile(r'\bmama\s*(izquierda|derecha|bilateral)\s*con.*lesi.*', re.IGNORECASE)

        for linea in self.informacion:
            # Verificar si la línea pertenece a una sección relevante
            if any(linea.startswith(seccion) for seccion in secciones_relevantes):
                if "mama izquierda" in linea.lower() or patron_mama_lesiones.search(linea) and "izquierda" in linea.lower():
                    mama_izquierda_flag = True
                if "mama derecha" in linea.lower() or patron_mama_lesiones.search(linea) and "derecha" in linea.lower():
                    mama_derecha_flag = True
                if "bilateral" in linea.lower():
                    self.mama = "bilateral"
                    print(f"Mama detectada: {self.mama}")
                    return

        # Determinar el lado de la mama basado en las banderas
        if mama_izquierda_flag and mama_derecha_flag:
            self.mama = "bilateral"
        elif mama_izquierda_flag:
            self.mama = "mama_izquierda"
        elif mama_derecha_flag:
            self.mama = "mama_derecha"  
        else:
            self.mama = None  # Si no se detecta ninguna mama afectada

        print(f"Mama detectada: {self.mama}")


    def __extraer_nombre_txt(self):
        """
        Extrae el nombre del archivo de texto de la ruta de archivo.
        devuelve el nombre del archivo de texto
        """
        return os.path.basename(self.rutaTxt)

    def __extract_units(self, data):
        """
        Extrae unidades de tiempo (años, meses, días, horas) de una cadena de texto.

        Args:
            data (str): Cadena de texto que contiene las unidades de tiempo.

        Returns:
            list: Lista de tuplas con el valor y la unidad de tiempo.
        """
        # Regular expression to match patterns like "años", "meses", "días", "horas"
        unit_pattern = re.compile(
            r'\b(\d+\.?\d*)\s*(año|años|mes|meses|día|días|hora|horas)\b|\b(año|años|mes|meses|día|días|hora|horas)\s*(\d+\.?\d*)\b',
            re.IGNORECASE
        )
        matches = unit_pattern.findall(data)

        units = []
        for match in matches:
            if match[0] and match[1]:  # Caso: "1 año" o "1.5 años"
                value = float(match[0]) if '.' in match[0] else int(match[0])  # Parseo de dígitos
                units.append((value, match[1].lower()))
            elif match[2] and match[3]:  # Caso: "año 1" o "años 1.5"
                value = float(match[3]) if '.' in match[3] else int(match[3])  # Parseo de dígitos
                units.append((value, match[2].lower()))

        return units

    def __extraer_datos_antecedentes_personales(self):
        """
        Extrae y estructura los datos de antecedentes personales del texto procesado.

        Los datos se almacenan en el diccionario `data` bajo la clave "antecedentes_personales".
        """
        # secciones de antecedentes_personales
        antecedentes_personales_secciones = {
            "edad": None,
            "sexo": "femenino",
            "peso": None,
            "talla": None,
            "preferencia": None,
            "índice_tabáquico": {
                "fuma": None,
                "observaciones": None
            },
            "alcohol": None,
            "drogas": None,
            "comorbilidades": None,
            "antecedentes_ginecológicos": {
                "fum": None,
                "menarca": None,
                "embarazos": None,
                "partos": None,
                "trh": None,
                "aco": None,
                "mpf": None,
                "estado_hormonal": None,
                "métodos_anticonceptivos": None
            }
        }

        #palaras clave para antecedentes_personales que buscaremos en el texto
        antecedentes_personales_keywords = [
            "edad", "sexo", "peso", "talla", "preferencia",
            "índice tabáquico", "tabaco", "tabaquismo", "alcohol", "drogas",
            "comorbilidades", "antecedentes ginecológicos", "menarca", "embarazos", "partos", "fum", "trh", "mpf", "aco", "estado hormonal", "métodos anticonceptivos"
        ]

        isEdad = False

        # Agregar una regex para detectar edades en el formato "XX años"
        edad_regex = re.compile(
            r'\b(?:edad:?\s*(\d+)(?:\s*años)?)|(?:\b(\d+)\s*años(?:\s*de\s*edad)?)|^(\w+)\s*/\s*(.+?)\s*/\s*(\d+\s*años)\s*/\s*(.*)$|(?:\b(\d+)\s*años(?:\s*de\s*edad)?)|^(\w+)\s*/\s*(.+?)\s*/\s*(\d+\s*años(?:\s*y\s*\d+\s*meses)?)\s*/\s*(.*)$',re.IGNORECASE
        )
        for linea in self.informacion:
            # Buscar una edad en el formato específico
            match = edad_regex.match(linea)
            if match:
                edad_valor = linea

                if edad_valor:
                    try:
                        unidades = self.__extract_units(edad_valor)
                        edad_dict = {}
                        for cantidad, unidad in unidades:
                            if unidad == "años":
                                edad_dict["años"] = cantidad
                            elif unidad == "meses":
                                edad_dict["meses"] = cantidad
                            elif unidad == "días":
                                edad_dict["días"] = cantidad
                            elif unidad == "horas":
                                edad_dict["horas"] = cantidad
                        antecedentes_personales_secciones["edad"] = edad_dict
                    except (IndexError, ValueError):
                        antecedentes_personales_secciones["edad"] = {"años": None}

                isEdad = True

            for keyword in antecedentes_personales_keywords:
                if keyword in linea:

                    # Si la keyword es "tabaquismo" o "tabaco" o "índice tabáquico" y si tiene o no ":" que separan
                    if keyword == "tabaquismo" or keyword == "tabaco" or keyword == "índice tabáquico":
                        # Removemos los ":" si están presentes
                        if ":" in linea:
                            linea = linea.replace(":", "")

                        # Extraemos el estado del tabaquismo y cualquier unidad de tiempo
                        estados = ["negado", "suspendido", "fumador"]
                        for estado in estados:
                            if estado in linea:
                                antecedentes_personales_secciones["índice_tabáquico"]["fuma"] = estado
                                # Verificamos si hay algo más en la línea
                                if len(linea.split(estado)[1].strip()) > 0:
                                    notas = linea.split(estado)[1].strip()
                                    observaciones = notas.split(". ")
                                    observaciones_list = []
                                    for observacion in observaciones:
                                        unidades = self.__extract_units(observacion)
                                        if unidades:
                                            exposicion = {"notas": observacion, "tiempo": {}}
                                            for cantidad, unidad in unidades:
                                                if unidad == "años":
                                                    exposicion["tiempo"]["años"] = cantidad
                                                elif unidad == "meses":
                                                    exposicion["tiempo"]["meses"] = cantidad
                                                elif unidad == "días":
                                                    exposicion["tiempo"]["días"] = cantidad
                                                elif unidad == "horas":
                                                    exposicion["tiempo"]["horas"] = cantidad
                                            observaciones_list.append(exposicion)

                                    if observaciones_list:
                                        antecedentes_personales_secciones["índice_tabáquico"]["observaciones"] = observaciones_list
                                    else:
                                        antecedentes_personales_secciones["índice_tabáquico"]["observaciones"] = None
                                break

                    elif keyword in ["fum", "menarca", "trh", "aco", "mpf", "estado hormonal", "métodos anticonceptivos", "embarazos", "partos"]:
                        # Patrón para identificar claves ginecológicas en la línea
                        pattern = re.compile(r'\b(fum|menarca|trh|mpf|aco|estado hormonal|métodos anticonceptivos|embarazos|partos)\b', re.IGNORECASE)
                        pattern_especial = re.match(r"menarca a los (\d+) años\. (\d+) embarazos?, (\d+) partos?", linea, re.IGNORECASE)

                        if pattern_especial:
                            print("patron especial")
                            edad_menarca, num_embarazos, num_partos = map(int, pattern_especial.groups())
                            antecedentes_personales_secciones["antecedentes_ginecológicos"]["menarca"] = {"años": edad_menarca}
                            antecedentes_personales_secciones["antecedentes_ginecológicos"]["embarazos"] = num_embarazos
                            antecedentes_personales_secciones["antecedentes_ginecológicos"]["partos"] = num_partos
                        else:
                            # Eliminar guiones y limpiar la línea
                            linea_limpia = re.sub(r'^-\s*', '', linea.strip())
                            matches = pattern.findall(linea)
                            
                            if len(matches) > 1:
                                # Separar por "/", ",", "y"
                                partes = re.split(r'\s*[\/,]\s*|\s+y\s+', linea_limpia)
                                valores = {}
                                
                                for parte in partes:
                                    parte = parte.strip()
                                    for keyword in matches:
                                        if keyword in parte:
                                            valor = None
                                            if ":" in parte:
                                                valor = parte.split(":")[1].strip()
                                            else:
                                                valor = parte.replace(keyword, "").strip()

                                            # Verificar si el valor está vacío y hay más claves
                                            if not valor and len(matches) > 1:
                                                valor = partes[-1].strip()

                                            unidades = self.__extract_units(valor)
                                            if unidades:
                                                valor_dict = {unidad: cantidad for cantidad, unidad in unidades}
                                                if len(valor.split()) > 2:
                                                    valor_dict["contexto"] = valor
                                                valores[keyword.strip().replace(" ", "_")] = valor_dict
                                            else:
                                                valores[keyword.strip().replace(" ", "_")] = valor
                                
                                # Caso especial: múltiples claves comparten el mismo valor
                                if any(separador in linea_limpia for separador in [" y ", "/", ","]):
                                    #imprimimos la linea que cae en este caso
                                    ultima_clave = matches[-1]
                                    valor_comun = linea_limpia.split(ultima_clave)[1].strip() if ":" not in linea_limpia else linea_limpia.split(":")[1].strip()
                                    for keyword in matches:
                                        if keyword not in valores:
                                            valores[keyword.strip().replace(" ", "_")] = valor_comun
                                
                                antecedentes_personales_secciones["antecedentes_ginecológicos"].update(valores)
                            else:
                                if matches:
                                    keyword = matches[0]
                                    valor = None
                                    if ":" in linea_limpia:
                                        valor = linea_limpia.split(":")[1].strip()
                                    else:
                                        valor = linea_limpia.split(keyword)[1].strip()

                                    unidades = self.__extract_units(valor)
                                    if unidades:
                                        valor_dict = {unidad: cantidad for cantidad, unidad in unidades}
                                        if len(valor.split()) > 2:
                                            valor_dict["contexto"] = valor
                                        antecedentes_personales_secciones["antecedentes_ginecológicos"][keyword.strip().replace(" ", "_")] = valor_dict
                                    else:
                                        antecedentes_personales_secciones["antecedentes_ginecológicos"][keyword.strip().replace(" ", "_")] = valor

                    # elif keyword in ["fum", "menarca", "trh", "aco", "mpf", "estado hormonal", "métodos anticonceptivos", "embarazos", "partos"]:
                    #     # Patrón para identificar claves ginecológicas en la línea
                    #     pattern = re.compile(r'\b(fum|menarca|trh|mpf|aco|estado hormonal|métodos anticonceptivos|embarazos|partos)\b', re.IGNORECASE)
                        
                    #     # Eliminar guiones y limpiar la línea
                    #     linea_limpia = re.sub(r'^-\s*', '', linea.strip())
                    #     matches = pattern.findall(linea_limpia)
                        
                    #     if len(matches) > 1:
                    #         # Separar por ".", "/", ",", " y "
                    #         partes = re.split(r'\s*[\./,]\s*|\s+y\s+', linea_limpia)
                    #         valores = {}
                            
                    #         for parte in partes:
                    #             parte = parte.strip()
                    #             for keyword in matches:
                    #                 if keyword in parte:
                    #                     valor = None
                    #                     if ":" in parte:
                    #                         valor = parte.split(":")[1].strip()
                    #                     else:
                    #                         valor = parte.replace(keyword, "").strip()
                                        
                    #                     # Verificar si el valor está vacío y hay más claves
                    #                     if not valor and len(matches) > 1:
                    #                         valor = parte.strip()
                                        
                    #                     unidades = self.__extract_units(valor)
                    #                     if unidades:
                    #                         valor_dict = {unidad: cantidad for cantidad, unidad in unidades}
                    #                         if len(valor.split()) > 2:
                    #                             valor_dict["contexto"] = valor
                    #                         valores[keyword.strip().replace(" ", "_")] = valor_dict
                    #                     else:
                    #                         valores[keyword.strip().replace(" ", "_")] = valor
                            
                    #         antecedentes_personales_secciones["antecedentes_ginecológicos"].update(valores)
                    #     else:
                    #         if matches:
                    #             keyword = matches[0]
                    #             valor = None
                    #             if ":" in linea_limpia:
                    #                 valor = linea_limpia.split(":")[1].strip()
                    #             else:
                    #                 valor = linea_limpia.split(keyword)[1].strip()
                                
                    #             unidades = self.__extract_units(valor)
                    #             if unidades:
                    #                 valor_dict = {unidad: cantidad for cantidad, unidad in unidades}
                    #                 if len(valor.split()) > 2:
                    #                     valor_dict["contexto"] = valor
                    #                 antecedentes_personales_secciones["antecedentes_ginecológicos"][keyword.strip().replace(" ", "_")] = valor_dict
                    #             else:
                    #                 antecedentes_personales_secciones["antecedentes_ginecológicos"][keyword.strip().replace(" ", "_")] = valor

                   

                    elif keyword == "comorbilidades":
                        comorbilidades = linea
                        comorbilidades = comorbilidades.replace("comorbilidades:", "").strip()
                        
                        # Verificar si está negado
                        if "negad" in comorbilidades:
                            antecedentes_personales_secciones["comorbilidades"] = "negadas"
                            continue
                        
                        # Dividir la cadena en comorbilidades individuales
                        comorbilidades_list = re.split(r'\d+\.\s', comorbilidades)

                        # Eliminar posibles cadenas vacías resultantes de la división
                        comorbilidades_list = [comorbilidad for comorbilidad in comorbilidades_list if comorbilidad]

                        comorbilidades_dict = {}

                        # Inicializar el campo "sin_fecha"
                        comorbilidades_dict["sin_fecha"] = []

                        for comorbilidad in comorbilidades_list:
                            comorbilidad = comorbilidad.strip()
                            # Extraer el año, que puede estar en formato (YYYY) o (MM.YYYY)
                            match = re.search(r'\((\d{4}|\d{2}\.\d{4})\)', comorbilidad)
                            if match:
                                year = match.group(1)
                                # Separar nombre y descripción
                                parts = comorbilidad.split(f"({year})")
                                nombre = parts[0].strip()
                                descripcion = parts[1].strip() if len(parts) > 1 else ""

                                # Si la descripción es solo un punto, lo agregamos al nombre
                                if descripcion == ".":
                                    descripcion = None  # Dejamos la descripción vacía
                                    nombre = nombre.rstrip('.')  # Quitamos el punto del nombre

                                if year not in comorbilidades_dict:
                                    comorbilidades_dict[year] = []

                                comorbilidades_dict[year].append({
                                    "nombre": nombre.strip(),
                                    "descripción": descripcion.lstrip(': ') if descripcion else None
                                })
                            else:
                                # Si no hay fecha, agregar a "sin_fecha"
                                comorbilidades_dict["sin_fecha"].append({
                                    "nombre": comorbilidad.strip(),
                                    "descripción": None  # No hay descripción si no hay fecha
                                })
                        
                        #si no hay comorbilidades sin fecha, eliminar el campo
                        if not comorbilidades_dict["sin_fecha"]:
                            del comorbilidades_dict["sin_fecha"]
                        antecedentes_personales_secciones["comorbilidades"] = comorbilidades_dict

                    else:
                        if keyword == "edad" and isEdad == True:
                            continue
                        elif re.match(r'^\d+\.|\(\d{4}\)', linea):  # Evitar claves en listas numeradas o con fechas
                            continue
                        elif ":" in linea:
                            antecedentes_personales_secciones[keyword.replace(" ", "_")] = linea.split(":")[1].strip()
                        else:
                            antecedentes_personales_secciones[keyword.replace(" ", "_")] = linea.split(keyword)[1].strip()

        self.data["antecedentes_personales"] = antecedentes_personales_secciones
        #self.imprimir_json()

    def __extraer_datos_antecedentes_familiares(self):
        """
        Extrae y estructura los datos de antecedentes familiares del texto procesado.

        Los datos se almacenan en el diccionario `data` bajo la clave "antecedentes_familiares".
        """
        antecedentes_familiares_secciones = {
            "ascendencia": None,
            "lateralidad": None,
            "descendencia": None,
        }

        for linea in self.informacion:
            linea = linea.strip().lower()

            # Verificar si está negado
            if "ahf" in linea and "negado" in linea:
                self.data["antecedentes_familiares"] = {
                    "ascendencia": "negado",
                    "lateralidad": "negado",
                    "descendencia": "negado"
                }
                return

            if "ahf" in linea:
                # Remover la parte inicial "AHF oncológicos:" si está presente
                if ":" in linea:
                    linea = linea.split(":", 1)[1].strip()

                # Inicializar listas para cada categoría
                ascendencia = []
                lateralidad = []
                descendencia = []

                # Separar la línea en partes basadas en "/", "-", ",", o ";"
                partes = re.split(r'[\/\-;,.]', linea)

                # for parte in partes:
                #     parte = parte.strip()
                #     # Verificar si la parte contiene alguna relación familiar al inicio
                #     if any(parte.startswith(rel) for rel in ["primo", "tío", "prima", "tía", "hermano", "hermana"]):
                #         lateralidad.append(parte)
                #     elif any(parte.startswith(rel) for rel in ["padre", "madre", "abuelo", "abuela", "papá", "mamá"]):
                #         ascendencia.append(parte)
                #     elif any(parte.startswith(rel) for rel in ["hija", "hijo", "nieto", "nieta"]):
                #         descendencia.append(parte)
                for parte in partes:
                    parte = parte.strip()
                    # Verificar si la parte contiene alguna relación familiar
                    if any(rel in parte for rel in ["primo", "tío", "prima", "tía", "hermano", "hermana"]):
                        lateralidad.append(parte)
                    elif any(rel in parte for rel in ["padre", "madre", "abuelo", "abuela", "papá", "mamá"]):
                        ascendencia.append(parte)
                    elif any(rel in parte for rel in ["hija", "hijo", "nieto", "nieta"]):
                        descendencia.append(parte)

                # Asignar las listas a las secciones correspondientes
                antecedentes_familiares_secciones["ascendencia"] = ascendencia if ascendencia else None
                antecedentes_familiares_secciones["lateralidad"] = lateralidad if lateralidad else None
                antecedentes_familiares_secciones["descendencia"] = descendencia if descendencia else None

        self.data["antecedentes_familiares"] = antecedentes_familiares_secciones
        # self.imprimir_json()

    def __extraer_datos_inmunohistoquuímica_tumoral(self):
        """
        Extrae y estructura los datos de inmunohistoquímica tumoral del texto procesado.

        Los datos se almacenan en el diccionario `data` bajo la clave "inmunohistoquímica_tumoral".
        """
        # Secciones de inmunohistoquímica tumoral
        inmunohistoquímica_tumoral_secciones = {
            "mama_izquierda": {
                "re": None,
                "rp": None,
                "her2": None,
                "ki67": None,
                "gh": None
            },
            "mama_derecha": {
                "re": None,
                "rp": None,
                "her2": None,
                "ki67": None,
                "gh": None
            }
        }

        for linea in self.informacion:
            linea = linea.strip()

            # Extraer biología tumoral
            if "biología tumoral" in linea.lower():
                try:
                    if self.mama == "mama_izquierda":
                        # RE
                        inmunohistoquímica_tumoral_secciones["mama_izquierda"]["re"] = re.search(r"re (\d+%)", linea).group(1) if re.search(r"re (\d+%)", linea) else None
                        # RP
                        inmunohistoquímica_tumoral_secciones["mama_izquierda"]["rp"] = re.search(r"rp (\d+%)", linea).group(1) if re.search(r"rp (\d+%)", linea) else None
                        # HER2
                        her2_match = re.search(r"her2\s*([^,]+)", linea, re.IGNORECASE)
                        inmunohistoquímica_tumoral_secciones["mama_izquierda"]["her2"] = her2_match.group(1).lower() if her2_match else None
                        # KI67
                        ki67_match = re.search(r"ki67 (\d+%)|ki67 (\w+)", linea)
                        inmunohistoquímica_tumoral_secciones["mama_izquierda"]["ki67"] = ki67_match.group(1) if ki67_match and ki67_match.group(1) else (ki67_match.group(2) if ki67_match and ki67_match.group(2) else None)
                        # GH
                        inmunohistoquímica_tumoral_secciones["mama_izquierda"]["gh"] = re.search(r"g\d", linea).group(0) if re.search(r"g\d", linea) else None

                    elif self.mama == "mama_derecha":
                        # RE
                        inmunohistoquímica_tumoral_secciones["mama_derecha"]["re"] = re.search(r"re (\d+%)", linea).group(1) if re.search(r"re (\d+%)", linea) else None
                        # RP
                        inmunohistoquímica_tumoral_secciones["mama_derecha"]["rp"] = re.search(r"rp (\d+%)", linea).group(1) if re.search(r"rp (\d+%)", linea) else None
                        # HER2
                        her2_match = re.search(r"her2\s*([^,]+)", linea, re.IGNORECASE)
                        inmunohistoquímica_tumoral_secciones["mama_derecha"]["her2"] = her2_match.group(1).lower() if her2_match else None
                        # KI67
                        ki67_match = re.search(r"ki67 (\d+%)|ki67 (\w+)", linea)
                        inmunohistoquímica_tumoral_secciones["mama_derecha"]["ki67"] = ki67_match.group(1) if ki67_match and ki67_match.group(1) else (ki67_match.group(2) if ki67_match and ki67_match.group(2) else None)
                        # GH
                        inmunohistoquímica_tumoral_secciones["mama_derecha"]["gh"] = re.search(r"g\d", linea).group(0) if re.search(r"g\d", linea) else None

                    elif self.mama == "bilateral":
                        # Patrón para capturar "mama izquierda" y "mama derecha"
                        match1 = re.search(r"mama izquierda:(.+?)mama derecha:(.+)", linea, re.IGNORECASE | re.DOTALL)
                        if match1:
                            izquierda = match1.group(1).strip()
                            derecha = match1.group(2).strip()

                            # Extraer datos específicos de cada mama
                            for mama, texto in [("mama_izquierda", izquierda), ("mama_derecha", derecha)]:
                                # RE
                                inmunohistoquímica_tumoral_secciones[mama]["re"] = re.search(r"re (\d+%)", texto).group(1) if re.search(r"re (\d+%)", texto) else None
                                # RP
                                inmunohistoquímica_tumoral_secciones[mama]["rp"] = re.search(r"rp (\d+%)", texto).group(1) if re.search(r"rp (\d+%)", texto) else None
                                # HER2
                                her2_match = re.search(r"her2\s*([^,]+)", linea, re.IGNORECASE)
                                inmunohistoquímica_tumoral_secciones[mama]["her2"] = her2_match.group(1).lower() if her2_match else None
                                # KI67
                                ki67_match = re.search(r"ki67 (\d+%)|ki67 (\w+)", texto)
                                inmunohistoquímica_tumoral_secciones[mama]["ki67"] = ki67_match.group(1) if ki67_match and ki67_match.group(1) else (ki67_match.group(2) if ki67_match and ki67_match.group(2) else None)
                                # GH
                                inmunohistoquímica_tumoral_secciones[mama]["gh"] = re.search(r"g\d", texto).group(0) if re.search(r"g\d", texto) else None

                except Exception as e:
                    print(f"Error al procesar la línea: '{linea}'. Error: {e}")
                    # Si ocurre un error, se asegura que al menos los campos que no causaron el error se llenen con None
                    if self.mama == "mama_izquierda":
                        inmunohistoquímica_tumoral_secciones["mama_izquierda"] = {key: None for key in ["re", "rp", "her2", "ki67", "gh"]}
                    elif self.mama == "mama_derecha":
                        inmunohistoquímica_tumoral_secciones["mama_derecha"] = {key: None for key in ["re", "rp", "her2", "ki67", "gh"]}
                    elif self.mama == "bilateral":
                        inmunohistoquímica_tumoral_secciones["mama_izquierda"] = {key: None for key in ["re", "rp", "her2", "ki67", "gh"]}
                        inmunohistoquímica_tumoral_secciones["mama_derecha"] = {key: None for key in ["re", "rp", "her2", "ki67", "gh"]}

            self.data["inmunohistoquímica_tumoral"] = inmunohistoquímica_tumoral_secciones

        # self.imprimir_data()

    def __extraer_datos_clasificacion(self):
        """
        Extrae y estructura los datos de clasificación del cáncer del texto procesado.

        Los datos se almacenan en el diccionario `data` bajo la clave "tipo".
        """
        clasificacion = {
            "mama_izquierda": {"clasificación": None, "descripcion": None},
            "mama_derecha": {"clasificación": None, "descripcion": None},
        }

        for linea in self.informacion:
            linea = linea.strip()

            # Buscar clasificación del cáncer
            if linea.startswith("diagnóstico"):
                # Quitar "Cáncer de mama bilateral." si está al inicio
                linea = re.sub(r"^cáncer de mama bilateral\.?", "", linea).strip()

                # Verificar si hay una barra "/" que indica ambas mamas
                if "/" in linea:
                    partes = linea.split("/")
                    for parte in partes:
                        parte = parte.strip()

                        # Extraer correctamente cada mama
                        if re.search(r"\bmi\b|\bmama izquierda\b", parte, re.IGNORECASE):
                            clasificacion["mama_izquierda"]["clasificación"] = parte.replace("diagnóstico: ", "").strip()
                        if re.search(r"\bmd\b|\bmama derecha\b", parte, re.IGNORECASE):
                            clasificacion["mama_derecha"]["clasificación"] = parte.replace("diagnóstico: ", "").strip()

                else:
                    # Buscar clasificación individual con más flexibilidad
                    match_izq = re.search(r"(?:diagnóstico:\s*)?(.*?)(?:\bmi\b|\bmama izquierda\b)\s*(.+)", linea, re.IGNORECASE)
                    match_der = re.search(r"(?:diagnóstico:\s*)?(.*?)(?:\bmd\b|\bmama derecha\b)\s*(.+)", linea, re.IGNORECASE)

                    if match_izq:
                        clasificacion["mama_izquierda"]["clasificación"] = f"{match_izq.group(1).strip()} {match_izq.group(2).strip()}".strip()
                    if match_der:
                        clasificacion["mama_derecha"]["clasificación"] = f"{match_der.group(1).strip()} {match_der.group(2).strip()}".strip()
                    else:
                        # Si no se encuentra ninguna coincidencia, guiarse por el atributo self.mama
                        if self.mama == "mama_izquierda":
                            clasificacion["mama_izquierda"]["clasificación"] = linea.replace("diagnóstico: ", "").strip()
                        elif self.mama == "mama_derecha":
                            clasificacion["mama_derecha"]["clasificación"] = linea.replace("diagnóstico: ", "").strip()

            # Buscar descripción de la extensión del tumor
            # if "extensión del tumor" in linea:
            #     match_izq = re.search(r"mama izquierda ([^\(]+) \(([^)]+)\)", linea) 
            #     match_der = re.search(r"mama derecha ([^\(]+) \(([^)]+)\)", linea)
            #     if match_izq:
            #         clasificacion["mama_izquierda"]["descripcion"] = f"{match_izq.group(1).strip()} ({match_izq.group(2).strip()})"
            #     if match_der:
            #         clasificacion["mama_derecha"]["descripcion"] = f"{match_der.group(1).strip()} ({match_der.group(2).strip()})"
            if "extensión del tumor" in linea:
                # Buscar mama izquierda
                match_izq = re.search(r"mama izquierda\s+([^\(]+)(?:\s*\(.*\))?", linea, re.IGNORECASE)
                # Buscar mama derecha
                match_der = re.search(r"mama derecha\s+([^\(]+)(?:\s*\(.*\))?", linea, re.IGNORECASE)
                
                if match_izq:
                    clasificacion["mama_izquierda"]["descripcion"] = f"{match_izq.group(1).strip()}"
                if match_der:
                    clasificacion["mama_derecha"]["descripcion"] = f"{match_der.group(1).strip()}"

        self.data["tipo"] = clasificacion
        # self.imprimir_data()

    def __extraer_datos_estadia_tumoral(self):
        """
        Extrae y estructura los datos de estadía tumoral del texto procesado.

        Los datos se almacenan en el diccionario `data` bajo la clave "estadía_tumoral".

        Los datos a extraer suelen estar dentro de este tipo de secciones:
        - Extensión del tumor: Mama izquierda EC IIA (pT1c, pN1a, MO)
        - Extensión del tumor: Mama derecha EC IIA (pT2, NO, MO)
        - Extensión del tumor: cdi de mama izquierda ec iia ct2 -3.5 cm cn0
        """
        estadia_tumoral_secciones = {
            "mama_izquierda": {
                "ultrasonido": None,
                "mastografía": None,
                "centros_tumorales": None,
                "nódulos": None,
                "metástasis": None,
            },
            "mama_derecha": {
                "ultrasonido": None,
                "mastografía": None,
                "centros_tumorales": None,
                "nódulos": None,
                "metástasis": None,
            }
        }

        for linea in self.informacion:
            linea = linea.strip()

            # Extraer datos de la extensión del tumor
            if "extensión del tumor" in linea.lower():
                # Buscar si hay información para ambas mamas o solo una
                if self.mama == "bilateral":
                    try:
                        secciones = re.split(r"mama (izquierda|derecha)", linea, flags=re.IGNORECASE)
                        seccion_izquierda = secciones[2].strip()
                        seccion_derecha = secciones[4].strip()

                        # Expresión regular mejorada para capturar campos con guiones o caracteres especiales
                        campos_izquierda = re.findall(r"(pt\d+\w*|ct\d+\w*|pn\d+\w*|n\d+\w*|cn\d+\w*|m\d+\w*)", seccion_izquierda, re.IGNORECASE)
                        for campo in campos_izquierda:
                            if campo.startswith("pt") or campo.startswith("ct"):
                                estadia_tumoral_secciones["mama_izquierda"]["centros_tumorales"] = campo
                            elif campo.startswith("pn") or campo.startswith("n") or campo.startswith("cn"):
                                estadia_tumoral_secciones["mama_izquierda"]["nódulos"] = campo
                            elif campo.startswith("m"):
                                estadia_tumoral_secciones["mama_izquierda"]["metástasis"] = campo

                        campos_derecha = re.findall(r"(pt\d+\w*|ct\d+\w*|pn\d+\w*|n\d+\w*|cn\d+\w*|m\d+\w*)", seccion_derecha, re.IGNORECASE)
                        for campo in campos_derecha:
                            if campo.startswith("pt") or campo.startswith("ct"):
                                estadia_tumoral_secciones["mama_derecha"]["centros_tumorales"] = campo
                            elif campo.startswith("pn") or campo.startswith("n") or campo.startswith("cn"):
                                estadia_tumoral_secciones["mama_derecha"]["nódulos"] = campo
                            elif campo.startswith("m"):
                                estadia_tumoral_secciones["mama_derecha"]["metástasis"] = campo
                    except IndexError:
                        print("Error al procesar datos de mama bilateral. Verifique el formato del texto.")
                        # Extraer datos en base a "mama izquierda" o "mama derecha" si el try falla
                        if "mama izquierda" in linea.lower():
                            campos_izquierda = re.findall(r"(pt\d+\w*|ct\d+\w*|pn\d+\w*|n\d+\w*|cn\d+\w*|m\d+\w*)", linea, re.IGNORECASE)
                            for campo in campos_izquierda:
                                if campo.startswith("pt") or campo.startswith("ct"):
                                    estadia_tumoral_secciones["mama_izquierda"]["centros_tumorales"] = campo
                                elif campo.startswith("pn") or campo.startswith("n") or campo.startswith("cn"):
                                    estadia_tumoral_secciones["mama_izquierda"]["nódulos"] = campo
                                elif campo.startswith("m"):
                                    estadia_tumoral_secciones["mama_izquierda"]["metástasis"] = campo

                        if "mama derecha" in linea.lower():
                            campos_derecha = re.findall(r"(pt\d+\w*|ct\d+\w*|pn\d+\w*|n\d+\w*|cn\d+\w*|m\d+\w*)", linea, re.IGNORECASE)
                            for campo in campos_derecha:
                                if campo.startswith("pt") or campo.startswith("ct"):
                                    estadia_tumoral_secciones["mama_derecha"]["centros_tumorales"] = campo
                                elif campo.startswith("pn") or campo.startswith("n") or campo.startswith("cn"):
                                    estadia_tumoral_secciones["mama_derecha"]["nódulos"] = campo
                                elif campo.startswith("m"):
                                    estadia_tumoral_secciones["mama_derecha"]["metástasis"] = campo

                elif self.mama == "mama_izquierda":
                    # Expresión regular mejorada para capturar campos con guiones o caracteres especiales
                    campos = re.findall(r"(pt\d+\w*|ct\d+\w*|pn\d+\w*|n\d+\w*|cn\d+\w*|m\d+\w*)", linea, re.IGNORECASE)
                    for campo in campos:
                        if campo.startswith("pt") or campo.startswith("ct"):
                            estadia_tumoral_secciones["mama_izquierda"]["centros_tumorales"] = campo
                        elif campo.startswith("pn") or campo.startswith("n") or campo.startswith("cn"):
                            estadia_tumoral_secciones["mama_izquierda"]["nódulos"] = campo
                        elif campo.startswith("m"):
                            estadia_tumoral_secciones["mama_izquierda"]["metástasis"] = campo

                elif self.mama == "mama_derecha":
                    # Expresión regular mejorada para capturar campos con guiones o caracteres especiales
                    campos = re.findall(r"(pt\d+\w*|ct\d+\w*|pn\d+\w*|n\d+\w*|cn\d+\w*|m\d+\w*)", linea, re.IGNORECASE)
                    for campo in campos:
                        if campo.startswith("pt") or campo.startswith("ct"):
                            estadia_tumoral_secciones["mama_derecha"]["centros_tumorales"] = campo
                        elif campo.startswith("pn") or campo.startswith("n") or campo.startswith("cn"):
                            estadia_tumoral_secciones["mama_derecha"]["nódulos"] = campo
                        elif campo.startswith("m"):
                            estadia_tumoral_secciones["mama_derecha"]["metástasis"] = campo

        self.data["estadía_tumoral"] = estadia_tumoral_secciones

    def convertir_txt_json(self, ruta_txt, ruta_destino):
        """
        Convierte un archivo de texto a un archivo JSON sin importar la cantidad de casos que contenga el txt.
        Crea tantos JSON como casos haya en el archivo de texto.
        Crea la carpeta de destino si no existe.

        Args:
            ruta_txt (str): Ruta del archivo de texto que se convertirá a JSON.
            ruta_destino (str): Ruta de la carpeta donde se guardarán los archivos
        """
        self.setrutaTxt(ruta_txt)
        self.setrutaDestino(ruta_destino)
        nombreJSON = self.__extraer_nombre_txt().replace(".txt", ".json")

        os.makedirs(ruta_destino, exist_ok=True) # Crear la carpeta de destino si no existe

        self.__limpiar_texto()
        self.imprimir_info()

        self.__detector_pezones()

        self.__extraer_datos_antecedentes_personales()
        self.__extraer_datos_antecedentes_familiares()
        self.__extraer_datos_inmunohistoquuímica_tumoral()
        self.__extraer_datos_clasificacion()
        self.__extraer_datos_estadia_tumoral()

        self.__crear_json(nombreJSON)
        
        self.__limpiar_instancia()

    def __limpiar_instancia(self):
        """
        Limpia el atributo "data" para evitar que se mezclen los datos de diferentes casos.
        """
        self.rutaTxt = None
        self.rutaDestino = None
        self.mama = None
        self.informacion = []
        self.data = {
            "antecedentes_personales": {},
            "antecedentes_familiares": {},
            "estadia_tumoral": {},
            "inmunohistoquímica_tumoral": {},
            "tipo": {},
        }

    def imprimir_info(self):
        """
        Imprime las lineas que contenga el atributo "Información".
        """
        for linea in self.informacion:
            print(linea)

    def imprimir_json(self):
        """
        Imprime el atributo "data" en formato JSON.
        """
        print(json.dumps(self.informacion, indent=4, ensure_ascii=False))

    def __crear_json(self, nombreJSON):
        """
        Crea un archivo JSON con el atributo "data" que es un diccionario.

        Args:
            destino (str): Ruta del archivo JSON que se creará.
        """

        with open(os.path.join(self.rutaDestino, nombreJSON), 'w', encoding="utf-8") as file:
            json.dump(self.data, file, indent=4, ensure_ascii=False)
