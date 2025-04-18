"""
Módulo principal de preprocesamiento.

Este módulo integra todas las funcionalidades de preprocesamiento
y las expone mediante una interfaz de usuario con múltiples tabs.
"""

import streamlit as st
from typing import Dict, Any, Callable

# Importamos los tabs
from .tabs.column_selection_tab import column_selection_tab
from .tabs.dni_validation_tab import dni_validation_tab
from .tabs.filter_area_tab import filter_area_tab
from .tabs.ruru_standardization_tab import ruru_standardization_tab
from .tabs.ruru_transform_tab import ruru_transform_tab


def preprocessing_page():
    """
    Página principal del módulo de preprocesamiento.
    Integra todos los tabs en una interfaz coherente.
    """
    st.title("Preprocesamiento de Datos")
    st.write("""
    Esta sección te permite preparar los datos antes del proceso de matching.
    Selecciona una de las siguientes opciones para comenzar.
    """)
    
    # Definir tabs disponibles y sus funciones
    tabs = {
        "Selección de Columnas": column_selection_tab,
        "Validación de DNIs/Correos": dni_validation_tab,
        "Filtrado por Área": filter_area_tab,
        "Estandarización de Rurus": ruru_standardization_tab,
        "Transformación de Rurus": ruru_transform_tab
    }
    
    # Crear tabs en la interfaz
    tab_names = list(tabs.keys())
    tab_functions = list(tabs.values())
    
    # Usar st.tabs para crear los tabs
    selected_tabs = st.tabs(tab_names)
    
    # Ejecutar la función correspondiente a cada tab
    for i, tab in enumerate(selected_tabs):
        with tab:
            tab_functions[i]()


if __name__ == "__main__":
    # Esto permite ejecutar este módulo directamente para pruebas
    preprocessing_page() 