"""
Aplicación principal Match-Yaku-Ruru.

Este es el punto de entrada principal de la aplicación, que integra
los diferentes módulos: preprocesamiento, match y envío de correos.
"""

import streamlit as st
import os
import sys

# Asegurarse de que el directorio actual está en el path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar módulos principales
from preprocessing.preprocessing_main import preprocessing_page
from match.match_main import match_page # Asegúrate que match_page esté definida en match_main.py
from emailing.email_main import email_page

# Inicializar el estado de sesión para la navegación
if "current_page" not in st.session_state:
    st.session_state.current_page = "Inicio"

# Configuración de la página
st.set_page_config(
    page_title="Match Yaku-Ruru",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Cargar estilos CSS si existen
css_path = os.path.join("assets", "styles.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def main():
    """
    Función principal de la aplicación.
    """
    # Sidebar para navegación
    st.sidebar.title("Match Yaku-Ruru")
    
    # Intentar cargar imagen si existe
    try:
        st.sidebar.image("https://www.hacerperu.pe/wp-content/uploads/2023/03/Yachay-Wasi.jpg", width=200)
    except:
        pass  # Si la imagen no existe, continuar sin error
    
    # Opciones de navegación
    page = st.sidebar.radio(
        "Navegación",
        options=["Inicio", "Preprocesamiento", "Match", "Envío de Correos"],
        index=["Inicio", "Preprocesamiento", "Match", "Envío de Correos"].index(st.session_state.current_page),
        key="navigation"
    )
    
    # Actualizar el estado de sesión con la página actual
    st.session_state.current_page = page
    
    # Mostrar página según selección
    if page == "Inicio":
        show_home_page()
    elif page == "Preprocesamiento":
        preprocessing_page()
    elif page == "Match":
        # --- LLAMAR A LA FUNCIÓN DE LA PÁGINA MATCH ---
        match_page()
    elif page == "Envío de Correos":
        # --- LLAMAR A LA PÁGINA DE EMAIL ---
        email_page()
    
    # Pie de página
    st.sidebar.markdown("---")
    st.sidebar.info(
        "Match Yaku-Ruru: Herramienta para optimizar la asignación "
        "de mentores a estudiantes en Yachay Wasi."
    )


# Función para cambiar de página programáticamente
def navigate_to(page_name):
    st.session_state.current_page = page_name
    st.rerun()


def show_home_page():
    """
    Muestra la página de inicio.
    """
    st.title("Bienvenido a Match Yaku-Ruru")
    
    st.write("""
    Esta aplicación te ayuda a optimizar la asignación de Yakus (mentores) 
    a Rurus (estudiantes) en Yachay Wasi, considerando criterios como:
    
    - Horarios disponibles
    - Áreas de especialidad
    - Niveles educativos
    - Preferencias de cursos
    - Y más...
    """)
    
    # Tarjetas para cada módulo
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### Preprocesamiento
        
        Prepara tus datos antes del match:
        
        - Selección de columnas
        - Validación de DNIs/Correos
        - Filtrado por área
        """)
        
        if st.button("Ir a Preprocesamiento", key="goto_preprocessing"):
            navigate_to("Preprocesamiento")
    
    with col2:
        st.markdown("""
        ### Match
        
        Ejecuta el algoritmo de asignación:
        
        - Carga datos procesados
        - Ejecuta el match por área
        - Visualiza y descarga resultados
        
        *En desarrollo*
        """)
        
        if st.button("Ir a Match", key="goto_match", disabled=False):
            navigate_to("Match")
    
    with col3:
        st.markdown("""
        ### Envío de Correos
        
        Comunica los resultados:
        
        - Envía asignaciones a Yakus
        - Carga resultados del match
        - Envío por lotes
        """)
        
        if st.button("Ir a Envío de Correos", key="goto_email", disabled=False):
            navigate_to("Envío de Correos")
    
    st.markdown("---")
    
    st.markdown("""
    ## ¿Cómo empezar?
    
    1. Ve a la sección de **Preprocesamiento** para preparar tus datos
    2. Luego, usa la sección de **Match** para ejecutar el algoritmo
    3. Finalmente, usa la sección de **Envío de Correos** para comunicar los resultados
    
    Selecciona una opción en el menú lateral para comenzar.
    """)


if __name__ == "__main__":
    main() 