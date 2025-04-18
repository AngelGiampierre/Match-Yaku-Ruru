"""
Funciones para la carga y guardado de archivos en el preprocesamiento.

Este módulo proporciona funciones para leer y escribir archivos en diferentes
formatos (Excel, CSV) y detectar automáticamente tipos de archivos.
"""

import os
import pandas as pd
import streamlit as st
from typing import Union, Optional, Tuple, Dict, List, Any
import io
import tempfile
from datetime import datetime


def detect_file_type(file_name: str) -> str:
    """
    Detecta el tipo de archivo basado en su extensión.
    
    Args:
        file_name: Nombre del archivo con extensión
        
    Returns:
        Tipo de archivo ('excel', 'csv' o 'desconocido')
    """
    ext = os.path.splitext(file_name)[1].lower()
    if ext in ['.xlsx', '.xls']:
        return 'excel'
    elif ext == '.csv':
        return 'csv'
    else:
        return 'desconocido'


def read_file(uploaded_file: Any) -> Tuple[pd.DataFrame, str, Optional[str]]:
    """
    Lee un archivo subido (Excel o CSV) y lo convierte a DataFrame.
    
    Args:
        uploaded_file: Archivo subido a través de st.file_uploader
        
    Returns:
        Tupla con (DataFrame, tipo_archivo, mensaje_error)
        Si hay error, DataFrame será None y mensaje_error contendrá el error
    """
    if uploaded_file is None:
        return None, None, "No se ha subido ningún archivo"
    
    try:
        file_type = detect_file_type(uploaded_file.name)
        
        if file_type == 'excel':
            df = pd.read_excel(uploaded_file)
            return df, file_type, None
        elif file_type == 'csv':
            df = pd.read_csv(uploaded_file)
            return df, file_type, None
        else:
            return None, file_type, f"Formato de archivo no soportado: {uploaded_file.name}"
    except Exception as e:
        return None, None, f"Error al leer el archivo: {str(e)}"


def save_excel(df: pd.DataFrame, file_name: Optional[str] = None) -> Tuple[bool, bytes, str]:
    """
    Guarda un DataFrame como archivo Excel y devuelve los bytes para descarga.
    
    Args:
        df: DataFrame a guardar
        file_name: Nombre base del archivo (sin extensión)
        
    Returns:
        Tupla con (éxito, bytes_del_archivo, nombre_archivo)
    """
    try:
        if file_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"datos_procesados_{timestamp}"
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Datos')
        
        return True, output.getvalue(), f"{file_name}.xlsx"
    except Exception as e:
        st.error(f"Error al guardar el archivo Excel: {str(e)}")
        return False, None, None


def save_csv(df: pd.DataFrame, file_name: Optional[str] = None) -> Tuple[bool, str, str]:
    """
    Guarda un DataFrame como archivo CSV y devuelve los datos para descarga.
    
    Args:
        df: DataFrame a guardar
        file_name: Nombre base del archivo (sin extensión)
        
    Returns:
        Tupla con (éxito, datos_csv, nombre_archivo)
    """
    try:
        if file_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"datos_procesados_{timestamp}"
        
        csv_data = df.to_csv(index=False)
        return True, csv_data, f"{file_name}.csv"
    except Exception as e:
        st.error(f"Error al guardar el archivo CSV: {str(e)}")
        return False, None, None


def save_temp_file(df: pd.DataFrame, file_name: str) -> str:
    """
    Guarda un DataFrame como archivo temporal.
    
    Args:
        df: DataFrame a guardar
        file_name: Nombre del archivo temporal (sin extensión)
        
    Returns:
        Ruta al archivo temporal guardado
    """
    try:
        # Crear directorio temporal si no existe
        temp_dir = os.path.join(tempfile.gettempdir(), 'match_yaku_ruru')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Crear ruta completa
        file_path = os.path.join(temp_dir, f"{file_name}.pkl")
        
        # Guardar DataFrame
        df.to_pickle(file_path)
        
        return file_path
    except Exception as e:
        st.error(f"Error al guardar archivo temporal: {str(e)}")
        return None


def load_temp_file(file_name: str) -> Optional[pd.DataFrame]:
    """
    Carga un DataFrame desde un archivo temporal.
    
    Args:
        file_name: Nombre del archivo temporal (sin extensión)
        
    Returns:
        DataFrame cargado o None si hay error
    """
    try:
        # Obtener ruta completa
        temp_dir = os.path.join(tempfile.gettempdir(), 'match_yaku_ruru')
        file_path = os.path.join(temp_dir, f"{file_name}.pkl")
        
        # Verificar si existe
        if not os.path.exists(file_path):
            return None
        
        # Cargar DataFrame
        df = pd.read_pickle(file_path)
        return df
    except Exception as e:
        st.error(f"Error al cargar archivo temporal: {str(e)}")
        return None 