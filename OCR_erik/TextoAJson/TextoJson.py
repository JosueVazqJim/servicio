import json
import re
import os
import glob
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
        self.nombre = None
        self.limpiador = LimpiezaTexto()
        self.fases = []
        self.informacion = []
        self.data = {
            "antecedentes_personales": {},
            "antecedentes_familiares": {},
            "estadía_tumoral": {},
            "inmunohistoquímica_tumoral": {},
            "tipo": {},
        }
        self.evoluciones = []
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

    def __hay_fases(self):
        """
        Verifica si el contenido contiene fases separadas por líneas de asteriscos,
        seguido de texto real en las siguientes líneas.
        
        Retorna:
            bool: True si hay fases detectadas, False en caso contrario.
        """
        asterisco_pattern = re.compile(r'^\*+$')
        
        for i, linea in enumerate(self.informacion):
            linea = linea.strip()
            
            if asterisco_pattern.match(linea):
                # Revisar si después de los asteriscos hay texto real
                if i + 1 < len(self.informacion):
                    siguiente_linea = self.informacion[i + 1].strip()
                    if siguiente_linea and not asterisco_pattern.match(siguiente_linea):  # Hay contenido después de los asteriscos y no es otra línea de asteriscos
                        return True
        return False  # No se detectaron fases reales
    
    def __separar_fases(self):
        """
        Divide el contenido en diferentes fases
        cada vez que encuentra líneas de asteriscos.
        
        Almacena cada fase como un elemento en la lista self.fases.
        """
        self.fases = []
        bloque_actual = []
        aux1 = 0
        aux2 = 0
        n = len(self.informacion)
        bandera = False
        
        aux2 = self.__buscar_linea_asteriscos(aux1)
        bandera = True

        while aux2 < n:
            if bandera:
                resultado = self.__buscar_linea_asteriscos_diagnostico(aux2)
            
                if resultado is None:  # No hay más patrones
                    # Agregar desde aux1 hasta aux2 como fase final
                    bloque_actual = [linea.strip() for linea in self.informacion[aux1:aux2]]
                    if bloque_actual:
                        self.fases.append(bloque_actual)
                    break
                    
                pos, tipo = resultado
                
                if tipo == 'diagnóstico':
                    # Guardar bloque desde aux1 hasta aux2
                    bloque_actual = [linea.strip() for linea in self.informacion[aux1:aux2]]
                    if bloque_actual:
                        self.fases.append(bloque_actual)
                    aux1 = aux2  # Movemos aux1 al inicio del diagnóstico
                    bandera = False  # Cambiamos la bandera para buscar asteriscos
                else:  # 'asteriscos'
                    aux2 = pos  # Actualizamos aux2 al nuevo asterisco
                    # Continuamos buscando sin cambiar aux1
            else:
                # Buscar siguiente asterisco desde aux1+1
                aux2 = self.__buscar_linea_asteriscos(aux1)
                if aux2 is None:
                    # No hay más asteriscos, agregar bloque actual
                    bloque_actual = [linea.strip() for linea in self.informacion[aux1:]]
                    if bloque_actual:
                        self.fases.append(bloque_actual)
                    break
                else:
                    bandera = True  # Cambiamos la bandera para buscar diagnóstico
            
    
    def __buscar_linea_asteriscos_diagnostico(self, inicio):
        for i in range(inicio + 1, len(self.informacion)):
            linea = self.informacion[i].strip()
            if linea.startswith("*"):
                return i, "asteriscos"
            elif linea.startswith("diagnóstico"):
                return i, "diagnóstico"
        return None
    
    def __buscar_linea_asteriscos(self, inicio):
        for i in range(inicio + 1, len(self.informacion)):
            linea = self.informacion[i].strip()
            if linea.startswith("*"):
                return i
        return None

    def __detector_pezones(self):
        """
        Establece el lado de la mama del caso actual.
        Solo considera las mamas afectadas por cáncer, basándose en las secciones de diagnóstico,
        extensión del tumor o biología tumoral. 
        En caso de no detectar ninguna mama afectada, se establece como Non y se continua llenando
        la estructura JSON sin indicar la mama afectada.
        """
        mama_izquierda_flag = False
        mama_derecha_flag = False
        bilateral_flag = False

        # Palabras clave que indican las secciones relevantes
        secciones_relevantes = ["diagnóstico", "extensión del tumor", "biología tumoral", "mama"]

        for linea in self.informacion:
            # Verificar si la línea pertenece a una sección relevante
            if any(linea.startswith(seccion) for seccion in secciones_relevantes):
                if "mama izquierda" in linea:
                    mama_izquierda_flag = True
                if "mama derecha" in linea:
                    mama_derecha_flag = True
                if "bilateral" in linea:
                    bilateral_flag = True

        # Determinar el lado de la mama basado en las banderas
        if (mama_izquierda_flag and mama_derecha_flag) or (bilateral_flag):
            self.mama = "bilateral"
        elif mama_izquierda_flag:
            self.mama = "mama_izquierda"
        elif mama_derecha_flag:
            self.mama = "mama_derecha"  
        else:
            self.mama = None  # Si no se detecta ninguna mama afectada
        
        print(f"Se detectó mama: {self.mama}")



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
                units.append((value, match[1]))
            elif match[2] and match[3]:  # Caso: "año 1" o "años 1.5"
                value = float(match[3]) if '.' in match[3] else int(match[3])  # Parseo de dígitos
                units.append((value, match[2]))

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
                "trh": None,
                "aco": None,
                "mpf": None,
                "estado_hormonal": None,
                "métodos_anticonceptivos": None,
                "g": None,
                "p": None,
                "c": None,
                "a": None
            }
        }

        #palaras clave para antecedentes_personales que buscaremos en el texto
        antecedentes_personales_keywords = [
           "sexo", "peso", "talla", "preferencia",
            "índice tabáquico", "tabaco", "tabaquismo", "alcohol", "drogas",
            "comorbilidades", "antecedentes ginecológicos", "menarca", "fum", 
            "trh", "mpf", "aco", "estado hormonal", "métodos anticonceptivos"
        ]

        isEdad = False
        isEstadoHormonal = False

        # Agregar una regex para detectar edades en el formato "XX años"
        edad_regex = re.compile(
            r'\b(?:edad:?\s*(\d+)(?:\s*años)?)|'  # Caso 1: "edad: 45" o "edad 45 años"
            r'(?:\b(\d+)\s*años(?:\s*de\s*edad)?)|'  # Caso 2: "45 años" o "45 años de edad"
            r'^(.*?)\s*/\s*(\d+)\s*/\s*(\d+\s*años?)\s*/\s*(.*)$|'  # Caso 3: "institución / ID / edad / médico"
            r'(?:\b(\w+)\s*\/\s*(\d+)\s*\/\s*(\d+)\s*años\b)',  # Caso 4: "institución / ID / edad años"
            re.IGNORECASE
        )

        g_p_c_a_regex = re.compile(
            r'\b[g](\d+)\b[^p]*\b[p](\d+)\b[^c]*\b[c](\d+)\b[^a]*\b[a](\d+)\b',
            re.IGNORECASE
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

            matchGPCA = g_p_c_a_regex.match(linea)
            if matchGPCA:
                antecedentes_personales_secciones["antecedentes_ginecológicos"]['g'] = int(matchGPCA[1])  # Tomar el número directamente
                antecedentes_personales_secciones["antecedentes_ginecológicos"]['p'] = int(matchGPCA[2])  # Tomar el número directamente
                antecedentes_personales_secciones["antecedentes_ginecológicos"]['c'] = int(matchGPCA[3])  # Tomar el número directamente
                antecedentes_personales_secciones["antecedentes_ginecológicos"]['a'] = int(matchGPCA[4])  # Tomar el número directamente

            for keyword in antecedentes_personales_keywords:
                if keyword in linea:

                    # Si la keyword es "tabaquismo" o "tabaco" o "índice tabáquico" y si tiene o no ":" que separan
                    if keyword == "tabaquismo" or keyword == "tabaco" or keyword == "índice tabáquico":
                        # Removemos los ":" si están presentes
                        if ":" in linea:
                            linea = linea.replace(":", "")

                        # Extraemos el estado del tabaquismo y cualquier unidad de tiempo
                        estados = ["negado", "suspendido", "fumador", "negadas"]
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
                    elif keyword == "talla":
                        # Extraer solo el fragmento consecuente de "talla"
                        match = re.search(r"talla\s*[:\-]?\s*(\d+\.?\d*)", linea, re.IGNORECASE)
                        if match:
                            antecedentes_personales_secciones["talla"] = match.group(1)
                        else:
                            # Buscar "talla" en un contexto como "talla baja"
                            match_contextual = re.search(r"talla\s*(baja|alta|normal)", linea, re.IGNORECASE)
                            if match_contextual:
                                antecedentes_personales_secciones["talla"] = match_contextual.group(1).lower()


                    elif keyword in ["fum", "menarca", "trh", "aco", "mpf", "estado hormonal", "métodos anticonceptivos"]:
                        # Patrón para identificar claves ginecológicas en la línea
                        pattern = re.compile(r'\b(fum|menarca|trh|mpf|aco|estado hormonal|métodos anticonceptivos)\b', re.IGNORECASE)
                        pattern_especial = re.match(r"menarca a los (\d+) años\. (\d+) embarazos?, (\d+) partos?", linea, re.IGNORECASE)

                        if pattern_especial:
                            edad_menarca, num_embarazos, num_partos = map(int, pattern_especial.groups())
                            antecedentes_personales_secciones["antecedentes_ginecológicos"]["menarca"] = {"años": edad_menarca}
                            
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
                            
                            elif 'estado hormonal' in matches:
                                valor = None
                                if ":" in linea_limpia:
                                    valor = linea_limpia.split(":")[1].strip()
                                else:
                                    valor = linea_limpia.split(matches[0])[1].strip()
                                
                                unidades = self.__extract_units(valor)
                                if unidades:
                                    valor_dict = {unidad: cantidad for cantidad, unidad in unidades}
                                    if len(valor.split()) > 2:
                                        valor_dict["contexto"] = valor
                                    antecedentes_personales_secciones["antecedentes_ginecológicos"][matches[0].strip().replace(" ", "_")] = valor_dict
                                else:
                                    antecedentes_personales_secciones["antecedentes_ginecológicos"][matches[0].strip().replace(" ", "_")] = valor
                                
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

                    elif keyword == "comorbilidades":
                        comorbilidades = linea
                        comorbilidades = comorbilidades.replace("comorbilidades:", "").strip()
                        
                        # Verificar si está negado
                        if "negad" in comorbilidades:
                            antecedentes_personales_secciones["comorbilidades"] = "negadas"
                            continue
                        
                        # Dividir la cadena en comorbilidades individuales
                        #!!!!!!!!!!!!!!!!!!!!!!
                        comorbilidades_list = re.split(r'\d+\.\s|\.\s|\||(?<=\(\d{4}\)),', comorbilidades)
                        comorbilidades_list = [item for item in comorbilidades_list if item and not item.isdigit()]

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
                        if re.match(r'^\d+\.|\(\d{4}\)', linea):  # Evitar claves en listas numeradas o con fechas
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
            linea = linea.strip()

            # Verificar si está negado
            if "ahf" in linea and "negado" in linea:
                self.data["antecedentes_familiares"] = {
                    "ascendencia": "negado",
                    "lateralidad": "negado",
                    "descendencia": "negado"
                }
                return
            
            if "ahf" in linea and "desconocemos" in linea:
                self.data["antecedentes_familiares"] = {
                    "ascendencia": "desconocemos",
                    "lateralidad": "desconocemos",
                    "descendencia": "desconocemos"
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

    def __extraer_datos_inmunohistoquímica_tumoral(self):
        """
        Extrae y estructura los datos de inmunohistoquímica tumoral del texto procesado.
        Primero busca en 'biología tumoral' y solo si no encuentra datos, busca en 'diagnóstico'.
        Mantiene la estructura original de dos diccionarios separados.
        """
        # Estructura de datos para inmunohistoquímica tumoral
        inmunohistoquimica_tumoral_secciones = {
            "mama_izquierda": {
                "re": None, "rp": None, "her2": None, "ki67": None, "gh": None
            },
            "mama_derecha": {
                "re": None, "rp": None, "her2": None, "ki67": None, "gh": None
            }
        }

        # Patrones de búsqueda mejorados (incluyendo el patrón para HER2 con paréntesis)
        patrones = {
            "re": re.compile(r"re\s*[:]?\s*(\d+%|\+|\-|positivo|negativo)", re.IGNORECASE),
            "rp": re.compile(r"rp\s*[:]?\s*(\d+%|\+|\-|positivo|negativo)", re.IGNORECASE),
            "her2": re.compile(r"her\s*2\s*[:]?\s*((?:\+{1,3})|\d+\+?\s*\(.*?\)|\d+\+?|\-|\+|negativo|positivo)", re.IGNORECASE),
            "ki67": re.compile(r"ki67\s*[:]?\s*(\d+%|\w+)", re.IGNORECASE),
            "gh": re.compile(r"gh\s*[:]?\s*(\d+)", re.IGNORECASE)
        }

        evoluciones = []

        # Variables para controlar si encontramos datos en biología tumoral
        encontrado_en_biologia = False

        if self.mama is not None:
            # Primera pasada: buscar solo en biología tumoral
            for linea in self.informacion:            
                # Verificar si estamos en biología tumoral
                if "biología tumoral" in linea and encontrado_en_biologia == False:
                    encontrado_en_biologia = True
                    # Extraer datos para cada marcador
                    for marcador, patron in patrones.items():
                        match = patron.search(linea)
                        if match:
                            valor = match.group(1).strip()
                            
                            # Asignar el valor según la mama detectada
                            if self.mama == "bilateral":
                                # Procesamiento especial para casos bilaterales
                                secciones = re.split(r"mama (izquierda|derecha)", linea, flags=re.IGNORECASE)
                                for i, seccion in enumerate(secciones):
                                    if seccion == "izquierda":
                                        match_izq = patron.search(secciones[i+1])
                                        if match_izq:
                                            val = match_izq.group(1).strip()
                                            inmunohistoquimica_tumoral_secciones["mama_izquierda"][marcador] = val
                                    elif seccion == "derecha":
                                        match_der = patron.search(secciones[i+1])
                                        if match_der:
                                            val = match_der.group(1).strip()
                                            inmunohistoquimica_tumoral_secciones["mama_derecha"][marcador] = val
                            elif self.mama == "mama_izquierda":
                                inmunohistoquimica_tumoral_secciones["mama_izquierda"][marcador] = valor
                            elif self.mama == "mama_derecha":
                                inmunohistoquimica_tumoral_secciones["mama_derecha"][marcador] = valor

                if "biología tumoral final" in linea or "biología tumoral pos" in linea:
                    evoluciones.append(linea.strip())
                


            # Segunda pasada: buscar en diagnóstico solo si no encontramos en biología tumoral
            if not encontrado_en_biologia or not any(
                val is not None 
                for dic in [inmunohistoquimica_tumoral_secciones["mama_izquierda"], 
                            inmunohistoquimica_tumoral_secciones["mama_derecha"]] 
                for val in dic.values()
            ):
                for linea in self.informacion:
                    
                    # Verificar si estamos en diagnóstico
                    if "diagnóstico" in linea:
                        # Extraer datos para cada marcador
                        for marcador, patron in patrones.items():
                            match = patron.search(linea)
                            if match:
                                valor = match.group(1).strip()
                                
                                # Solo asignar si no tenemos ya un valor (de biología tumoral)
                                if self.mama == "bilateral":
                                    if inmunohistoquimica_tumoral_secciones["mama_izquierda"][marcador] is None:
                                        inmunohistoquimica_tumoral_secciones["mama_izquierda"][marcador] = valor
                                    if inmunohistoquimica_tumoral_secciones["mama_derecha"][marcador] is None:
                                        inmunohistoquimica_tumoral_secciones["mama_derecha"][marcador] = valor
                                elif self.mama == "mama_izquierda":
                                    if inmunohistoquimica_tumoral_secciones["mama_izquierda"][marcador] is None:
                                        inmunohistoquimica_tumoral_secciones["mama_izquierda"][marcador] = valor
                                elif self.mama == "mama_derecha":
                                    if inmunohistoquimica_tumoral_secciones["mama_derecha"][marcador] is None:
                                        inmunohistoquimica_tumoral_secciones["mama_derecha"][marcador] = valor

            self.data["inmunohistoquímica_tumoral"] = inmunohistoquimica_tumoral_secciones
            if evoluciones:
                for evolucion in evoluciones:
                    # Crear NUEVO diccionario en cada iteración
                    aux = {
                        "mama_izquierda": {
                            "re": None, "rp": None, "her2": None, "ki67": None, "gh": None
                        },
                        "mama_derecha": {
                            "re": None, "rp": None, "her2": None, "ki67": None, "gh": None
                        }
                    }
                    
                    # Crear NUEVO resumen en cada iteración
                    resumen = self.data.copy()  # Copia profunda de los datos base
                    
                    for marcador, patron in patrones.items():
                        match = patron.search(evolucion)
                        if match:
                            valor = match.group(1).strip()
                            
                            # Asignar el valor según la mama detectada
                            if self.mama == "bilateral":
                                secciones = re.split(r"mama (izquierda|derecha)", evolucion, flags=re.IGNORECASE)
                                for i, seccion in enumerate(secciones):
                                    if seccion == "izquierda":
                                        match_izq = patron.search(secciones[i+1])
                                        if match_izq:
                                            val = match_izq.group(1).strip()
                                            aux["mama_izquierda"][marcador] = val
                                    elif seccion == "derecha":
                                        match_der = patron.search(secciones[i+1])
                                        if match_der:
                                            val = match_der.group(1).strip()
                                            aux["mama_derecha"][marcador] = val
                            elif self.mama == "mama_izquierda":
                                aux["mama_izquierda"][marcador] = valor
                            elif self.mama == "mama_derecha":
                                aux["mama_derecha"][marcador] = valor
                    
                    # Asignar la nueva estructura al resumen
                    resumen["inmunohistoquímica_tumoral"] = {
                        "mama_izquierda": aux["mama_izquierda"].copy(),
                        "mama_derecha": aux["mama_derecha"].copy()
                    }
                    
                    self.evoluciones.append(resumen)
        else:
            # Si no se detecta mama, asignar los datos de biología tumoral directamente
            self.data["inmunohistoquímica_tumoral"] = inmunohistoquimica_tumoral_secciones
            
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

        patron = r"(ct\d+\w*|pt\d+\w*|pn\d+\w*|n\d+\w*|cn\d+\w*|m\d+\w*)"
        
        if self.mama is not None:
            for linea in self.informacion:
                linea = linea.strip()

                try:
                    # Extraer datos de la extensión del tumor o diagnóstico
                    if "extensión del tum" in linea or "diagnóstico" in linea:
                        # Buscar si hay información para ambas mamas o solo una
                        if self.mama == "bilateral":
                            try:
                                secciones = re.split(r"mama (izquierda|derecha)", linea, flags=re.IGNORECASE)
                                seccion_izquierda = secciones[2].strip()
                                seccion_derecha = secciones[4].strip()

                                # Expresión regular mejorada para capturar campos con guiones o caracteres especiales
                                campos_izquierda = re.findall(patron, seccion_izquierda, re.IGNORECASE)
                                for campo in campos_izquierda:
                                    if campo.startswith(('pt','ct','t')):
                                        estadia_tumoral_secciones["mama_izquierda"]["centros_tumorales"] = campo
                                    elif campo.startswith(('pn','n','cn')):
                                        estadia_tumoral_secciones["mama_izquierda"]["nódulos"] = campo
                                    elif campo.startswith("m"):
                                        estadia_tumoral_secciones["mama_izquierda"]["metástasis"] = campo

                                campos_derecha = re.findall(patron, seccion_derecha, re.IGNORECASE)
                                for campo in campos_derecha:
                                    if campo.startswith(('pt','ct','t')):
                                        estadia_tumoral_secciones["mama_derecha"]["centros_tumorales"] = campo
                                    elif campo.startswith(('pn','n','cn')):
                                        estadia_tumoral_secciones["mama_derecha"]["nódulos"] = campo
                                    elif campo.startswith("m"):
                                        estadia_tumoral_secciones["mama_derecha"]["metástasis"] = campo
                            except IndexError:
                                print("Error al procesar datos de mama bilateral para la estadia tumoral. Se identificaron la mención de mama izquierda y derecha, pero se procede de otra manera.")
                                # Extraer datos en base a "mama izquierda" o "mama derecha" si el try falla
                                if "mama izquierda" in linea:
                                    campos_izquierda = re.findall(patron, linea, re.IGNORECASE)
                                    for campo in campos_izquierda:
                                        if campo.startswith(('pt','ct','t')):
                                            estadia_tumoral_secciones["mama_izquierda"]["centros_tumorales"] = campo
                                        elif campo.startswith(('pn','n','cn')):
                                            estadia_tumoral_secciones["mama_izquierda"]["nódulos"] = campo
                                        elif campo.startswith("m"):
                                            estadia_tumoral_secciones["mama_izquierda"]["metástasis"] = campo

                                if "mama derecha" in linea:
                                    campos_derecha = re.findall(patron, linea, re.IGNORECASE)
                                    for campo in campos_derecha:
                                        if campo.startswith(('pt','ct','t')):
                                            estadia_tumoral_secciones["mama_derecha"]["centros_tumorales"] = campo
                                        elif campo.startswith(('pn','n','cn')):
                                            estadia_tumoral_secciones["mama_derecha"]["nódulos"] = campo
                                        elif campo.startswith("m"):
                                            estadia_tumoral_secciones["mama_derecha"]["metástasis"] = campo

                        elif self.mama == "mama_izquierda":
                            # Expresión regular mejorada para capturar campos con guiones o caracteres especiales
                            campos = re.findall(patron, linea, re.IGNORECASE)
                            for campo in campos:
                                if campo.startswith(('pt','ct','t')):
                                    estadia_tumoral_secciones["mama_izquierda"]["centros_tumorales"] = campo
                                elif campo.startswith(('pn','n','cn')):
                                    estadia_tumoral_secciones["mama_izquierda"]["nódulos"] = campo
                                elif campo.startswith("m"):
                                    estadia_tumoral_secciones["mama_izquierda"]["metástasis"] = campo

                        elif self.mama == "mama_derecha":
                            # Expresión regular mejorada para capturar campos con guiones o caracteres especiales
                            campos = re.findall(patron, linea, re.IGNORECASE)
                            for campo in campos:
                                if campo.startswith(('pt', 't', 'ct')): 
                                    estadia_tumoral_secciones["mama_derecha"]["centros_tumorales"] = campo
                                elif campo.startswith(('pn', 'n', 'cn')):
                                    estadia_tumoral_secciones["mama_derecha"]["nódulos"] = campo
                                elif campo.startswith("m"):
                                    estadia_tumoral_secciones["mama_derecha"]["metástasis"] = campo

                except:
                    print("Error en algún formato que imposibilita extraer los datos para la estadía tumoral")

            self.data["estadía_tumoral"] = estadia_tumoral_secciones
        else:
            self.data["estadía_tumoral"] = estadia_tumoral_secciones

    
    def __extraer_datos_clasificacion(self):
        """
        Extrae y estructura los datos de clasificación del cáncer del texto procesado.

        Los datos se almacenan en el diccionario `data` bajo la clave "tipo".
        """
        clasificacion = {
            "mama_izquierda": {"clasificación": None, "descripcion": None},
            "mama_derecha": {"clasificación": None, "descripcion": None},
        }

        if self.mama is not None:
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

                if "extensión del tum" in linea:
                    # Buscar mama izquierda
                    match_izq = re.search(r"mama izquierda\s+([^\(]+)(?:\s*\(.*\))?", linea, re.IGNORECASE)
                    # Buscar mama derecha
                    match_der = re.search(r"mama derecha\s+([^\(]+)(?:\s*\(.*\))?", linea, re.IGNORECASE)
                    
                    if match_izq:
                        clasificacion["mama_izquierda"]["descripcion"] = f"{match_izq.group(1).strip()}"
                    if match_der:
                        clasificacion["mama_derecha"]["descripcion"] = f"{match_der.group(1).strip()}"

            self.data["tipo"] = clasificacion
        else:
            self.data["tipo"] = clasificacion

    def __aplicar_mapa_semantico(self):
        """
        Aplica mapas semánticos para completar datos que no se encontraron con los patrones directos.
        """
        # Mapa semántico para los campos GPCA
        mapa_gpca = {
            'g': ['gestacion', 'gestaciones', 'embarazos', 'embarazo', "gestas"],
            'p': ['partos', 'parto'],
            'c': ['cesareas', 'cesáreas', 'cesarea', 'cesárea'],
            'a': ['abortos', 'aborto']
        }

        # mapa para la inmunohistoquimica tumoral
        mapa_inmunohistoquimica = {
            "triple negativo": {
                "re": "negativo",
                "rp": "negativo",
                "her2": "negativo"
            },
            "triple positivo": {
                "re": "positivo",
                "rp": "positivo",
                "her2": "positivo"
            },
        }


        # Verificar si las claves "g", "p", "c", "a" son None en self.data["antecedentes_personales"]["antecedentes_ginecológicos"]
        gpca_data = self.data.get("antecedentes_personales", {}).get("antecedentes_ginecológicos", {})
        
        if not all(gpca_data.get(letra) is not None for letra in ["g", "p", "c", "a"]):  # Verificar si alguna clave es None
            for linea in self.informacion:
                # Buscar términos relacionados con cada componente de GPCA
                for letra, terminos in mapa_gpca.items():
                    if gpca_data.get(letra) is None:  # Solo si no tenemos el dato
                        for termino in terminos:
                            if termino in linea:
                                # Extraer número asociado al término
                                # match = re.search(rf'{termino}\D*(\d+)', linea)
                                match = re.search(rf'(\d+)\s*\D*{termino}', linea, re.IGNORECASE)
                                if match:
                                    gpca_data[letra] = int(match.group(1))  # Actualizar el valor en gpca_data
                                    break  # Salir del bucle si ya encontramos el dato
        
        for letra in ["g", "p", "c", "a"]:
            if gpca_data.get(letra) is None:
                gpca_data[letra] = 0
        
        # Actualizar self.data con los cambios realizados en gpca_data
        self.data["antecedentes_personales"]["antecedentes_ginecológicos"] = gpca_data

        if (self.mama is not None) and (self.mama != "bilateral"):
            inmuno_data = self.data.get("inmunohistoquímica_tumoral", {}).get(self.mama, {})
        
            # Solo buscamos si alguno es None
            if any(inmuno_data.get(marcador) is None for marcador in ["re", "rp", "her2"]):
                print("Intentando llenar inmunohistoquímica tumoral con su mapa")
                for linea in self.informacion:
                    for termino, valores in mapa_inmunohistoquimica.items():
                        if termino in linea.lower():
                            for marcador, resultado in valores.items():
                                if inmuno_data.get(marcador) is None:
                                    inmuno_data[marcador] = resultado
            
            self.data["inmunohistoquímica_tumoral"][self.mama] = inmuno_data


    
    def __verificar_valores_nulos(self, ruta_log, nombre_caso):
        """
        Verifica los valores nulos en el diccionario self.data y guarda los resultados en un archivo de texto.

        Args:
            ruta_log (str): Ruta del archivo de texto donde se guardarán los valores nulos.
        """
        valores_nulos = {}

        # Función recursiva para recorrer los diccionarios anidados
        def verificar_subniveles(d, clave_principal=None):
            for clave, valor in d.items():
                if isinstance(valor, dict):
                    # Si el valor es un diccionario, llamamos a la función recurasiva
                    verificar_subniveles(valor, clave)
                elif clave not in ["ultrasonido", "mastografía"] and (valor is None or (isinstance(valor, (dict, list)) and not valor)):
                    # Si encontramos un valor nulo o vacío (excepto ultrasonido y mastografía), lo registramos
                    if clave_principal not in valores_nulos:
                        valores_nulos[clave_principal] = {}
                    valores_nulos[clave_principal][clave] = valor

        # Llamar a la función recursiva
        verificar_subniveles(self.data)

        if valores_nulos:
            # Asegúrate de que la ruta log es válida
            ruta_log = ruta_log + '/log.txt'

            try:
                with open(ruta_log, "a") as log_file:
                    log_file.write(f"Nombre del caso: {nombre_caso}\n")
                    log_file.write("Valores nulos encontrados:\n")
                    for clave_principal, subdiccionario in valores_nulos.items():
                        log_file.write(f"  - {clave_principal}:\n")
                        for subclave, valor in subdiccionario.items():
                            log_file.write(f"    - {subclave}: {valor}\n")
                    log_file.write("\n")
            except Exception as e:
                print(f"Error al escribir en el archivo de log: {e}")

    
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
        self.nombre = self.__extraer_nombre_txt().replace(".txt", "")
    

        os.makedirs(ruta_destino, exist_ok=True)  # Crear carpeta si no existe

        self.__limpiar_texto()

        if self.__hay_fases():
            # Si detecta fases, las separa
            self.__separar_fases()

            for idx, fase in enumerate(self.fases, start=1):
                self.informacion = fase  # Setea la fase actual como la información a procesar
                
                self.imprimir_info()

                self.__detector_pezones()
                self.__extraer_datos_antecedentes_personales()
                self.__extraer_datos_antecedentes_familiares()
                self.__extraer_datos_estadia_tumoral()
                self.__extraer_datos_clasificacion()
                self.__extraer_datos_inmunohistoquímica_tumoral()

                for i, evolucion in enumerate(self.evoluciones, start=1):
                    self.__crear_json(f"{self.nombre}_{idx}_{i}.json", evolucion)
                
                self.__aplicar_mapa_semantico()
                print('_________________________')
                nombre_json_fase = f"{self.nombre}_{idx}.json"  # Ejemplo: 123_1.json, 123_2.json
                self.__verificar_valores_nulos(ruta_destino, nombre_json_fase)
                self.__crear_json(nombre_json_fase, self.data)

                self.__limpiar_instancia(parcial=True)  # Limpia solo lo necesario para cada fase
        else:
            self.imprimir_info()
            # Solo un caso completo
            self.__detector_pezones()
            self.__extraer_datos_antecedentes_personales()
            self.__extraer_datos_antecedentes_familiares()
            self.__extraer_datos_estadia_tumoral()
            self.__extraer_datos_clasificacion()
            self.__extraer_datos_inmunohistoquímica_tumoral()
            self.__aplicar_mapa_semantico()
            print('_________________________')

            nombre_json = f"{self.nombre}.json"
            self.__verificar_valores_nulos(ruta_destino, nombre_json)
            self.__crear_json(nombre_json, self.data)

        self.__limpiar_instancia()

    def __limpiar_instancia(self, parcial=False):
            """
            Limpia el atributo "data" para evitar que se mezclen los datos de diferentes casos.
            Si parcial es True, limpia self.data y self.mama.
            """
            if parcial:
                self.data = {
                    "antecedentes_personales": {},
                    "antecedentes_familiares": {},
                    "estadía_tumoral": {},
                    "inmunohistoquímica_tumoral": {},
                    "tipo": {},
                }
                self.mama = None
            else:
                self.rutaTxt = None
                self.rutaDestino = None
                self.nombre = None
                self.mama = None
                self.informacion = []
                self.fases = []
                self.data = {
                    "antecedentes_personales": {},
                    "antecedentes_familiares": {},
                    "estadía_tumoral": {},
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

    def __crear_json(self, nombreJSON, diccionario):
        """
        Crea un archivo JSON con el atributo "data" que es un diccionario.

        Args:
            destino (str): Ruta del archivo JSON que se creará.
        """

        with open(os.path.join(self.rutaDestino, nombreJSON), 'w', encoding="utf-8") as file:
            json.dump(diccionario, file, indent=4, ensure_ascii=False)
