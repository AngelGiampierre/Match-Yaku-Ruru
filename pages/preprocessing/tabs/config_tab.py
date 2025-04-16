import streamlit as st
import os
import sys
import json
import pandas as pd

# Agregar la raíz del proyecto al path de Python para importaciones absolutas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from utils import get_temp_dir, load_data, save_data

def config_tab():
    """
    Tab para configurar parámetros de estandarización y compatibilidad de datos.
    Permite ajustar cómo se procesan los datos de Rurus y Yakus para asegurar una correcta compatibilidad.
    """
    st.header("Configuración de Preprocesamiento")
    st.subheader("Ajusta parámetros de estandarización")
    
    # Cargar configuración existente o usar valores predeterminados
    config = load_config()
    
    # Crear secciones para diferentes aspectos de la configuración
    st.write("### Configuración general")
    
    # Opción para guardar automáticamente los datos procesados
    config['guardar_automaticamente'] = st.checkbox(
        "Guardar automáticamente los datos procesados", 
        value=config.get('guardar_automaticamente', True),
        help="Guarda automáticamente los datos procesados en archivos temporales para su uso posterior"
    )
    
    # Formato de salida preferido
    config['formato_salida'] = st.selectbox(
        "Formato de salida preferido",
        options=["Excel (.xlsx)", "CSV (.csv)", "Ambos"],
        index=["Excel (.xlsx)", "CSV (.csv)", "Ambos"].index(config.get('formato_salida', "Ambos")),
        help="Formato de archivo preferido para descargar los datos procesados"
    )
    
    # Sección de estandarización de datos
    st.write("### Estandarización de datos")
    
    # Categorías de horarios
    st.write("#### Categorías de horarios")
    config['usar_categoria_horarios'] = st.checkbox(
        "Usar categorías estándar para horarios", 
        value=config.get('usar_categoria_horarios', True),
        help="Convertir los horarios a categorías estándar (Mañana, Tarde, Noche)"
    )
    
    if config['usar_categoria_horarios']:
        col1, col2, col3 = st.columns(3)
        with col1:
            config['horario_manana'] = st.text_input(
                "Horario de Mañana", 
                value=config.get('horario_manana', "8:00 - 12:00"),
                help="Rango de horas para la categoría Mañana"
            )
        with col2:
            config['horario_tarde'] = st.text_input(
                "Horario de Tarde", 
                value=config.get('horario_tarde', "12:00 - 18:00"),
                help="Rango de horas para la categoría Tarde"
            )
        with col3:
            config['horario_noche'] = st.text_input(
                "Horario de Noche", 
                value=config.get('horario_noche', "18:00 - 22:00"),
                help="Rango de horas para la categoría Noche"
            )
    
    # Configuración de niveles educativos
    st.write("#### Niveles educativos")
    config['estandarizar_niveles'] = st.checkbox(
        "Estandarizar niveles educativos", 
        value=config.get('estandarizar_niveles', True),
        help="Convertir los diferentes formatos de niveles educativos a un formato estándar"
    )
    
    if config['estandarizar_niveles']:
        # Configuración para primaria
        st.write("**Niveles de Primaria:**")
        col1, col2 = st.columns(2)
        with col1:
            config['primaria_nivel1'] = st.text_input(
                "Primer nivel", 
                value=config.get('primaria_nivel1', "Primaria (1° y 2° grado)"),
                help="Nombre estándar para el primer nivel de primaria"
            )
        with col2:
            config['primaria_nivel1_grados'] = st.text_input(
                "Grados incluidos", 
                value=config.get('primaria_nivel1_grados', "1, 2"),
                help="Grados incluidos en este nivel, separados por coma"
            )
        
        col1, col2 = st.columns(2)
        with col1:
            config['primaria_nivel2'] = st.text_input(
                "Segundo nivel", 
                value=config.get('primaria_nivel2', "Primaria (3° y 4° grado)"),
                help="Nombre estándar para el segundo nivel de primaria"
            )
        with col2:
            config['primaria_nivel2_grados'] = st.text_input(
                "Grados incluidos", 
                value=config.get('primaria_nivel2_grados', "3, 4"),
                help="Grados incluidos en este nivel, separados por coma"
            )
        
        col1, col2 = st.columns(2)
        with col1:
            config['primaria_nivel3'] = st.text_input(
                "Tercer nivel", 
                value=config.get('primaria_nivel3', "Primaria (5° y 6° grado)"),
                help="Nombre estándar para el tercer nivel de primaria"
            )
        with col2:
            config['primaria_nivel3_grados'] = st.text_input(
                "Grados incluidos", 
                value=config.get('primaria_nivel3_grados', "5, 6"),
                help="Grados incluidos en este nivel, separados por coma"
            )
        
        # Configuración para secundaria
        st.write("**Niveles de Secundaria:**")
        col1, col2 = st.columns(2)
        with col1:
            config['secundaria_nivel1'] = st.text_input(
                "Primer nivel", 
                value=config.get('secundaria_nivel1', "Secundaria (1°, 2° y 3° grado)"),
                help="Nombre estándar para el primer nivel de secundaria"
            )
        with col2:
            config['secundaria_nivel1_grados'] = st.text_input(
                "Grados incluidos", 
                value=config.get('secundaria_nivel1_grados', "1, 2, 3"),
                help="Grados incluidos en este nivel, separados por coma"
            )
        
        col1, col2 = st.columns(2)
        with col1:
            config['secundaria_nivel2'] = st.text_input(
                "Segundo nivel", 
                value=config.get('secundaria_nivel2', "Secundaria (4° y 5° grado)"),
                help="Nombre estándar para el segundo nivel de secundaria"
            )
        with col2:
            config['secundaria_nivel2_grados'] = st.text_input(
                "Grados incluidos", 
                value=config.get('secundaria_nivel2_grados', "4, 5"),
                help="Grados incluidos en este nivel, separados por coma"
            )
    
    # Configuración de formato de nombres
    st.write("#### Formato de nombres")
    config['estandarizar_nombres'] = st.checkbox(
        "Estandarizar formato de nombres", 
        value=config.get('estandarizar_nombres', True),
        help="Aplicar un formato estándar a los nombres (nombres completos y apellidos abreviados)"
    )
    
    # Configuración de áreas
    st.write("#### Áreas")
    config['areas_estandar'] = st.multiselect(
        "Áreas estándar",
        options=["Arte & Cultura", "Asesoría a Colegios Nacionales", "Bienestar Psicológico"],
        default=config.get('areas_estandar', ["Arte & Cultura", "Asesoría a Colegios Nacionales", "Bienestar Psicológico"]),
        help="Lista de áreas estándar para la clasificación"
    )
    
    # Configuración de niveles de quechua
    st.write("#### Niveles de Quechua")
    config['niveles_quechua'] = st.multiselect(
        "Niveles de Quechua estándar",
        options=["No lo hablo", "Nivel básico", "Nivel intermedio", "Nivel avanzado", "Nativo"],
        default=config.get('niveles_quechua', ["No lo hablo", "Nivel básico", "Nivel intermedio", "Nivel avanzado", "Nativo"]),
        help="Lista de niveles de quechua estándar"
    )
    
    # Sección de verificación de compatibilidad
    st.write("### Verificación de compatibilidad")
    
    config['verificar_compatibilidad'] = st.checkbox(
        "Verificar compatibilidad entre Rurus y Yakus", 
        value=config.get('verificar_compatibilidad', True),
        help="Realizar una verificación de compatibilidad entre los datos de Rurus y Yakus después del procesamiento"
    )
    
    if config['verificar_compatibilidad']:
        config['umbral_compatibilidad'] = st.slider(
            "Umbral de compatibilidad (%)",
            min_value=50,
            max_value=100,
            value=config.get('umbral_compatibilidad', 80),
            help="Porcentaje mínimo de compatibilidad requerido entre los datos de Rurus y Yakus"
        )
    
    # Botón para guardar la configuración
    if st.button("Guardar configuración"):
        save_config(config)
        st.success("✅ Configuración guardada correctamente")
    
    # Botón para restablecer la configuración por defecto
    if st.button("Restablecer configuración predeterminada"):
        reset_config()
        st.success("✅ Configuración restablecida a valores predeterminados")
        st.warning("Recarga la página para ver los cambios")
    
    # Mostrar configuración actual
    with st.expander("Ver configuración actual (JSON)"):
        st.json(config)
    
    # Verificar compatibilidad actual
    if st.button("Verificar compatibilidad de datos procesados"):
        verificar_compatibilidad_datos()

