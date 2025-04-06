import streamlit as st

def sidebar_navigation():
    """
    Componente para la navegación lateral que se usará en todas las páginas
    """
    with st.sidebar:
        st.title("Navegación")
        
        # Botón para ir al dashboard principal
        if st.button("Dashboard Principal", use_container_width=True):
            st.session_state.page = "dashboard"
        
        st.markdown("---")
        
        st.subheader("Herramientas")
        
        # Botones para las diferentes herramientas
        if st.button("Pre-procesamiento", use_container_width=True):
            st.session_state.page = "preprocessing"
            
        if st.button("Match Yaku-Ruru", use_container_width=True):
            st.session_state.page = "match"
            
        if st.button("Envío de Emails", use_container_width=True):
            st.session_state.page = "email"
        
        st.markdown("---")
        
        # Información adicional
        st.markdown("### Ayuda")
        if st.button("Documentación", use_container_width=True):
            st.session_state.page = "docs"
        
        # Footer
        st.markdown("---")
        st.markdown("**Yachay Wasi © 2025**")
        st.markdown("*Versión 1.0.0*") 