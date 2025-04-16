import os
import pickle
import tempfile
import streamlit as st

def get_temp_dir():
    """
    Obtiene la ruta del directorio temporal para guardar archivos.
    Crea el directorio si no existe.
    
    Returns:
        str: Ruta del directorio temporal
    """
    # Usar un subdirectorio en el directorio temporal del sistema
    temp_dir = os.path.join(tempfile.gettempdir(), "yachay_wasi_match")
    
    # Crear el directorio si no existe
    os.makedirs(temp_dir, exist_ok=True)
    
    return temp_dir

def get_temp_files():
    """
    Obtiene la lista de archivos en el directorio temporal.
    
    Returns:
        list: Lista de nombres de archivos en el directorio temporal
    """
    temp_dir = get_temp_dir()
    
    # Obtener la lista de archivos si el directorio existe
    if os.path.exists(temp_dir):
        return os.listdir(temp_dir)
    
    return []

def save_data(data, filename):
    """
    Guarda datos en un archivo pickle en el directorio temporal.
    
    Args:
        data: Datos a guardar (cualquier objeto serializable)
        filename (str): Nombre del archivo (sin ruta)
        
    Returns:
        bool: True si se guardó correctamente, False en caso contrario
    """
    try:
        # Obtener ruta completa
        file_path = os.path.join(get_temp_dir(), filename)
        
        # Guardar datos
        with open(file_path, 'wb') as f:
            pickle.dump(data, f)
        
        return True
    except Exception as e:
        st.error(f"Error al guardar datos: {str(e)}")
        return False

def load_data(filename):
    """
    Carga datos desde un archivo pickle en el directorio temporal.
    
    Args:
        filename (str): Nombre del archivo (sin ruta)
        
    Returns:
        object: Datos cargados, o None si hay error
    """
    try:
        # Obtener ruta completa
        file_path = os.path.join(get_temp_dir(), filename)
        
        # Verificar si el archivo existe
        if not os.path.exists(file_path):
            return None
        
        # Cargar datos
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
        
        return data
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")
        return None 