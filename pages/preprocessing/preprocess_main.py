import streamlit as st
import sys
import os

# Importar pestañas individuales
from pages.preprocessing.tabs.load_clean_tab import load_clean_tab
from pages.preprocessing.tabs.selection_area_tab import selection_area_tab
from pages.preprocessing.tabs.export_tab import export_tab
from pages.preprocessing.tabs.file_explorer_tab import file_explorer_tab
from pages.preprocessing.tabs.yaku_process_tab import yaku_process_tab
from pages.preprocessing.tabs.ruru_process_tab import ruru_process_tab
from pages.preprocessing.tabs.courses_process_tab import courses_process_tab
from pages.preprocessing.tabs.config_tab import config_tab

def preprocessing_page():
    """
    Página principal de preprocesamiento.
    Incluye pestañas para diferentes funcionalidades relacionadas con el preprocesamiento de datos.
    """
    st.title("Preprocesamiento")
    st.write("""
        Esta sección permite cargar, limpiar, procesar y exportar los datos de yakus, rurus y cursos
        para prepararlos para el proceso de matching. Utiliza las diferentes pestañas para realizar
        operaciones específicas.
    """)
    
    # Crear pestañas
    tabs = st.tabs([
        "Explorador de Archivos", 
        "Carga y Limpieza", 
        "Preprocesamiento de Yakus", 
        "Preprocesamiento de Rurus", 
        "Preprocesamiento de Cursos", 
        "Selección por Área", 
        "Exportación",
        "Configuración"
    ])
    
    # Contenido de cada pestaña
    with tabs[0]:
        file_explorer_tab()
    
    with tabs[1]:
        load_clean_tab()
    
    with tabs[2]:
        yaku_process_tab()
    
    with tabs[3]:
        ruru_process_tab()
    
    with tabs[4]:
        courses_process_tab()
    
    with tabs[5]:
        selection_area_tab()
    
    with tabs[6]:
        export_tab()
    
    with tabs[7]:
        config_tab()

# Añadimos esta función para mantener compatibilidad con app.py
def preprocess_main():
    """
    Función de entrada para la página de preprocesamiento.
    Esta función existe para mantener compatibilidad con las importaciones existentes.
    """
    return preprocessing_page()

if __name__ == "__main__":
    preprocessing_page() 