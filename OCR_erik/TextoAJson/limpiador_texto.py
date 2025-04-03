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

    def __preprocesar_texto(self):
        """
        Procesa el texto, segmentándolo en claves y valores según palabras clave conocidas.
        """
        # Lista de claves que indican el inicio de una nueva sección en el texto
        claves = [
            "diagnóstico", "edad", "sexo", "peso", "talla", "preferencia", 
            "índice tabáquico", "tabaquismo", "tabaco", "alcohol", "drogas", 
            "comorbilidades", "antecedentes ginecológicos", "menarca", "embarazos", 
            "partos", "fum", "trh", "estado hormonal", "métodos anticonceptivos", 
            "cirugías", "originaria y residente", "seguridad social", "ocupación", 
            "ahf", "resumen del", "extensión del tumor", "biología tumoral",
            "aco", "mpf"
        ]
        patron_gn_pn_cn_an = r'[-\s]*\bg\d+\s*p\d+\s*c\d+\s*a\d+\b'
        patron_fecha = r'\b\d{1,2}\.\d{1,2}\.\d{2}|\b\d{1,2}\.\d{4}' 
        patron_lista_numerada = r'^\d+\.\s'  # Patrón para detectar líneas numeradas (ej: "1. cáncer de mama")
        patron_vineta = r'^-\s'  # Patrón para detectar líneas con viñetas (ej: "- Tia materna con cáncer de páncreas")

        clave_actual = None  # Almacena la clave en procesamiento
        valor_actual = []  # Acumula el valor correspondiente a la clave actual

        for linea in self.informacion:
            try:
                # Determina si la línea es una clave basándose en la lista de claves o si es una fecha
                es_clave = any(clave in linea for clave in claves) or re.match(patron_fecha, linea) or re.match(patron_gn_pn_cn_an, linea)

                es_lista_numerada = re.match(patron_lista_numerada, linea)  # Detecta si es una línea numerada
                es_vineta = re.match(patron_vineta, linea)  # Detecta si es una línea con viñeta

                # Verificar si la línea con viñeta contiene palabras clave
                if es_vineta and any(clave in linea for clave in claves):
                    es_clave = True  # Tratar como una línea independiente

                if es_clave and not es_lista_numerada:
                    # Si hay una clave en proceso, guarda la clave anterior con su valor acumulado
                    if clave_actual:
                        self.texto_procesado.append(f"{clave_actual} {' '.join(valor_actual).strip()}")
                        clave_actual = None
                        valor_actual = []
            
                    # Si la línea contiene una clave, se trata como una línea individual
                    clave_actual = linea
                    valor_actual = []  # Reinicia el valor actual
                elif clave_actual:
                    # Si estamos procesando una clave, acumulamos el valor
                    valor_actual.append(linea)
                else:
                    # Si no hay clave en proceso, se añade la línea tal cual
                    self.texto_procesado.append(linea)
            
            except Exception as e:
                raise ValueError(f"Error procesando la línea: {linea}. Error: {str(e)}")

        # Asegurarse de que la última clave se guarde
        if clave_actual:
            self.texto_procesado.append(f"{clave_actual} {' '.join(valor_actual).strip()}")

        # Elimina ':' innecesarios al final de cada línea
        self.texto_procesado = [re.sub(r'[:\s]+$', '', linea) for linea in self.texto_procesado]
    
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
            "ahf", "extensión del tumor", "biología tumoral",
            "aco", "mpf", "cáncer de mama bilateral"
        ]

        # Claves que pueden aparecer en cualquier parte de la línea como palabras individuales
        claves_palabras = ["menarca", "embarazos", "partos", "fum", "trh", "aco", "mpf"]

        # Patrones adicionales a conservar
        patron_gn_pn_cn_an = re.compile(r'[-\s]*\bg\d+\s*p\d+\s*a\d+\s*c\d+\b.*|g\d+p\d+c\d+a\d+', re.IGNORECASE)
        patron_lista_numerada = r'^\d+\.\s'  # Patrón para detectar líneas numeradas (ej: "1. cáncer de mama")
        patron_vineta = r'^-\s'  # Patrón para detectar líneas con viñetas (ej: "- Tia materna con cáncer de páncreas")
        patron_linea_tipo = r'^[^/]+ / \d+ / \d+ años / .+$'  # Patrón para detectar líneas del tipo "GACNC / 84959 / 67 años / Dra. Martínez"
        patron_mama_lesiones = re.compile(r'\bmama\s*(izquierda|derecha|bilateral)\s*con.*lesi.*', re.IGNORECASE)

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
                re.match(patron_linea_tipo, linea)):
                lineas_filtradas.append(linea)
                continue

        #eliminamos caracteres especiales al inicio de la línea
        lineas_filtradas = [re.sub(r'^[\s*-]+[^a-zA-Z0-9*-]+|^(?:\*{1,3}(?=\s|$))', '', linea) for linea in lineas_filtradas]
        
        self.texto_procesado = lineas_filtradas

    def __unir_lineas_relevantes(self):
        """
        Une las líneas relevantes cuando sea necesario y deja otras líneas individuales.
        """

        claves_inicio = [
            "diagnóstico", "edad", "sexo", "peso", "talla", "preferencia", 
            "índice tabáquico", "tabaquismo", "tabaco", "alcohol", "drogas", 
            "comorbilidades", "antecedentes ginecológicos", "menarca", "embarazos", 
            "partos", "fum", "trh", "estado hormonal", "métodos anticonceptivos", 
            "cirugías", "originaria y residente", "seguridad social", "ocupación", 
            "ahf", "resumen del", "extensión del tumor", "biología tumoral",
            "aco", "mpf", "eco", "mama izquierda", "mama derecha", "cáncer de mama bilateral"
        ]

        # Claves que deben tratarse como líneas individuales
        claves_palabras = {"menarca", "embarazos", "partos", "fum", "trh", "aco", "mpf", "métodos" }

        # Patrones que se consideran claves
        patron_gn_pn_cn_an = re.compile(r'[-\s]*\bg\d+\s*p\d+\s*a\d+\s*c\d+\b.*|g\d+p\d+c\d+a\d+', re.IGNORECASE)
        patron_fecha = re.compile(r'\b\d{1,2}\.\d{1,2}\.\d{2}|\b\d{1,2}\.\d{4}')
        patron_linea_tipo = re.compile(r'^[^/]+ / \d+ / \d+ años / .+$')  # Patrón para detectar líneas del tipo "GACNC / 84959 / 67 años / Dra. Martínez"

        lineas_procesadas = []
        clave_actual = None
        valor_actual = []
        en_biologia_o_extension = False  # Bandera para identificar si estamos en "Biología tumoral" o "Extensión del tumor"

        for linea in self.informacion:
            linea = linea.strip()

            # Verificar si la línea es una clave de inicio
            es_clave_inicio = any(linea.startswith(clave) for clave in claves_inicio)
            es_clave_palabra = any(palabra in linea.split() for palabra in claves_palabras)
            es_patron = patron_gn_pn_cn_an.match(linea) or patron_fecha.match(linea) or patron_linea_tipo.match(linea)

            # Detectar inicio de "Extensión del tumor" o "Biología tumoral"
            if linea.startswith("extensión del tumor") or linea.startswith("biología tumoral"):
                if clave_actual:
                    lineas_procesadas.append(f"{clave_actual} {' '.join(valor_actual).strip()}")
                clave_actual = linea
                valor_actual = []
                en_biologia_o_extension = True
                continue

            # Si estamos en "Biología tumoral" o "Extensión del tumor", seguir concatenando hasta que aparezca otra clave de inicio
            if en_biologia_o_extension:
                if any(linea.startswith(clave) for clave in claves_inicio if clave not in ["mama derecha", "mama izquierda"]):  # Si encontramos otra clave de inicio, cerramos el bloque
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
    
    def __tratar_casos_especiales(self):
        """
        Trata casos especiales en el texto procesado, incluyendo el patrón GPAC 
        en el orden específico: g → p → c → a.
        """
        for i, linea in enumerate(self.texto_procesado):
            # Caso 1: Biología tumoral
            if "biología tumoral" in linea and 'final' in linea:
                self.texto_procesado[i] = f"biología tumoral{linea.split('final', 1)[1].strip()}"
            
            # Caso 2: Líneas que comienzan con "e — cmbm"
            elif linea.lower().startswith("e — cmbm"):
                self.texto_procesado[i] = linea.split("—", 1)[1].strip()

            # Caso 3: Patrón GPAC (g, p, c, a) en cualquier orden
            else:
                def ordenar_gpac(linea):
                    # Extrae componentes en cualquier orden
                    g = re.search(r'g(\d+)', linea)
                    p = re.search(r'p(\d+)', linea)
                    c = re.search(r'c(\d+)', linea)
                    a = re.search(r'a(\d+)', linea)
                    
                    # Reconstruye en el orden g → p → c → a
                    if all([g, p, c, a]):
                        return f"g{g.group(1)} p{p.group(1)} c{c.group(1)} a{a.group(1)}"
                    return linea  # Si no hay 4 componentes, devuelve original

                linea_ordenada = ordenar_gpac(linea)
                if linea_ordenada != linea:
                    self.texto_procesado[i] = linea_ordenada
    
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
        for linea in self.informacion:
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
        # self.__preprocesar_texto()
        self.__unir_lineas_relevantes()
        self.__filtrar_lineas_relevantes()
        self.__tratar_casos_especiales()
        return self.obtener_texto_procesado()