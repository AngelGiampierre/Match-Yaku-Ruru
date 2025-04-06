import streamlit as st
from pages.match.data_loader import cargar_datos_page
from pages.match.results import resultados_page
from components.sidebar import sidebar_navigation

def match_main():
    """
    Página principal para la funcionalidad de Match Yaku-Ruru
    """
    # Configurar la navegación lateral
    sidebar_navigation()
    
    st.markdown("<h1 class='main-header'>Match Yaku Ruru</h1>", unsafe_allow_html=True)
    st.markdown("<p class='info-text'>Plataforma para asignar Yakus a Rurus de manera óptima</p>", unsafe_allow_html=True)
    
    # Crear pestañas para cargar datos y ver resultados
    tabs = st.tabs(["Cargar Datos", "Resultados"])
    
    with tabs[0]:
        cargar_datos_page()
    
    with tabs[1]:
        resultados_page() 