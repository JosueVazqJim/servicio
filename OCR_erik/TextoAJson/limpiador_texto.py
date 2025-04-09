import re
import os

class LimpiezaTexto:
    """
    Clase para limpiar y procesar texto de un archivo, segmentándolo en claves y valores según palabras clave conocidas.
    """

    def __init__(self):
        """
        Inicializa la clase LimpiezaTexto.
        """
        self.nombreArchivo = None # Almacena la ruta del archivo de texto a procesar
        self.informacion = []  # Almacena el contenido del archivo después de la limpieza inicial
        self.texto_procesado = []  # Contendrá el texto final procesado

    def __cargar_datos(self):
        """
        Carga el archivo de texto, eliminando líneas vacías y convirtiendo a minúsculas.
        """
        if not os.path.exists(self.nombreArchivo):
            raise FileNotFoundError(f"El archivo {self.nombreArchivo} no existe.")

        try:
            with open(self.nombreArchivo, 'r', encoding='utf-8') as file:
                # Elimina líneas vacías y convierte el texto a minúsculas
                self.informacion = [linea.strip().lower() for linea in file if linea.strip()]
                
                # Elimina caracteres especiales al inicio de la línea, excepto separadores con 4 o más asteriscos y guiones
                self.informacion = [
                    re.sub(r'^[\s]*[^a-zA-Z0-9*-]+|^(?:\*{1,3}(?=\s|$))', '', linea)
                    for linea in self.informacion
                ]
        except PermissionError:
            raise PermissionError(f"No tienes permiso para abrir el archivo {self.nombreArchivo}.")
        except Exception as e:
            raise RuntimeError(f"Ocurrió un error al cargar el archivo {self.nombreArchivo}: {str(e)}")


    def __restaurar_instancia(self):
        """
        Restaura la instancia a su estado original.
        """
        self.nombreArchivo = None
        self.informacion = []
        self.texto_procesado = []

    def __unir_lineas_relevantes(self):
        """
        Une las líneas relevantes cuando sea necesario y deja otras líneas individuales.
        """

        claves_inicio = [
            "diagnóstico", "edad", "sexo", "peso", "talla", "preferencia", 
            "índice tabáquico", "tabaquismo", "tabaco", "alcohol", "drogas", 
            "comorbilidades", "antecedentes ginecológicos", "menarca", "embarazos", 
            "partos", "fum", "trh", "estado hormonal", "métodos anticonceptivos", 
            "cirugías", "originaria y residente", 'originar', "seguridad social", "ocupación", 
            "ahf", "resumen del", "extensión del tumor", "biología tumoral",
            "aco", "mpf", "eco", "mama izquierda", "mama derecha", "cáncer de mama bilateral", 'plan',
            "cdi ", 'carcinoma', "IHQ final", "extensión del tumot", "- fum"
        ]

        # Claves que deben tratarse como líneas individuales
        claves_palabras = {"menarca", "embarazos", "partos", "fum", "trh", "aco", "mpf", "métodos", "- fum" }

        # Patrones que se consideran claves
        patron_gn_pn_cn_an = re.compile(
            r'^\s*-?\s*(?:[gpca]\s*\d+\s*){4}(?:\s*\(.*?\))?\s*$', 
            re.IGNORECASE
        )
        patron_fecha = re.compile(r'\b\d{1,2}\.\d{1,2}\.\d{2}|\b\d{1,2}\.\d{4}')
        patron_linea_tipo = re.compile(r'^[^/]+ / \d+ / \d+ años / .+$')  # Patrón para detectar líneas del tipo "GACNC / 84959 / 67 años / Dra. Martínez"
        asterisco_pattern = re.compile(r'^\*+$')

        lineas_procesadas = []
        clave_actual = None
        valor_actual = []
        en_biologia_o_extension = False  # Bandera para identificar si estamos en "Biología tumoral" o "Extensión del tumor"
        
        for linea in self.informacion:
            linea = linea.strip()

            # Verificar si la línea es una clave de inicio
            es_clave_inicio = any(linea.startswith(clave) for clave in claves_inicio)
            es_clave_palabra = any(palabra in linea.split() for palabra in claves_palabras)
            es_patron = patron_gn_pn_cn_an.match(linea) or patron_fecha.match(linea) or patron_linea_tipo.match(linea) or asterisco_pattern.match(linea)

            # Detectar inicio de "Extensión del tumor" o "Biología tumoral"
            if linea.startswith("extensión del tumo") or linea.startswith("biología tumoral") or linea.startswith("extensión del tumot"):
                if clave_actual:
                    lineas_procesadas.append(f"{clave_actual} {' '.join(valor_actual).strip()}")
                clave_actual = linea
                valor_actual = []
                en_biologia_o_extension = True
                continue

            # Si estamos en "Biología tumoral" o "Extensión del tumor", seguir concatenando hasta que aparezca otra clave de inicio
            if en_biologia_o_extension:
                if any(linea.startswith(clave) for clave in claves_inicio if clave not in ["mama derecha", "mama izquierda", 'cdi ', 'carcinoma']):  # Si encontramos otra clave de inicio, cerramos el bloque
                    lineas_procesadas.append(f"{clave_actual} {' '.join(valor_actual).strip()}")
                    clave_actual = linea
                    valor_actual = []
                    en_biologia_o_extension = False
                    continue
                else:
                    valor_actual.append(linea)
                    continue

            if es_clave_inicio or es_patron:
                if clave_actual:
                    lineas_procesadas.append(f"{clave_actual} {' '.join(valor_actual).strip()}")
                clave_actual = linea
                valor_actual = []
            elif es_clave_palabra:
                if clave_actual:
                    lineas_procesadas.append(f"{clave_actual} {' '.join(valor_actual).strip()}")
                    clave_actual = None
                    valor_actual = []
                lineas_procesadas.append(linea)
            elif clave_actual:
                valor_actual.append(linea)
            else:
                lineas_procesadas.append(linea)

        # Guardar la última clave y su valor si existe
        if clave_actual:
            lineas_procesadas.append(f"{clave_actual} {' '.join(valor_actual).strip()}")

    
        self.texto_procesado = lineas_procesadas    
    
    def __filtrar_lineas_relevantes(self):
        """
        Filtra las líneas que contienen las claves o patrones relevantes.
        """
        # Lista de claves que indican el inicio de una nueva sección en el texto
        claves_inicio = [
            "diagnóstico", "edad", "sexo", "peso", "talla", "preferencia", 
            "índice tabáquico", "tabaquismo", "tabaco", "alcohol", "drogas", 
            "comorbilidades", "antecedentes ginecológicos", "menarca", "embarazos", 
            "partos", "fum", "trh", "estado hormonal", "métodos anticonceptivos", 
            "ahf", "extensión del tumor", "biología tumoral", "extensión del tumot",
            "aco", "mpf", "cáncer de mama bilateral", 'cdi ', 'carcinoma', "IHQ final"
        ]

        # Claves que pueden aparecer en cualquier parte de la línea como palabras individuales
        claves_palabras = ["menarca", "embarazos", "partos", "fum", "trh", "aco", "mpf"]

        # Patrones adicionales a conservar
        patron_gn_pn_cn_an = re.compile(
            r'\b(?=.*g\s*\d+)(?=.*p\s*\d+)(?=.*c\s*\d+)(?=.*a\s*\d+)[gpca\d\s]*\b',
            re.IGNORECASE
        )        
        patron_lista_numerada = r'^\d+\.\s'  # Patrón para detectar líneas numeradas (ej: "1. cáncer de mama")
        patron_vineta = r'^-\s'  # Patrón para detectar líneas con viñetas (ej: "- Tia materna con cáncer de páncreas")
        patron_linea_tipo = r'^[^/]+ / \d+ / \d+ años / .+$'  # Patrón para detectar líneas del tipo "GACNC / 84959 / 67 años / Dra. Martínez"
        patron_mama_lesiones = re.compile(r'\bmama\s*(izquierda|derecha|bilateral)\s*con.*lesi.*', re.IGNORECASE)
        patron_fecha = re.compile(r'\b\d{1,2}\.\d{1,2}\.\d{2}|\b\d{1,2}\.\d{4}')
        asterisco_pattern = re.compile(r'^\*+$')
        
        lineas_filtradas = []
        for linea in self.texto_procesado:
            linea = linea.strip()

            # Verificar si la línea comienza con una clave de inicio
            if any(linea.startswith(clave) for clave in claves_inicio):
                lineas_filtradas.append(linea)
                continue

            # Verificar si la línea contiene una clave como palabra individual
            if any(re.search(r'\b' + re.escape(clave) + r'\b', linea.lower()) for clave in claves_palabras):
                lineas_filtradas.append(linea)
                continue

            # Verificar si la línea coincide con los patrones adicionales
            if (re.match(patron_gn_pn_cn_an, linea) or
                re.match(patron_lista_numerada, linea) or
                re.match(patron_vineta, linea) or
                re.match(patron_mama_lesiones, linea) or
                re.match(patron_linea_tipo, linea) or
                re.match(patron_fecha, linea) or
                re.match(asterisco_pattern, linea)):
                lineas_filtradas.append(linea)
                continue

        #eliminamos caracteres especiales al inicio de la línea
        lineas_filtradas = [re.sub(r'^[\s*-]+[^a-zA-Z0-9*-]+|^(?:\*{1,3}(?=\s|$))', '', linea) for linea in lineas_filtradas]
        
        self.texto_procesado = lineas_filtradas

    def __tratar_casos_especiales(self):
        """
        Trata casos especiales en el texto procesado, incluyendo:
        - Patrón GPAC (g → p → c → a)
        - Líneas con múltiples datos separados por /, y, o . seguido de espacio
        - Un solo apartado de biología tumoral
        - Líneas que comienzan con "e — cmbm"
        - Asignar la clave diagnóstico a la línea que contiene no lo contiene
        - Otros casos especiales predefinidos
        """
        nuevo_texto = []
        for linea in self.texto_procesado:
            
            # Caso 2: Líneas que comienzan con "e — cmbm"
            if linea.startswith("e — cmbm"):
                nuevo_texto.append(linea.split("—", 1)[1].strip())
                continue
            
            # Caso 3: Separar líneas con múltiples patrones
            patrones = [
                # Patrón para fum: XXX * cirugías: YYY
                (r'(fum:\s*[^*]+)\s*\*\s*(cirugías:\s*.+)', 
                lambda m: [m.group(1).strip(), m.group(2).strip()]),
                
                # Patrón para aco: negado. mpf: otb (2005)
                (r'(aco:\s*negado)\.\s*(mpf:\s*otb\s*\(\d{4}\))', 
                lambda m: [m.group(1).strip(), m.group(2).strip()]),
                
                # Patrón para menarca XX años / fum XX años
                (r'(menarca\s+\d+\s*años)\s*/\s*(fum\s+\d+\s*años)', 
                lambda m: [m.group(1), m.group(2)]),
                
                # Patrón para menarca XX / fum XX.XX
                (r'(menarca\s+\d+)\s*/\s*(fum\s+[\d.]+)', 
                lambda m: [m.group(1), m.group(2)]),
                
                # Patrón para aco y trh negados (variantes)
                (r'(aco)\s*[:y]?\s*(trh)\s*[:]?\s*(negados?)', 
                lambda m: [f"{m.group(1)}: {m.group(3)}", f"{m.group(2)}: {m.group(3)}"]),
                
                (r'(aco)\s+y\s+(trh)\s+(negados?)', 
                lambda m: [f"{m.group(1)} {m.group(3)}", f"{m.group(2)} {m.group(3)}"]),
                
                # Patrón general para XX: AAA / YY: BBB
                (r'(\w+)\s*[:]\s*([^/]+)\s*[/]\s*(\w+)\s*[:]\s*([^/]+)', 
                lambda m: [f"{m.group(1)}: {m.group(2)}", f"{m.group(3)}: {m.group(4)}"])
            ]
            
            dividido = False
            for patron, handler in patrones:
                match = re.search(patron, linea, re.IGNORECASE)
                if match:
                    nuevo_texto.extend(handler(match))
                    dividido = True
                    break
            
            if dividido:
                continue
    
            
            # Caso 4: Patrón GPAC (g, p, c, a) en cualquier orden
            def ordenar_gpac(linea):
                # Verificar si la línea contiene un patrón GPAC válido delimitado correctamente
                patron_gpac = re.compile(
                    r'\b(?:g\s*\d+\s*p\s*\d+\s*c\s*\d+\s*a\s*\d+|p\s*\d+\s*g\s*\d+\s*a\s*\d+\s*c\s*\d+|c\s*\d+\s*a\s*\d+\s*g\s*\d+\s*p\s*\d+|a\s*\d+\s*c\s*\d+\s*p\s*\d+\s*g\s*\d+)\b',
                    re.IGNORECASE
                )
                match = patron_gpac.search(linea)
                if match:
                    # Extraer el patrón GPAC encontrado
                    gpac = match.group(0)
                    # Extraer los valores de g, p, c, a y ordenarlos
                    g = re.search(r'g\s*(\d+)', gpac, re.IGNORECASE)
                    p = re.search(r'p\s*(\d+)', gpac, re.IGNORECASE)
                    c = re.search(r'c\s*(\d+)', gpac, re.IGNORECASE)
                    a = re.search(r'a\s*(\d+)', gpac, re.IGNORECASE)
            
                    if all([g, p, c, a]):
                        # Reemplazar el patrón GPAC en la línea original con el ordenado
                        gpac_ordenado = f"g{g.group(1)} p{p.group(1)} c{c.group(1)} a{a.group(1)}"
                        return linea.replace(gpac, gpac_ordenado)
                return linea
            
            linea_ordenada = ordenar_gpac(linea)
            if linea_ordenada != linea:
                nuevo_texto.append(linea_ordenada)
            else:
                nuevo_texto.append(linea)
        
        self.texto_procesado = nuevo_texto
        # self.imprimir_datos()        
        
    def obtener_texto_procesado(self):
        """
        Devuelve el texto procesado como una lista de líneas.

        Returns:
            list: Lista de líneas del texto procesado.
        """
        return self.texto_procesado

    def imprimir_datos(self):
        """
        Imprime el contenido del texto procesado línea por línea.
        """
        for linea in self.texto_procesado:
            print(linea)
    
    def __setNombreArchivo(self, nombreArchivo):
        self.nombreArchivo = nombreArchivo

    def limpiar_archivo(self, ruta_archivo):
        """
        Carga un archivo de texto, lo limpia y procesa, y devuelve el texto procesado.
        Pero primero, restaura la instancia a su estado original.

        Args:
            ruta_archivo (str): La ruta del archivo de texto a procesar.
        """
        if not os.path.exists(ruta_archivo):
            raise FileNotFoundError(f"El archivo {ruta_archivo} no existe.")

        self.__restaurar_instancia()
        self.__setNombreArchivo(ruta_archivo)
        self.__cargar_datos()

        self.__unir_lineas_relevantes()
        self.__filtrar_lineas_relevantes()
        self.__tratar_casos_especiales()
        return self.obtener_texto_procesado()