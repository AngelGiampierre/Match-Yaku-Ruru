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
from .tabs.update_match_results_tab import update_match_results_tab

# Mapeo de nombres de tabs a funciones
# (Añadir el nuevo tab al final o donde prefieras)
TAB_MAP = {
    "Selección de Columnas": column_selection_tab,
    "Validación DNI/Correo": dni_validation_tab,
    "Filtrado por Área/ID": filter_area_tab,
    "Estandarización Rurus": ruru_standardization_tab,
    "Transformación Rurus": ruru_transform_tab,
    "Actualizar Resultados Match": update_match_results_tab, # <-- Nuevo Tab
}

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
    
    # Crear pestañas usando st.tabs
    tab_names = list(TAB_MAP.keys())
    tabs = st.tabs(tab_names)
    
    # Renderizar el contenido de cada tab
    for i, tab_name in enumerate(tab_names):
        with tabs[i]:
            # Llamar a la función correspondiente al tab
            tab_function = TAB_MAP[tab_name]
            tab_function()


if __name__ == "__main__":
    # Esto permite ejecutar este módulo directamente para pruebas
    preprocessing_page() 