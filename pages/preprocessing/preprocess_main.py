import streamlit as st
import sys
import os

# Importamos navegación lateral
from components.sidebar import sidebar_navigation

# Importamos los tabs modularizados
from pages.preprocessing.tabs.load_clean_tab import load_clean_tab
from pages.preprocessing.tabs.selection_area_tab import selection_area_tab
from pages.preprocessing.tabs.export_tab import export_tab
from .tabs.ruru_process_tab import ruru_process_tab
from .tabs.file_explorer_tab import file_explorer_tab
from .tabs.yaku_process_tab import yaku_process_tab
from .tabs.courses_process_tab import courses_process_tab
from .tabs.config_tab import config_tab

def preprocessing_page():
    """
    Página principal de preprocesamiento que contiene todas las pestañas para preparar los datos
    para el algoritmo de matching.
    """
    st.title("Preprocesamiento de Datos")
    st.write("Utiliza estas herramientas para preparar los datos antes de ejecutar el algoritmo de matching.")
    
    # Crear pestañas para las diferentes funcionalidades
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Explorador de Archivos", 
        "Preprocesamiento de Yakus", 
        "Preprocesamiento de Rurus",
        "Preprocesamiento de Cursos",
        "Configuración"
    ])
    
    # Contenido de cada pestaña
    with tab1:
        file_explorer_tab()
        
    with tab2:
        yaku_process_tab()
        
    with tab3:
        ruru_process_tab()
        
    with tab4:
        courses_process_tab()
        
    with tab5:
        config_tab()

def preprocess_main():
    """
    Página principal para la funcionalidad de Preprocesamiento
    """
    # Configurar la navegación lateral
    sidebar_navigation()
    
    st.markdown("<h1 class='main-header'>Preprocesamiento de Datos</h1>", unsafe_allow_html=True)
    st.markdown("<p class='info-text'>Limpia y prepara tus datos antes de realizar el match</p>", unsafe_allow_html=True)
    
    # Inicializar variables de estado si no existen
    for key in ['yakus_data', 'processed_data', 'selected_data', 'export_data', 'last_action']:
        if key not in st.session_state:
            st.session_state[key] = None
    
    # Variable para rastrear acciones de usuario
    if 'last_action' not in st.session_state:
        st.session_state['last_action'] = None
    
    # Crear tabs para las diferentes funcionalidades
    tab1, tab2, tab3, tab4 = st.tabs([
        "Carga y Limpieza de Yakus", 
        "Selección por Área", 
        "Exportación",
        "Preprocesamiento de Rurus"
    ])
    
    with tab1:
        load_clean_tab()
    
    with tab2:
        selection_area_tab()
    
    with tab3:
        export_tab()
    
    with tab4:
        ruru_process_tab() 