# Funciones auxiliares para gestionar la configuración
def load_config():
    """
    Carga la configuración desde un archivo o utiliza valores predeterminados.
    
    Returns:
        dict: Diccionario con la configuración cargada o predeterminada
    """
    try:
        config = load_data("preprocessing_config.pkl")
        if config is None:
            return get_default_config()
        return config
    except:
        return get_default_config()

def save_config(config):
    """
    Guarda la configuración en un archivo.
    
    Args:
        config (dict): Diccionario con la configuración a guardar
    """
    save_data(config, "preprocessing_config.pkl")

def reset_config():
    """
    Restablece la configuración a los valores predeterminados.
    """
    save_config(get_default_config())

def get_default_config():
    """
    Retorna la configuración predeterminada.
    
    Returns:
        dict: Diccionario con la configuración predeterminada
    """
    return {
        'guardar_automaticamente': True,
        'formato_salida': "Ambos",
        'usar_categoria_horarios': True,
        'horario_manana': "8:00 - 12:00",
        'horario_tarde': "12:00 - 18:00",
        'horario_noche': "18:00 - 22:00",
        'estandarizar_niveles': True,
        'primaria_nivel1': "Primaria (1° y 2° grado)",
        'primaria_nivel1_grados': "1, 2",
        'primaria_nivel2': "Primaria (3° y 4° grado)",
        'primaria_nivel2_grados': "3, 4",
        'primaria_nivel3': "Primaria (5° y 6° grado)",
        'primaria_nivel3_grados': "5, 6",
        'secundaria_nivel1': "Secundaria (1°, 2° y 3° grado)",
        'secundaria_nivel1_grados': "1, 2, 3",
        'secundaria_nivel2': "Secundaria (4° y 5° grado)",
        'secundaria_nivel2_grados': "4, 5",
        'estandarizar_nombres': True,
        'areas_estandar': ["Arte & Cultura", "Asesoría a Colegios Nacionales", "Bienestar Psicológico"],
        'niveles_quechua': ["No lo hablo", "Nivel básico", "Nivel intermedio", "Nivel avanzado", "Nativo"],
        'verificar_compatibilidad': True,
        'umbral_compatibilidad': 80
    }

