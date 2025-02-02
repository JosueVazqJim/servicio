import re
import os

class LimpiezaTexto:
    def __init__(self, nombreArchivo):
        self.nombreArchivo = nombreArchivo
        self.informacion = []  # Almacena el contenido del archivo después de la limpieza inicial
        self.texto_procesado = []  # Contendrá el texto final procesado

        self._cargar_datos()  # Cargar y limpiar los datos del archivo
        self._preprocesar_texto()  # Procesar el contenido para estructurarlo correctamente

    def _cargar_datos(self):
        """Carga el archivo de texto, eliminando líneas vacías y convirtiendo a minúsculas."""
        if not os.path.exists(self.nombreArchivo):
            raise FileNotFoundError(f"El archivo {self.nombreArchivo} no existe.")

        with open(self.nombreArchivo, 'r', encoding='utf-8') as file:
            # Elimina líneas vacías y convierte el texto a minúsculas
            self.informacion = [linea.strip() for linea in file if linea.strip()]
            
            # Elimina caracteres especiales al inicio de la línea
            self.informacion = [re.sub(r'^[\s]*[^a-zA-Z0-9]+', '', linea) for linea in self.informacion]

    def _preprocesar_texto(self):
        """Procesa el texto, segmentándolo en claves y valores según palabras clave conocidas."""
        # Lista de claves que indican el inicio de una nueva sección en el texto
        claves = [
            "diagnóstico", "edad", "sexo", "peso", "talla", "preferencia", 
            "índice tabáquico", "tabaquismo", "tabaco", "alcohol", "drogas", 
            "comorbilidades", "antecedentes ginecológicos", "menarca", "embarazos", 
            "partos", "fum", "trh", "estado hormonal", "métodos anticonceptivos", 
            "cirugías", "originaria y residente", "seguridad social", "ocupación", 
            "ahf", "g0 p0 c0 a0", "cáncer de", "resumen del", "extensión del tumor", "biología tumoral"
        ]

        # Patrón regex para detectar fechas en formato DD.MM.AA o tambien MM.AAAA
        patron_fecha = r'\b\d{1,2}\.\d{1,2}\.\d{2}|\b\d{1,2}\.\d{4}' 

        clave_actual = None  # Almacena la clave en procesamiento
        valor_actual = []  # Acumula el valor correspondiente a la clave actual

        for linea in self.informacion:
            # Determina si la línea es una clave basándose en la lista de claves o si es una fecha
            es_clave = any(linea.lower().startswith(clave) for clave in claves) or re.match(patron_fecha, linea)

            if es_clave:
                # Si hay una clave en proceso, guarda la clave anterior con su valor acumulado
                if clave_actual:
                    self.texto_procesado.append(f"{clave_actual}: {' '.join(valor_actual).strip()}")

                # Divide la línea en clave y valor si tiene ':'; si no, la línea completa es la clave
                clave_actual, valor = re.split(r':\s*', linea, maxsplit=1) if ':' in linea else (linea, "")
                valor_actual = [valor] if valor else []  # Inicializa el valor actual
            elif clave_actual:
                # Si la línea no es una clave, se acumula como parte del valor de la clave actual
                valor_actual.append(linea)
            else:
                # Si no hay una clave en curso, se agrega la línea tal cual
                self.texto_procesado.append(linea)

        # Guarda la última clave en proceso si quedó pendiente
        if clave_actual:
            self.texto_procesado.append(f"{clave_actual}: {' '.join(valor_actual).strip()}")

        # Elimina ':' innecesarios al final de cada línea
        self.texto_procesado = [re.sub(r'[:\s]+$', '', linea) for linea in self.texto_procesado]

    def obtener_texto_procesado(self):
        """Devuelve el texto procesado como una lista de líneas."""
        return self.texto_procesado

    def imprimir_datos(self):
        """Imprime el contenido del texto procesado línea por línea."""
        print('\n'.join(self.texto_procesado))

