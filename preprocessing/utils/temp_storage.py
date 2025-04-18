"""
Funciones para el almacenamiento temporal de datos entre tabs.

Este módulo proporciona funciones para guardar y recuperar datos temporales
que deben ser compartidos entre diferentes tabs o sesiones.
"""

import os
import pandas as pd
import streamlit as st
import pickle
import tempfile
from datetime import datetime
from typing import Any, Optional, Dict, List, Tuple


def get_temp_dir() -> str:
    """
    Obtiene el directorio temporal para guardar archivos, creándolo si no existe.
    
    Returns:
        Ruta al directorio temporal
    """
    temp_dir = os.path.join(tempfile.gettempdir(), 'match_yaku_ruru')
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir


def save_data(data: Any, key: str) -> bool:
    """
    Guarda datos temporales para uso entre tabs o sesiones.
    
    Args:
        data: Datos a guardar (cualquier objeto serializable)
        key: Clave única para identificar los datos
        
    Returns:
        True si el guardado fue exitoso, False en caso contrario
    """
    try:
        # Obtener directorio temporal
        temp_dir = get_temp_dir()
        
        # Crear ruta completa del archivo
        file_path = os.path.join(temp_dir, f"{key}.pkl")
        
        # Guardar datos usando pickle
        with open(file_path, 'wb') as f:
            pickle.dump(data, f)
        
        return True
    except Exception as e:
        st.error(f"Error al guardar datos temporales: {str(e)}")
        return False


def load_data(key: str) -> Optional[Any]:
    """
    Carga datos temporales previamente guardados.
    
    Args:
        key: Clave única que identifica los datos
        
    Returns:
        Datos cargados o None si no se encuentran o hay error
    """
    try:
        # Obtener directorio temporal
        temp_dir = get_temp_dir()
        
        # Crear ruta completa del archivo
        file_path = os.path.join(temp_dir, f"{key}.pkl")
        
        # Verificar si el archivo existe
        if not os.path.exists(file_path):
            return None
        
        # Cargar datos usando pickle
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
        
        return data
    except Exception as e:
        st.error(f"Error al cargar datos temporales: {str(e)}")
        return None


def list_temp_files() -> List[Dict[str, Any]]:
    """
    Lista todos los archivos temporales disponibles.
    
    Returns:
        Lista de diccionarios con información de los archivos
    """
    try:
        # Obtener directorio temporal
        temp_dir = get_temp_dir()
        
        # Listar archivos
        files = []
        
        for filename in os.listdir(temp_dir):
            if filename.endswith('.pkl'):
                file_path = os.path.join(temp_dir, filename)
                
                # Obtener estadísticas del archivo
                stats = os.stat(file_path)
                
                # Obtener fecha de modificación
                mod_time = datetime.fromtimestamp(stats.st_mtime)
                
                # Obtener tamaño
                size_kb = stats.st_size / 1024  # Convertir a KB
                
                # Intentar determinar el tipo de datos
                data_type = "Desconocido"
                try:
                    with open(file_path, 'rb') as f:
                        data = pickle.load(f)
                        
                        if isinstance(data, pd.DataFrame):
                            data_type = f"DataFrame ({data.shape[0]} filas x {data.shape[1]} columnas)"
                        else:
                            data_type = type(data).__name__
                except:
                    pass
                
                # Agregar a la lista
                files.append({
                    'name': filename.replace('.pkl', ''),
                    'path': file_path,
                    'size': f"{size_kb:.2f} KB",
                    'modified': mod_time.strftime("%Y-%m-%d %H:%M:%S"),
                    'type': data_type
                })
        
        return files
    except Exception as e:
        st.error(f"Error al listar archivos temporales: {str(e)}")
        return []


def delete_temp_file(key: str) -> bool:
    """
    Elimina un archivo temporal.
    
    Args:
        key: Clave única que identifica el archivo
        
    Returns:
        True si la eliminación fue exitosa, False en caso contrario
    """
    try:
        # Obtener directorio temporal
        temp_dir = get_temp_dir()
        
        # Crear ruta completa del archivo
        file_path = os.path.join(temp_dir, f"{key}.pkl")
        
        # Verificar si el archivo existe
        if not os.path.exists(file_path):
            return False
        
        # Eliminar archivo
        os.remove(file_path)
        return True
    except Exception as e:
        st.error(f"Error al eliminar archivo temporal: {str(e)}")
        return False 