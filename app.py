import streamlit as st
import os

# Importar componentes
from components.dashboard import dashboard_page
from components.sidebar import sidebar_navigation

# Importar páginas
from pages.match.match_page import match_main
from pages.preprocessing.preprocess_page import preprocess_main
from pages.email.email_page import email_main

# Configuración de la página
st.set_page_config(
    page_title="Yachay Wasi Dashboard", 
    page_icon="🔍", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cargar estilos CSS
with open("assets/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Inicializar variables de sesión si no existen
if "page" not in st.session_state:
    st.session_state.page = "dashboard"

def main():
    """
    Función principal que maneja la navegación entre páginas
    """
    # Mostrar la página actual según la variable de sesión
    if st.session_state.page == "dashboard":
        dashboard_page()
    
    elif st.session_state.page == "match":
        match_main()
    
    elif st.session_state.page == "preprocessing":
        preprocess_main()
    
    elif st.session_state.page == "email":
        email_main()
    
    elif st.session_state.page == "docs":
        docs_page()
    
    else:
        # Si la página no existe, mostrar el dashboard
        dashboard_page()

def docs_page():
    """
    Página de documentación
    """
    # Configurar la navegación lateral
    sidebar_navigation()
    
    st.markdown("<h1 class='main-header'>Documentación</h1>", unsafe_allow_html=True)
    st.markdown("<p class='info-text'>Guía de uso de la plataforma Yachay Wasi</p>", unsafe_allow_html=True)
    
    st.markdown("""
    ## Bienvenido a la documentación
    
    Esta plataforma te permite gestionar todo el proceso de asignación de Yakus a Rurus de forma eficiente.
    
    ### Herramientas disponibles:
    
    1. **Pre-procesamiento**: Limpia y prepara los datos antes de realizar el match.
    2. **Match Yaku-Ruru**: Asigna Yakus a Rurus de manera óptima según disponibilidad y preferencias.
    3. **Envío de Emails**: Comunica los resultados del match a Yakus y Rurus de forma automatizada.
    
    ### Flujo de trabajo recomendado:
    
    1. Preprocesa los datos para asegurarte que están limpios y estandarizados
    2. Ejecuta el algoritmo de match para encontrar las mejores asignaciones
    3. Envía emails a los participantes para notificarles sus asignaciones
    
    Para más información, contacta al equipo de soporte.
    """)

if __name__ == "__main__":
    main() 