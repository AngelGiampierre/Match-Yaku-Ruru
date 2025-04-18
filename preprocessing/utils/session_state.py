"""
Funciones para manejar el estado de sesión en Streamlit.

Provee funciones para guardar y recuperar DataFrames y estados entre sesiones.
"""

import streamlit as st


def get_dataframe(key):
    """
    Obtiene un DataFrame del estado de sesión.
    
    Args:
        key (str): Clave para identificar el DataFrame
        
    Returns:
        pd.DataFrame: DataFrame guardado o None si no existe
    """
    return st.session_state.get(key)


def set_dataframe(df, key):
    """
    Guarda un DataFrame en el estado de sesión.
    
    Args:
        df (pd.DataFrame): DataFrame a guardar
        key (str): Clave para identificar el DataFrame
    """
    st.session_state[key] = df


def get_processing_step(step_name):
    """
    Verifica si un paso de procesamiento ha sido completado.
    
    Args:
        step_name (str): Nombre del paso de procesamiento
        
    Returns:
        bool: True si el paso está completado, False en caso contrario
    """
    key = f"step_{step_name}_completed"
    return st.session_state.get(key, False)


def set_processing_step(step_name, completed=True):
    """
    Marca un paso de procesamiento como completado o pendiente.
    
    Args:
        step_name (str): Nombre del paso de procesamiento
        completed (bool): Estado del paso (True=completado, False=pendiente)
    """
    key = f"step_{step_name}_completed"
    st.session_state[key] = completed 