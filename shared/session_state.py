"""
Gestión del estado de sesión entre módulos.

Este módulo proporciona funciones para compartir datos entre diferentes
módulos de la aplicación utilizando el st.session_state de Streamlit.
"""

import streamlit as st
from typing import Any, Optional, Dict


def get_value(key: str, default: Any = None) -> Any:
    """
    Obtiene un valor del estado de sesión.
    
    Args:
        key: Clave única del valor
        default: Valor por defecto si no existe
        
    Returns:
        Valor almacenado o default si no existe
    """
    return st.session_state.get(key, default)


def set_value(key: str, value: Any) -> None:
    """
    Guarda un valor en el estado de sesión.
    
    Args:
        key: Clave única para el valor
        value: Valor a guardar
    """
    st.session_state[key] = value


def delete_value(key: str) -> bool:
    """
    Elimina un valor del estado de sesión.
    
    Args:
        key: Clave única del valor
        
    Returns:
        True si se eliminó correctamente, False si no existía
    """
    if key in st.session_state:
        del st.session_state[key]
        return True
    return False


def has_value(key: str) -> bool:
    """
    Verifica si una clave existe en el estado de sesión.
    
    Args:
        key: Clave a verificar
        
    Returns:
        True si la clave existe, False de lo contrario
    """
    return key in st.session_state


def get_all_values() -> Dict[str, Any]:
    """
    Obtiene todos los valores del estado de sesión.
    
    Returns:
        Diccionario con todos los valores almacenados
    """
    return dict(st.session_state)


def clear_all_values() -> None:
    """
    Elimina todos los valores del estado de sesión.
    """
    for key in list(st.session_state.keys()):
        del st.session_state[key] 