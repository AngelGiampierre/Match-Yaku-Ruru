import streamlit as st
import sys
import os

# Importamos navegación lateral
from components.sidebar import sidebar_navigation

# Importamos los tabs modularizados
from pages.preprocessing.tabs.load_clean_tab import load_and_clean_tab
from pages.preprocessing.tabs.selection_area_tab import selection_by_area_tab
from pages.preprocessing.tabs.export_tab import export_tab

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
    tab1, tab2, tab3 = st.tabs([
        "1. Carga y Limpieza de Datos", 
        "2. Selección por Área", 
        "3. Exportación de Datos"
    ])
    
    with tab1:
        load_and_clean_tab()
    
    with tab2:
        selection_by_area_tab()
    
    with tab3:
        export_tab() 