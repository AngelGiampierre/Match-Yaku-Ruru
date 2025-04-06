import streamlit as st

def dashboard_page():
    """
    Página principal del dashboard que muestra todas las herramientas disponibles
    """
    st.markdown("<h1 class='main-header'>Dashboard Yachay Wasi</h1>", unsafe_allow_html=True)
    st.markdown("<p class='info-text'>Plataforma integral para la gestión de Yakus y Rurus</p>", unsafe_allow_html=True)
    
    # Introducción
    st.markdown("""
    <div class='highlight'>
        <h3>Bienvenido a la plataforma de gestión</h3>
        <p>Esta plataforma te permite gestionar todo el proceso desde el pre-procesamiento de datos, 
        hasta la asignación de Yakus a Rurus y la comunicación de resultados.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Mostrar tarjetas para cada herramienta
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class='dashboard-card' onclick="parent.window.location.href='?page=preprocessing'">
            <div class='card-icon'>🔍</div>
            <div class='card-title'>Pre-procesamiento</div>
            <p class='card-description'>Prepara y limpia los datos de Yakus y Rurus antes de realizar el match.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Botón adicional para navegación directa (ya que el onClick en HTML puede no funcionar en Streamlit)
        if st.button("Ir a Pre-procesamiento", key="goto_preprocessing"):
            st.session_state.page = "preprocessing"
    
    with col2:
        st.markdown("""
        <div class='dashboard-card' onclick="parent.window.location.href='?page=match'">
            <div class='card-icon'>🤝</div>
            <div class='card-title'>Match Yaku-Ruru</div>
            <p class='card-description'>Asigna Yakus a Rurus de manera óptima según disponibilidad y preferencias.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Ir a Match", key="goto_match"):
            st.session_state.page = "match"
    
    with col3:
        st.markdown("""
        <div class='dashboard-card' onclick="parent.window.location.href='?page=email'">
            <div class='card-icon'>📧</div>
            <div class='card-title'>Envío de Emails</div>
            <p class='card-description'>Comunica los resultados del match a Yakus y Rurus de forma automatizada.</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Ir a Emails", key="goto_email"):
            st.session_state.page = "email"
    
    # Métricas o estadísticas (opcional)
    st.markdown("<h2 class='section-header'>Estadísticas del Sistema</h2>", unsafe_allow_html=True)
    
    metric1, metric2, metric3 = st.columns(3)
    
    metric1.metric(label="Total Yakus", value="0")
    metric2.metric(label="Total Rurus", value="0")
    metric3.metric(label="Matches Realizados", value="0") 