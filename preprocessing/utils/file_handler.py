"""
Utilidades para manejo de archivos.

Funciones para guardar y cargar archivos temporales durante el procesamiento.
"""

import os
import pandas as pd
import tempfile
import uuid
from datetime import datetime


def get_temp_dir():
    """
    Obtiene el directorio temporal para archivos de la aplicación.
    
    Returns:
        str: Ruta al directorio temporal
    """
    # Crear directorio temporal para la aplicación si no existe
    temp_dir = os.path.join(tempfile.gettempdir(), "yachay-match")
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir


def get_temp_file_path(prefix="data", extension="xlsx"):
    """
    Genera una ruta temporal para guardar un archivo.
    
    Args:
        prefix (str): Prefijo para el nombre del archivo
        extension (str): Extensión del archivo (sin el punto)
        
    Returns:
        str: Ruta completa al archivo temporal
    """
    # Crear nombre único basado en timestamp y UUID
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    filename = f"{prefix}_{timestamp}_{unique_id}.{extension}"
    
    # Combinar con el directorio temporal
    return os.path.join(get_temp_dir(), filename)


def save_dataframe(df, prefix="data", extension="xlsx"):
    """
    Guarda un DataFrame en un archivo temporal.
    
    Args:
        df (pd.DataFrame): DataFrame a guardar
        prefix (str): Prefijo para el nombre del archivo
        extension (str): Formato del archivo ('xlsx' o 'csv')
        
    Returns:
        str: Ruta al archivo guardado o None si hay error
    """
    if df is None or df.empty:
        return None
    
    try:
        # Generar ruta del archivo
        file_path = get_temp_file_path(prefix, extension)
        
        # Guardar según formato
        if extension.lower() == 'xlsx':
            df.to_excel(file_path, index=False)
        elif extension.lower() == 'csv':
            df.to_csv(file_path, index=False)
        else:
            return None
        
        return file_path
    except Exception as e:
        print(f"Error al guardar DataFrame: {str(e)}")
        return None


def load_dataframe(file_path):
    """
    Carga un DataFrame desde un archivo.
    
    Args:
        file_path (str): Ruta al archivo a cargar
        
    Returns:
        pd.DataFrame: DataFrame cargado o None si hay error
    """
    if not file_path or not os.path.exists(file_path):
        return None
    
    try:
        # Determinar formato por extensión
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext in ['.xlsx', '.xls']:
            return pd.read_excel(file_path)
        elif ext == '.csv':
            return pd.read_csv(file_path)
        else:
            return None
    except Exception as e:
        print(f"Error al cargar DataFrame: {str(e)}")
        return None 