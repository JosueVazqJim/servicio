import json
import re
import os
from .limpiador_texto import LimpiezaTexto

class TextoJson:
    """
    Clase para procesar y estructurar texto médico en un formato JSON.

    Esta clase toma un archivo de texto con información médica, la procesa y la estructura
    en un formato JSON que incluye secciones como antecedentes personales, antecedentes familiares,
    estadia tumoral, inmunohistoquímica tumoral, y tipo de cáncer.
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
            "estadia_tumoral": {},
            "inmunohistoquímica_tumoral": {},
            "tipo": {},
        }

    def setrutaTxt(self, rutaTxt):
        self.rutaTxt = rutaTxt

    def setrutaDestino(self, rutaDestino):
        self.rutaDestino = rutaDestino

    def __limpiar_texto(self):
        """
        Limpia el texto de entrada utilizando la instancia de LimpiezaTexto.
        """
        self.informacion = self.limpiador.limpiar_archivo(self.rutaTxt)

    def __extraer_nombre_txt(self):
        """
        Extrae el nombre del archivo de texto de la ruta de archivo.
        devuelve el nombre del archivo de texto
        """
        return os.path.basename(self.rutaTxt)

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
        print("ruta_txt: ", ruta_txt)
        print("ruta_destino: ", ruta_destino)
        nombreJSON = self.__extraer_nombre_txt().replace(".txt", ".json")

        os.makedirs(ruta_destino, exist_ok=True)

        self.__limpiar_texto()

        self.__extraer_datos_antecedentes_personales()
        self.__extraer_datos_antecedentes_familiares()
        self.__extraer_datos_inmunohistoquuímica_tumoral()
        self.__extraer_datos_clasificacion()
        self.__extraer_datos_estadia_tumoral()
        self.__crear_json(ruta_destino + "\\" + nombreJSON)
        self.__limpiar_data()
        self.__limpiar_instancia()

    def __limpiar_instancia(self):
        """
        Limpia el atributo "data" para evitar que se mezclen los datos de diferentes casos.
        """
        self.rutaTxt = None
        self.rutaDestino = None
        self.informacion = []
        self.data = {
            "antecedentes_personales": {},
            "antecedentes_familiares": {},
            "estadia_tumoral": {},
            "inmunohistoquímica_tumoral": {},
            "tipo": {},
        }

    def __limpiar_data(self):
        """
        Limpia el atributo "data" para evitar que se mezclen los datos de diferentes casos.
        """
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

    def __crear_json(self, destino):
        """
        Crea un archivo JSON con el atributo "data" que es un diccionario.

        Args:
            destino (str): Ruta del archivo JSON que se creará.
        """

        with open(destino, 'w', encoding="utf-8") as file:
            json.dump(self.data, file, indent=4, ensure_ascii=False)

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
                "estado_hormonal": None,
                "métodos_anticonceptivos": None
            }
        }

        #palaras clave para antecedentes_personales que buscaremos en el texto
        antecedentes_personales_keywords = [
            "edad", "sexo", "peso", "talla", "preferencia",
            "índice tabáquico", "tabaco", "tabaquismo", "alcohol", "drogas",
            "comorbilidades", "antecedentes ginecológicos", "menarca", "embarazos", "partos", "fum", "trh",
            "estado hormonal", "métodos anticonceptivos"
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
                        # Removemos los ":"
                        if ":" in linea:
                            linea = linea.replace(":", "")

                        # Extraemos lo que sea diferente a "negado" y guardamos el resto en una variable
                        if "negado" in linea:
                            antecedentes_personales_secciones["índice_tabáquico"]["fuma"] = "negado"
                            # Verificamos si hay algo más en la línea
                            if len(linea.split("negado")[1].strip()) > 0:
                                notas = linea.split("negado")[1].strip()
                                observaciones = notas.split(". ")
                                observaciones_list = []
                                for observacion in observaciones:
                                    unidades = self.__extract_units(observacion)
                                    if unidades:
                                        exposicion = {"tipo": observacion, "tiempo": {}}
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

                    elif keyword in ["fum", "menarca", "trh", "estado hormonal", "métodos anticonceptivos", "embarazos", "partos"]:
                        # Verificar las keywords de antecedentes ginecológicos en la misma línea
                        pattern = re.compile(r'(fum|menarca|trh|estado hormonal|métodos anticonceptivos|embarazos|partos)', re.IGNORECASE)
                        matches = pattern.findall(linea)
                        if len(matches) > 1:
                            # Dividir la línea en partes basadas en varios separadores posibles
                            partes = re.split(r'[\/,\.]', linea)
                            for parte in partes:
                                # Asegurarte de que cada elemento sea una cadena válida
                                if isinstance(parte, str):  # Por seguridad, verifica si el elemento es una cadena
                                    parte = parte.strip()  # Elimina espacios al inicio y al final

                                for keyword in matches:
                                    if keyword in parte:
                                        valor = None
                                        if ":" in parte:
                                            valor = parte.split(":")[1].strip()
                                        else:
                                            # Verificar si el valor precede a la clave
                                            if parte.strip().startswith(keyword):
                                                valor = parte.split(keyword)[1].strip()
                                            else:
                                                valor = parte.split(keyword)[0].strip()

                                        # Usar __extract_units para procesar el valor
                                        try:
                                            unidades = self.__extract_units(valor)
                                            if unidades:
                                                valor_dict = {}
                                                for cantidad, unidad in unidades:
                                                    if unidad == "años":
                                                        valor_dict["años"] = cantidad
                                                    elif unidad == "meses":
                                                        valor_dict["meses"] = cantidad
                                                    elif unidad == "días":
                                                        valor_dict["días"] = cantidad
                                                    elif unidad == "horas":
                                                        valor_dict["horas"] = cantidad
                                                antecedentes_personales_secciones["antecedentes_ginecológicos"][keyword.strip().replace(" ", "_")] = valor_dict
                                            else:
                                                antecedentes_personales_secciones["antecedentes_ginecológicos"][keyword.strip().replace(" ", "_")] = int(valor)
                                        except (IndexError, ValueError):
                                            antecedentes_personales_secciones["antecedentes_ginecológicos"][keyword.strip().replace(" ", "_")] = valor
                        else:
                            # Procesar la línea si solo hay una coincidencia
                            keyword = matches[0]
                            valor = None
                            if ":" in linea:
                                valor = linea.split(":")[1].strip()
                            else:
                                valor = linea.split(keyword)[1].strip()

                            # Usar __extract_units para procesar el valor
                            try:
                                unidades = self.__extract_units(valor)
                                if unidades:
                                    valor_dict = {}
                                    for cantidad, unidad in unidades:
                                        if unidad == "años":
                                            valor_dict["años"] = cantidad
                                        elif unidad == "meses":
                                            valor_dict["meses"] = cantidad
                                        elif unidad == "días":
                                            valor_dict["días"] = cantidad
                                        elif unidad == "horas":
                                            valor_dict["horas"] = cantidad
                                    antecedentes_personales_secciones["antecedentes_ginecológicos"][keyword.strip().replace(" ", "_")] = valor_dict
                                else:
                                    antecedentes_personales_secciones["antecedentes_ginecológicos"][keyword.strip().replace(" ", "_")] = valor
                            except (IndexError, ValueError):
                                antecedentes_personales_secciones["antecedentes_ginecológicos"][keyword.strip().replace(" ", "_")] = valor

                    ##tratamos las comoorbilidades dado que es una linea con varias comorbilidades separadas por "/"
                    elif keyword == "comorbilidades":
                        comorbilidades = linea
                        # Dividir la cadena en comorbilidades individuales
                        comorbilidades_list = re.split(r'\d+\.\s', comorbilidades)

                        # Eliminar posibles cadenas vacías resultantes de la división
                        comorbilidades_list = [comorbilidad for comorbilidad in comorbilidades_list if comorbilidad]

                        comorbilidades_dict = {}

                        for comorbilidad in comorbilidades_list:
                            comorbilidad = comorbilidad.strip()
                            # Extraer el año
                            match = re.search(r'\((\d{4})\)', comorbilidad)
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
                                    "nombre": nombre.replace("comorbilidades: ", "").strip(),
                                    "descripción": descripcion.lstrip(': ') if descripcion else None
                                })
                        antecedentes_personales_secciones["comorbilidades"] = comorbilidades_dict

                    else:
                        if keyword == "edad" and isEdad == True:
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

                # Separar la línea en partes basadas en "/"
                partes = linea.split("/")

                for parte in partes:
                    parte = parte.strip()
                    if any(rel in parte for rel in ["primo", "tío", "prima", "tía", "hermano", "hermana"]):
                        lateralidad.append(parte)
                    elif any(rel in parte for rel in ["padre", "madre", "abuelo", "abuela"]):
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
            if "biología tumoral" in linea:
                match1 = re.search(r"mama izquierda:(.+?)mama derecha:(.+)", linea)
                if match1:
                    izquierda = match1.group(1).strip()
                    derecha = match1.group(2).strip()

                    # Extraer datos específicos de cada mama
                    for mama, texto in [("mama_izquierda", izquierda), ("mama_derecha", derecha)]:
                        inmunohistoquímica_tumoral_secciones[mama]["re"] = re.search(r"re (\d+%)", texto).group(1) if re.search(r"re (\d+%)", texto) else None
                        inmunohistoquímica_tumoral_secciones[mama]["rp"] = re.search(r"rp (\d+%)", texto).group(1) if re.search(r"rp (\d+%)", texto) else None
                        inmunohistoquímica_tumoral_secciones[mama]["her2"] = "negativo" if "her2 negativo" in texto else "positivo"
                        inmunohistoquímica_tumoral_secciones[mama]["ki67"] = re.search(r"ki67 (\d+%)", texto).group(1) if re.search(r"ki67 (\d+%)", texto) else None
                        inmunohistoquímica_tumoral_secciones[mama]["gh"] = re.search(r"g\d", texto).group(0) if re.search(r"g\d", texto) else None

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
            if "cáncer de mama" in linea or "diagnóstico" in linea:
                # Quitar "Cáncer de mama bilateral." si está al inicio
                linea = re.sub(r"^cáncer de mama bilateral\.?", "", linea).strip()

                # Verificar si hay una barra "/" que indica ambas mamas
                if "/" in linea:
                    partes = linea.split("/")
                    for parte in partes:
                        parte = parte.strip()

                        # Extraer correctamente cada mama
                        if re.search(r"\bmi\b|\bmama izquierda\b", parte, re.IGNORECASE):
                            clasificacion["mama_izquierda"]["clasificación"] = re.sub(r"^(mi|mama izquierda)\s*", "", parte.replace("diagnóstico: ", ""), flags=re.IGNORECASE).strip()
                        if re.search(r"\bmd\b|\bmama derecha\b", parte, re.IGNORECASE):
                            clasificacion["mama_derecha"]["clasificación"] = re.sub(r"^(md|mama derecha)\s*", "", parte.replace("diagnóstico: ", ""), flags=re.IGNORECASE).strip()

                else:
                    # Buscar clasificación individual con más flexibilidad
                    match_izq = re.search(r"(?:diagnóstico:\s*)?(.*?)(?:\bmi\b|\bmama izquierda\b)\s*(.+)", linea, re.IGNORECASE)
                    match_der = re.search(r"(?:diagnóstico:\s*)?(.*?)(?:\bmd\b|\bmama derecha\b)\s*(.+)", linea, re.IGNORECASE)

                    if match_izq:
                        clasificacion["mama_izquierda"]["clasificación"] = f"{match_izq.group(1).strip()} {match_izq.group(2).strip()}".strip()
                    if match_der:
                        clasificacion["mama_derecha"]["clasificación"] = f"{match_der.group(1).strip()} {match_der.group(2).strip()}".strip()

            # Buscar descripción de la extensión del tumor
            if "extensión del tumor" in linea:
                match_izq = re.search(r"mama izquierda ([^\(]+) \(([^)]+)\)", linea)
                match_der = re.search(r"mama derecha ([^\(]+) \(([^)]+)\)", linea)
                if match_izq:
                    clasificacion["mama_izquierda"]["descripcion"] = f"{match_izq.group(1).strip()} ({match_izq.group(2).strip()})"
                if match_der:
                    clasificacion["mama_derecha"]["descripcion"] = f"{match_der.group(1).strip()} ({match_der.group(2).strip()})"

        self.data["tipo"] = clasificacion
        # self.imprimir_data()

    def __extraer_datos_estadia_tumoral(self):
        """
        Extrae y estructura los datos de estadia tumoral del texto procesado.

        Los datos se almacenan en el diccionario `data` bajo la clave "estadia_tumoral".

        Los datos a extraer suelen estar dentro de este tipo de secciones:
        Extensión del tumor: Mama izquierda EC IIA (pT1c, pN1a, MO) Mama derecha EC IIA (pT2, NO, MO)
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
                # Expresión regular flexible para capturar los campos pT, pN, M en cualquier orden
                regex = r"(mama (izquierda|derecha)) [^\(]+\(([^)]+)\)"
                matches = re.findall(regex, linea, re.IGNORECASE)

                for match in matches:
                    mama_lado = match[0].lower()  # "mama izquierda" o "mama derecha"
                    campos = match[2].split(",")  # Separar los campos por comas

                    # Inicializar un diccionario temporal para almacenar los campos
                    campos_extraidos = {}

                    for campo in campos:
                        campo = campo.strip().lower()
                        if campo.startswith("pt"):
                            campos_extraidos["centros_tumorales"] = campo
                        elif campo.startswith("pn") or campo.startswith("n"):
                            campos_extraidos["nódulos"] = campo
                        elif campo.startswith("m"):
                            campos_extraidos["metástasis"] = campo

                    # Asignar los campos extraídos al diccionario correspondiente
                    if mama_lado == "mama izquierda":
                        estadia_tumoral_secciones["mama_izquierda"].update(campos_extraidos)
                    elif mama_lado == "mama derecha":
                        estadia_tumoral_secciones["mama_derecha"].update(campos_extraidos)

        self.data["estadia_tumoral"] = estadia_tumoral_secciones