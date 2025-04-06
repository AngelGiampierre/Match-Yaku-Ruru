import streamlit as st
import pandas as pd
from components.sidebar import sidebar_navigation

def email_main():
    """
    Página principal para la funcionalidad de Envío de Emails
    """
    # Configurar la navegación lateral
    sidebar_navigation()
    
    st.markdown("<h1 class='main-header'>Envío de Emails</h1>", unsafe_allow_html=True)
    st.markdown("<p class='info-text'>Comunica los resultados del match a Yakus y Rurus de forma automatizada</p>", unsafe_allow_html=True)
    
    # Contenido de ejemplo para esta página - se implementará en el futuro
    st.info("Esta funcionalidad está en desarrollo. Próximamente podrás:")
    
    features = [
        "Enviar emails personalizados a Yakus y Rurus con sus asignaciones",
        "Crear plantillas de email personalizables",
        "Programar envíos automáticos",
        "Ver estadísticas de envío y apertura",
        "Reenviar emails a destinatarios específicos"
    ]
    
    for feature in features:
        st.markdown(f"- {feature}")
    
    # Plantilla de ejemplo
    st.markdown("<h2 class='section-header'>Plantilla de Email</h2>", unsafe_allow_html=True)
    
    template = """
    Asunto: Asignación Match Yaku-Ruru: {{nombre}}
    
    Estimado/a {{nombre}},
    
    Nos complace informarte que has sido asignado/a con éxito en el programa Match Yaku-Ruru.
    
    Detalles de tu asignación:
    - {{tipo}}: {{nombre_contraparte}}
    - Opción: {{opcion}}
    - Días y horarios: {{horarios}}
    
    Para cualquier consulta, no dudes en contactarnos.
    
    Saludos cordiales,
    Equipo Yachay Wasi
    """
    
    st.code(template, language="text")
    
    # Carga de resultados
    st.markdown("<h2 class='section-header'>Cargar Resultados del Match</h2>", unsafe_allow_html=True)
    
    upload_method = st.radio("Método de carga", ["Usar resultados actuales", "Cargar archivo de resultados"])
    
    if upload_method == "Cargar archivo de resultados":
        uploaded_file = st.file_uploader("Cargar archivo Excel con resultados", type=["xlsx"])
        
        if uploaded_file is not None:
            try:
                matches_df = pd.read_excel(uploaded_file)
                st.success(f"Archivo cargado exitosamente con {len(matches_df)} matches.")
                
                with st.expander("Ver datos cargados", expanded=True):
                    st.dataframe(matches_df)
                
                st.session_state["email_matches"] = matches_df
            
            except Exception as e:
                st.error(f"Error al cargar el archivo: {str(e)}")
    else:
        if "matches_df" in st.session_state:
            st.success(f"Usando resultados actuales con {len(st.session_state['matches_df'])} matches.")
            
            with st.expander("Ver datos cargados", expanded=True):
                st.dataframe(st.session_state["matches_df"])
            
            st.session_state["email_matches"] = st.session_state["matches_df"]
        else:
            st.warning("No hay resultados de match disponibles en la sesión actual.")
    
    # Configuración de envío
    st.markdown("<h2 class='section-header'>Configuración de Envío</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input("Remitente", "match@yachaywasi.org")
        st.text_input("Nombre de Remitente", "Match Yaku-Ruru")
        st.selectbox("Destinatarios", ["Yakus y Rurus", "Solo Yakus", "Solo Rurus"])
    
    with col2:
        st.checkbox("Incluir copia al administrador")
        st.text_input("Email del administrador", "admin@yachaywasi.org")
        st.checkbox("Programar envío")
        st.date_input("Fecha de envío")
    
    if st.button("Previsualizar Emails"):
        st.info("Funcionalidad en desarrollo. Esta acción aún no está implementada.")
    
    if st.button("Enviar Emails"):
        st.info("Funcionalidad en desarrollo. Esta acción aún no está implementada.") 