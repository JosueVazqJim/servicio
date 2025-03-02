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
                
                # Elimina caracteres especiales al inicio de la línea, excepto separadores con 4 o más asteriscos
                self.informacion = [
                    re.sub(r'^[\s]*[^a-zA-Z0-9*]+|^(?:\*{1,3}(?=\s|$))', '', linea)
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
            "ahf", "cáncer de", "resumen del", "extensión del tumor", "biología tumoral",
            "aco", "mpf", "eco"
        ]
        patron_gn_pn_cn_an = r'\bg\d+\s*p\d+\s*c\d+\s*a\d+\b'
        patron_fecha = r'\b\d{1,2}\.\d{1,2}\.\d{2}|\b\d{1,2}\.\d{4}' 

        clave_actual = None  # Almacena la clave en procesamiento
        valor_actual = []  # Acumula el valor correspondiente a la clave actual

        for linea in self.informacion:
            try:
                # Determina si la línea es una clave basándose en la lista de claves o si es una fecha
                es_clave = any(clave in linea for clave in claves) or re.match(patron_fecha, linea) or re.match(patron_gn_pn_cn_an, linea)
        
                if es_clave:
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
            self.texto_procesado.append(f"{clave_actual}: {' '.join(valor_actual).strip()}")

        # Elimina ':' innecesarios al final de cada línea
        self.texto_procesado = [re.sub(r'[:\s]+$', '', linea) for linea in self.texto_procesado]

    
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
        self.__preprocesar_texto()
        return self.obtener_texto_procesado()