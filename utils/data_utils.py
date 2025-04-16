import os
import pickle
import pandas as pd
import streamlit as st

def load_data(filename, default=None):
    """
    Carga datos desde un archivo pickle.
    
    Args:
        filename (str): Nombre del archivo pickle a cargar
        default: Valor a devolver si el archivo no existe
        
    Returns:
        object: Datos cargados o valor por defecto si no se encuentra el archivo
    """
    # Directorio para archivos temporales
    temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'temp')
    
    # Crear directorio temporal si no existe
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    file_path = os.path.join(temp_dir, filename)
    
    try:
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                return pickle.load(f)
        else:
            return default
    except Exception as e:
        st.error(f"Error al cargar los datos: {str(e)}")
        return default

def save_data(data, filename):
    """
    Guarda datos en un archivo pickle.
    
    Args:
        data (object): Datos a guardar
        filename (str): Nombre del archivo pickle
        
    Returns:
        bool: True si fue guardado exitosamente, False en caso contrario
    """
    # Directorio para archivos temporales
    temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'temp')
    
    # Crear directorio temporal si no existe
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    file_path = os.path.join(temp_dir, filename)
    
    try:
        with open(file_path, 'wb') as f:
            pickle.dump(data, f)
        return True
    except Exception as e:
        st.error(f"Error al guardar los datos: {str(e)}")
        return False

def get_temp_dir():
    """
    Obtiene la ruta del directorio temporal para archivos.
    
    Returns:
        str: Ruta al directorio temporal
    """
    temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'temp')
    
    # Crear directorio temporal si no existe
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    return temp_dir 