def verificar_compatibilidad_datos():
    """
    Verifica la compatibilidad entre los datos procesados de Rurus y Yakus.
    Muestra el resultado en la interfaz.
    """
    try:
        # Cargar datos procesados
        rurus_df = load_data("rurus_processed.pkl")
        yakus_df = load_data("yakus_processed.pkl")
        
        if rurus_df is None or yakus_df is None:
            st.warning("⚠️ No se encontraron datos procesados. Procesa los datos de Rurus y Yakus primero.")
            return
        
        # Verificar las columnas comunes
        columnas_rurus = set(rurus_df.columns)
        columnas_yakus = set(yakus_df.columns)
        columnas_comunes = columnas_rurus.intersection(columnas_yakus)
        
        # Calcular estadísticas
        total_columnas = len(columnas_rurus.union(columnas_yakus))
        porcentaje_compatibilidad = (len(columnas_comunes) / total_columnas) * 100
        
        st.write("### Resultado de la verificación de compatibilidad")
        st.write(f"**Porcentaje de compatibilidad:** {porcentaje_compatibilidad:.1f}%")
        
        # Mostrar detalles
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Columnas en común:**")
            for col in sorted(columnas_comunes):
                st.write(f"- ✅ {col}")
        
        with col2:
            st.write("**Columnas diferentes:**")
            columnas_diferentes_rurus = columnas_rurus - columnas_yakus
            columnas_diferentes_yakus = columnas_yakus - columnas_rurus
            
            if columnas_diferentes_rurus:
                st.write("Solo en Rurus:")
                for col in sorted(columnas_diferentes_rurus):
                    st.write(f"- 🔵 {col}")
            
            if columnas_diferentes_yakus:
                st.write("Solo en Yakus:")
                for col in sorted(columnas_diferentes_yakus):
                    st.write(f"- 🟠 {col}")
        
        # Verificar horarios
        dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        horarios_compatibles = True
        
        for dia in dias_semana:
            horario_col = f"Horario_{dia}"
            if horario_col in columnas_comunes:
                # Verificar si los valores son compatibles
                valores_rurus = set(rurus_df[horario_col].dropna().unique())
                valores_yakus = set(yakus_df[horario_col].dropna().unique())
                if valores_rurus != valores_yakus and valores_rurus.intersection(valores_yakus) != valores_rurus.union(valores_yakus):
                    horarios_compatibles = False
                    break
        
        # Verificar niveles educativos
        niveles_compatibles = True
        if 'Grado' in columnas_rurus and 'Grados' in columnas_yakus:
            valores_rurus = set(rurus_df['Grado'].dropna().unique())
            valores_yakus = set()
            
            # Los yakus pueden tener múltiples niveles separados por coma
            for nivel in yakus_df['Grados'].dropna():
                for n in nivel.split(','):
                    valores_yakus.add(n.strip())
            
            # Verificar si hay al menos un nivel en común o si todos son compatibles
            if not valores_rurus.intersection(valores_yakus):
                niveles_compatibles = False
        
        # Mostrar resultado general
        config = load_config()
        umbral = config.get('umbral_compatibilidad', 80)
        
        if porcentaje_compatibilidad >= umbral and horarios_compatibles and niveles_compatibles:
            st.success(f"✅ Los datos son compatibles (compatibilidad > {umbral}%)")
            st.success("✅ Los datos están listos para el proceso de matching")
        else:
            st.error(f"❌ Los datos no son completamente compatibles")
            
            if not horarios_compatibles:
                st.warning("⚠️ Los formatos de horarios no son compatibles entre Rurus y Yakus")
            
            if not niveles_compatibles:
                st.warning("⚠️ Los niveles educativos no son compatibles entre Rurus y Yakus")
            
            if porcentaje_compatibilidad < umbral:
                st.warning(f"⚠️ El porcentaje de compatibilidad ({porcentaje_compatibilidad:.1f}%) es menor que el umbral ({umbral}%)")
            
            st.info("Recomendación: Revisa la configuración y vuelve a procesar los datos.")
            
    except Exception as e:
        st.error(f"Error al verificar la compatibilidad: {str(e)}") 