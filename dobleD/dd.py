import json
import re
import os
import glob
import requests
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

    def formatear_texto(self):
        """
        Reformatea el contenido de self.informacion para que las líneas de texto
        aparezcan en el formato: ["vmv / 144923 / 65 años / dra. verduzco  \n"].
        """
        self.informacion = [
            f"{linea.strip()}  \n"
            for linea in self.informacion
            if linea.strip()  # Filtra líneas vacías
        ]

    def preguta_dd(self):
        try:

            contexto = "\n".join(self.informacion)
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": "Bearer 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",
                    "Content-Type": "application/json",
                },
                data=json.dumps({
                    "model": "deepseek/deepseek-chat-v3-0324:free",
                    "messages": [
                        {
                            "role": "user",
                            "content": (
                                f"A continuación se proporciona información médica estructurada:\n"
                                f"{contexto}\n\n"
                                "\nConsidera que la informacion de centros tumorales, \n"
                                "nódulos, metástasis vienen en el diagnóstico,en la extensión tumroal, o en la biología tumoral y que \n" 
                                "se puede representar como t1c o como t3 o ct3 o n0 o m0, entre otras combinaciones pero nosotros solo requeremos la parte de t,n,m que seria la t o la n o la m acompañada de numeros. Ademas, las comorbilidades \n"
                                "podrias separarlas por la fecha que indican. y para que tengas mas contexto, el g, p, c, a indican las \n"
                                "gestaciones, los partos, las cesáreas y los abortos. el aco indica Anticonceptivos Orales. \n" 
                                "La mama afectada aparece en el diagnóstico, en la extensión tumoral o en la biología tumoral, si la encuentras en esas secciones, ya no busques mas la mama. pero en caso que no se encuentre ahi\n"
                                "se puede encontrar la mama afectada en otras lineas como de cirugias tal vez, puedes poner la informacion de mama izquierda o mama derecha o ambas en caso de el cancer bilateral. \n"
                                "los antecedentes familiares oheredofamiliares considera laterales como tios, primos o hermanos; la ascendencia son padres, abuelos; la descendencia son hijos\n"
                                "Ahora por favor rellena el diccionario (el xxxx que esta en comorbilidades indica numeros o mas bien fechas): \n"
                                "{\n"
                                "Por favor, responde con un JSON que tenga la siguiente estructura y llena los campos con la información correspondiente:\n"
                                "{\n"
                                "    \"antecedentes_personales\": {\n"
                                "        \"edad\": {},\n"
                                "        \"sexo\": \"\",\n"
                                "        \"peso\": null,\n"
                                "        \"talla\": null,\n"
                                "        \"preferencia\": null,\n"
                                "        \"índice_tabáquico\": {\n"
                                "            \"fuma\": \"\",\n"
                                "            \"observaciones\": []\n"
                                "        },\n"
                                "        \"alcohol\": \"\",\n"
                                "        \"drogas\": \"\",\n"
                                "        \"comorbilidades\": {\n"
                                "            \"sin_fecha\": [],\n"
                                "            \"xxxx\": \"\"\n"
                                "        },\n"
                                "        \"antecedentes_ginecológicos\": {\n"
                                "            \"fum\": {},\n"
                                "            \"menarca\": {},\n"
                                "            \"trh\": \"\",\n"
                                "            \"aco\": \"\",\n"
                                "            \"mpf\": null,\n"
                                "            \"estado_hormonal\": \"\",\n"
                                "            \"métodos_anticonceptivos\": null,\n"
                                "            \"g\": 0,\n"
                                "            \"p\": 0,\n"
                                "            \"c\": 0,\n"
                                "            \"a\": 0\n"
                                "        }\n"
                                "    },\n"
                                "    \"antecedentes_familiares\": {\n"
                                "        \"ascendencia\": [],\n"
                                "        \"lateralidad\": [],\n"
                                "        \"descendencia\": []\n"
                                "    },\n"
                                "    \"estadía_tumoral\": {\n"
                                "        \"mama_izquierda\": {\n"
                                "            \"ultrasonido\": null,\n"
                                "            \"mastografía\": null,\n"
                                "            \"centros_tumorales\": null,\n"
                                "            \"nódulos\": null,\n"
                                "            \"metástasis\": null\n"
                                "        },\n"
                                "        \"mama_derecha\": {\n"
                                "            \"ultrasonido\": null,\n"
                                "            \"mastografía\": null,\n"
                                "            \"centros_tumorales\": null,\n"
                                "            \"nódulos\": null,\n"
                                "            \"metástasis\": null\n"
                                "        }\n"
                                "    },\n"
                                "    \"inmunohistoquímica_tumoral\": {\n"
                                "        \"mama_izquierda\": {\n"
                                "            \"re\": null,\n"
                                "            \"rp\": null,\n"
                                "            \"her2\": null,\n"
                                "            \"ki67\": null,\n"
                                "            \"gh\": null\n"
                                "        },\n"
                                "        \"mama_derecha\": {\n"
                                "            \"re\": null,\n"
                                "            \"rp\": null,\n"
                                "            \"her2\": null,\n"
                                "            \"ki67\": null,\n"
                                "            \"gh\": null\n"
                                "        }\n"
                                "    },\n"
                                "    \"tipo\": {\n"
                                "        \"mama_izquierda\": {\n"
                                "            \"clasificación\": null,\n"
                                "            \"descripcion\": null\n"
                                "        },\n"
                                "        \"mama_derecha\": {\n"
                                "            \"clasificación\": null,\n"
                                "            \"descripcion\": null\n"
                                "        }\n"
                                "    }\n"
                                "}\n"
                            )
                        }
                    ],
                })
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                # Parsear la respuesta JSON
                response_data = response.json()
                # Extraer el contenido del mensaje
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    message_content = response_data["choices"][0]["message"]["content"]
                    print("Response (JSON):")
                    print(message_content)  # La IA debería devolver un JSON estructurado
                else:
                    print("No se encontró contenido en la respuesta.")
            else:
                print(f"Error en la respuesta: {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")

    def __extraer_nombre_txt(self):
        """
        Extrae el nombre del archivo de texto de la ruta de archivo.
        devuelve el nombre del archivo de texto
        """
        return os.path.basename(self.rutaTxt)
    
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
                
                self.formatear_texto()  # Formatea el texto de la fase actual
                self.imprimir_info()
                

                # for i, evolucion in enumerate(self.evoluciones, start=1):
                #     self.__crear_json(f"{self.nombre}_{idx}_{i}.json", evolucion)
                
                print('_________________________')
                # nombre_json_fase = f"{self.nombre}_{idx}.json"  # Ejemplo: 123_1.json, 123_2.json
                # self.__verificar_valores_nulos(ruta_destino, nombre_json_fase)
                # self.__crear_json(nombre_json_fase, self.data)

        else:
            self.formatear_texto()  # Formatea el texto completo
            self.imprimir_info()
            self.preguta_dd()
            # Solo un caso completo
            
            print('_________________________')

            # nombre_json = f"{self.nombre}.json"
            # self.__verificar_valores_nulos(ruta_destino, nombre_json)
            # self.__crear_json(nombre_json, self.data)

        self.__limpiar_instancia()

    def __limpiar_instancia(self):
            """
            Limpia el atributo "data" para evitar que se mezclen los datos de diferentes casos.
            Si parcial es True, limpia self.data y self.mama.
            """

            self.rutaTxt = None
            self.rutaDestino = None
            self.nombre = None
            self.informacion = []
            self.fases = []

    def imprimir_info(self):
        """
        Imprime las lineas que contenga el atributo "Información".
        """
        for linea in self.informacion:
            print(linea)

    def __crear_json(self, nombreJSON, diccionario):
        """
        Crea un archivo JSON con el atributo "data" que es un diccionario.

        Args:
            destino (str): Ruta del archivo JSON que se creará.
        """

        with open(os.path.join(self.rutaDestino, nombreJSON), 'w', encoding="utf-8") as file:
            json.dump(diccionario, file, indent=4, ensure_ascii=False)

