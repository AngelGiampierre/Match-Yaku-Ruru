import streamlit as st
import pandas as pd
from pages.preprocessing.components.file_handlers import export_dataframe

def export_tab():
    """Tab para exportación de datos procesados"""
    st.header("Exportación de Datos")
    
    # Determinar qué datos exportar (procesados o filtrados por área)
    data_to_export = get_data_to_export()
    
    if data_to_export is None:
        st.warning("⚠️ No hay datos para exportar. Procesa los datos en las pestañas anteriores.")
        return
    
    # Mostrar una vista previa para confirmar que los datos están ordenados correctamente
    with st.expander("Verificar datos a exportar", expanded=False):
        st.dataframe(data_to_export)
    
    # Opciones de exportación
    export_options(data_to_export)

def get_data_to_export():
    """Obtiene los datos a exportar desde la sesión."""
    if st.session_state.export_data is not None:
        data_to_export = st.session_state.export_data.copy()  # Hacer una copia para no modificar el original
        st.success("✅ Se exportarán los datos filtrados por área")
        return data_to_export
    
    elif st.session_state.processed_data is not None:
        data_to_export = st.session_state.processed_data.copy()  # Hacer una copia para no modificar el original
        st.info("ℹ️ Se exportarán los datos procesados (sin filtrado por área)")
        # Verificación adicional para mostrar información sobre los datos a exportar
        st.info(f"📊 Registros a exportar: {len(data_to_export)} | Incluye todas las ediciones realizadas")
        return data_to_export
    
    return None

def export_options(data_to_export):
    """Muestra y procesa las opciones de exportación."""
    st.subheader("Opciones de Exportación")
    
    export_format = st.radio(
        "Formato de exportación:",
        options=["Excel (.xlsx)", "CSV (.csv)"]
    )
    
    include_validation = st.checkbox(
        "Incluir columnas de validación (DNI_Validado, etc.)", 
        value=False
    )
    
    # Crear nombre de archivo
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    default_filename = f"yakus_procesados_{timestamp}"
    export_filename = st.text_input("Nombre del archivo:", value=default_filename)
    
    if st.button("Exportar Datos"):
        # Eliminar columnas de validación si no se desean incluir
        export_df = clean_export_dataframe(data_to_export, include_validation)
        
        # Verificación para confirmar que se están exportando los datos correctos
        st.success(f"✅ Exportando {len(export_df)} registros con todas las ediciones aplicadas")
        
        # Exportar según formato
        export_dataframe(export_df, export_filename, export_format)
        
        # Resumen de datos exportados
        show_export_summary(export_df)

def clean_export_dataframe(df, include_validation=False):
    """Prepara el DataFrame para exportación."""
    export_df = df.copy()
    
    # Asegurarnos que todas las columnas de texto sean de tipo string para evitar problemas con PyArrow
    for col in export_df.select_dtypes(include=['object']).columns:
        export_df[col] = export_df[col].astype(str)
    
    # Buscar y asegurar que la columna DNI sea string
    dni_cols = [col for col in export_df.columns if 'dni' in col.lower() or 'pasaporte' in col.lower()]
    for col in dni_cols:
        export_df[col] = export_df[col].astype(str)
    
    if not include_validation:
        validation_cols = [col for col in export_df.columns if '_Validado' in col or '_Normalizado' in col]
        if validation_cols:
            export_df = export_df.drop(columns=validation_cols)
    
    return export_df

def show_export_summary(export_df):
    """Muestra el resumen de los datos exportados."""
    st.subheader("Resumen de Datos Exportados")
    st.info(f"📊 Total de registros: {len(export_df)}")
    st.info(f"📋 Columnas: {len(export_df.columns)}")
    
    # Si hay área, mostrar distribución por área
    area_cols = [col for col in export_df.columns if 'área' in col.lower() or 'area' in col.lower() or 'interesado' in col.lower()]
    if area_cols:
        area_col = area_cols[0]
        area_counts = export_df[area_col].value_counts()
        
        st.subheader("Distribución por Área")
        for area, count in area_counts.items():
            st.write(f"- {area}: {count} yakus") 