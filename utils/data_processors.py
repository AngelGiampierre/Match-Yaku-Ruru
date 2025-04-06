import pandas as pd
import re

def limpiar_texto(texto):
    """
    Limpia un texto eliminando espacios extras, normalizando mayúsculas/minúsculas
    y eliminando caracteres especiales.
    
    Args:
        texto (str): Texto a limpiar
        
    Returns:
        str: Texto limpio
    """
    if pd.isna(texto) or texto is None:
        return ""
    
    # Convertir a string si no lo es
    texto = str(texto)
    
    # Eliminar espacios en blanco al inicio y final
    texto = texto.strip()
    
    # Normalizar espacios múltiples
    texto = re.sub(r'\s+', ' ', texto)
    
    return texto

def formatear_lista(lista_texto, separador=","):
    """
    Convierte un texto con elementos separados por un separador en una lista limpia.
    
    Args:
        lista_texto (str): Texto con elementos separados
        separador (str): Separador de elementos (por defecto: coma)
        
    Returns:
        list: Lista de elementos limpios
    """
    if pd.isna(lista_texto) or lista_texto is None or lista_texto == "":
        return []
    
    # Convertir a string si no lo es
    lista_texto = str(lista_texto)
    
    # Dividir por el separador y limpiar cada elemento
    elementos = [limpiar_texto(elemento) for elemento in lista_texto.split(separador)]
    
    # Eliminar elementos vacíos
    elementos = [elemento for elemento in elementos if elemento]
    
    return elementos

def validar_correo(correo):
    """
    Valida si un correo electrónico tiene un formato válido.
    
    Args:
        correo (str): Correo electrónico a validar
        
    Returns:
        bool: True si el correo es válido, False en caso contrario
    """
    if pd.isna(correo) or correo is None or correo == "":
        return False
    
    # Patrón básico para validar correos
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(patron, str(correo)))

def validar_celular(celular):
    """
    Valida si un número de celular tiene un formato válido (solo dígitos).
    
    Args:
        celular (str): Número de celular a validar
        
    Returns:
        bool: True si el celular es válido, False en caso contrario
    """
    if pd.isna(celular) or celular is None or celular == "":
        return False
    
    # Convertir a string si no lo es
    celular = str(celular)
    
    # Eliminar espacios, guiones y paréntesis
    celular = re.sub(r'[\s\-\(\)]', '', celular)
    
    # Verificar que solo contenga dígitos
    return celular.isdigit()

def estandarizar_opciones(opcion, mapeo_opciones=None):
    """
    Estandariza los nombres de las opciones según un mapeo.
    
    Args:
        opcion (str): Nombre de la opción a estandarizar
        mapeo_opciones (dict): Diccionario de equivalencias {variante: nombre_estandar}
        
    Returns:
        str: Nombre estandarizado de la opción
    """
    if mapeo_opciones is None:
        # Diccionario de equivalencias por defecto
        mapeo_opciones = {
            # Arte y Cultura
            "musica": "Música",
            "música": "Música",
            "dibujo": "Dibujo y Pintura",
            "pintura": "Dibujo y Pintura",
            "dibujo y pintura": "Dibujo y Pintura",
            "cuenta": "Cuenta cuentos",
            "cuentos": "Cuenta cuentos",
            "cuenta cuentos": "Cuenta cuentos",
            "cuentacuentos": "Cuenta cuentos",
            "danza": "Danza",
            "baile": "Danza",
            "teatro": "Teatro",
            "actuación": "Teatro",
            "actuacion": "Teatro",
            
            # Asesoría a Colegios
            "mate": "Matemática",
            "matematica": "Matemática",
            "matemática": "Matemática",
            "comuni": "Comunicación",
            "comunicacion": "Comunicación",
            "comunicación": "Comunicación",
            "ingles": "Inglés",
            "inglés": "Inglés",
            "english": "Inglés",
            
            # Bienestar Psicológico
            "psico": "Facilitador psicoeducativo",
            "facilitador": "Facilitador psicoeducativo",
            "psicoeduca": "Facilitador psicoeducativo",
            "facilitador psicoeducativo": "Facilitador psicoeducativo"
        }
    
    if pd.isna(opcion) or opcion is None or opcion == "":
        return ""
    
    # Convertir a string si no lo es
    opcion = str(opcion).lower().strip()
    
    # Buscar la mejor coincidencia en el mapeo
    for variante, estandar in mapeo_opciones.items():
        if variante in opcion:
            return estandar
    
    # Si no hay coincidencia, devolver la opción original con primera letra en mayúscula
    return opcion.capitalize() 