procesador = TextoJson()

#Obtener todos los archivos .txt en la carpeta especificada
# ruta_txts = r'D:\DOCUMENTOS\VirtualEnvPy\dataScience\source\Servicio\OCR_erik\TextoAJson\probando\expedientes\*.txt'
# ruta_destino = r'D:\DOCUMENTOS\VirtualEnvPy\dataScience\source\Servicio\OCR_erik\TextoAJson\probando\jsons'

# for archivo_txt in glob.glob(ruta_txts):
#     procesador.convertir_txt_json(archivo_txt, ruta_destino)

# ruta_txts = r'/home/josuevj/Documents/uni/servicio/sources/OCR_erik/TextoAJson/probando/expedientes/*.txt'
# ruta_destino = r'/home/josuevj/Documents/uni/servicio/sources/OCR_erik/TextoAJson/probando/jsons'

# for archivo_txt in glob.glob(ruta_txts):
#     procesador.convertir_txt_json(archivo_txt, ruta_destino)

# procesador.convertir_txt_json(r'D:\DOCUMENTOS\VirtualEnvPy\dataScience\source\Servicio\OCR_erik\TextoAJson\nuevos_contetstos\expedientes\144923.txt', r'D:\DOCUMENTOS\VirtualEnvPy\dataScience\source\Servicio\OCR_erik\TextoAJson\nuevos_contetstos\jsons')
procesador.convertir_txt_json(r'/home/josuevj/Documents/uni/servicio/sources/dobleD/expedientes/83432 (LISTO).txt', r'/home/josuevj/Documents/uni/servicio/sources/dobleD/')