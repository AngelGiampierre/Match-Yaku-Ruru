import streamlit as st
import pandas as pd
import numpy as np
import io
import os
import sys
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from pages.preprocessing.components.file_handlers import export_dataframe

# Agregar la raíz del proyecto al path de Python para importaciones absolutas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from utils import load_data, save_data, get_temp_files

def export_tab():
    """
    Tab para exportar los datos procesados.
    Permite visualizar resúmenes de datos y exportar en diferentes formatos.
    """
    st.header("Exportación de Datos")
    st.subheader("Visualiza, resume y exporta los datos procesados")
    
    # Obtener lista de archivos temporales disponibles
    temp_files = get_temp_files()
    pkl_files = [f for f in temp_files if f.endswith('.pkl')]
    
    if not pkl_files:
        st.warning("⚠️ No se encontraron archivos de datos procesados. Por favor, procesa algunos datos primero.")
        return
    
    # Seleccionar archivo a exportar
    st.write("### Seleccionar archivo para exportar")
    
    # Categorizar archivos
    yakus_files = [f for f in pkl_files if 'yaku' in f.lower()]
    rurus_files = [f for f in pkl_files if 'ruru' in f.lower()]
    other_files = [f for f in pkl_files if 'yaku' not in f.lower() and 'ruru' not in f.lower()]
    
    # Crear tabs para los diferentes tipos de archivos
    tab1, tab2, tab3 = st.tabs(["Datos de Yakus", "Datos de Rurus", "Otros datos"])
    
    with tab1:
        if yakus_files:
            selected_yaku_file = st.selectbox(
                "Selecciona un archivo de datos de Yakus:",
                options=yakus_files,
                key="yaku_file_select"
            )
            
            if st.button("Cargar datos de Yakus", key="load_yaku_button"):
                process_file_export(selected_yaku_file)
        else:
            st.info("No hay archivos de datos de Yakus disponibles.")
    
    with tab2:
        if rurus_files:
            selected_ruru_file = st.selectbox(
                "Selecciona un archivo de datos de Rurus:",
                options=rurus_files,
                key="ruru_file_select"
            )
            
            if st.button("Cargar datos de Rurus", key="load_ruru_button"):
                process_file_export(selected_ruru_file)
        else:
            st.info("No hay archivos de datos de Rurus disponibles.")
    
    with tab3:
        if other_files:
            selected_other_file = st.selectbox(
                "Selecciona un archivo de otros datos:",
                options=other_files,
                key="other_file_select"
            )
            
            if st.button("Cargar otros datos", key="load_other_button"):
                process_file_export(selected_other_file)
        else:
            st.info("No hay otros archivos de datos disponibles.")

def process_file_export(file_name):
    """
    Procesa y muestra opciones de exportación para un archivo seleccionado.
    
    Args:
        file_name (str): Nombre del archivo a procesar y exportar
    """
    try:
        # Cargar datos
        data = load_data(file_name)
        
        if data is None:
            st.error(f"❌ Error al cargar el archivo {file_name}.")
            return
        
        # Mostrar información del archivo
        st.success(f"✅ Archivo cargado: {file_name}")
        st.write(f"Dimensiones: {data.shape[0]} filas x {data.shape[1]} columnas")
        
        # Mostrar vista previa de los datos
        with st.expander("Vista previa de los datos", expanded=True):
            st.dataframe(data.head(10))
        
        # Resumen estadístico básico
        with st.expander("Resumen estadístico"):
            # Mostrar solo para columnas numéricas
            numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_cols:
                st.write("Estadísticas para columnas numéricas:")
                st.dataframe(data[numeric_cols].describe())
            else:
                st.info("No hay columnas numéricas para mostrar estadísticas.")
        
        # Distribución por área si existe la columna
        area_cols = [col for col in data.columns if 'area' in col.lower() or 'área' in col.lower()]
        if area_cols:
            area_col = area_cols[0]  # Usar la primera columna de área encontrada
            
            with st.expander("Distribución por Área"):
                # Crear gráfico de distribución por área
                if pd.api.types.is_string_dtype(data[area_col]):
                    plt.figure(figsize=(10, 6))
                    area_counts = data[area_col].value_counts()
                    sns.barplot(x=area_counts.index, y=area_counts.values)
                    plt.xticks(rotation=45, ha='right')
                    plt.xlabel('Área')
                    plt.ylabel('Cantidad')
                    plt.title('Distribución por Área')
                    plt.tight_layout()
                    st.pyplot(plt)
                    
                    # Mostrar tabla de distribución
                    st.write("Distribución numérica por área:")
                    area_distribution = data[area_col].value_counts().reset_index()
                    area_distribution.columns = ['Área', 'Cantidad']
                    area_distribution['Porcentaje'] = (area_distribution['Cantidad'] / area_distribution['Cantidad'].sum() * 100).round(2)
                    st.dataframe(area_distribution)
        
        # Opciones de exportación
        st.write("### Opciones de exportación")
        
        # Configuración de exportación
        col1, col2 = st.columns(2)
        
        with col1:
            include_index = st.checkbox("Incluir índice en la exportación", value=False)
        
        with col2:
            if 'xlsx' in file_name:
                sheet_name = st.text_input("Nombre de la hoja (para Excel):", value="Datos")
        
        # Botones de exportación
        export_col1, export_col2 = st.columns(2)
        
        with export_col1:
            # Exportar a Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                data.to_excel(writer, index=include_index, sheet_name=sheet_name if 'sheet_name' in locals() else "Datos")
            excel_data = output.getvalue()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_base = file_name.replace(".pkl", "")
            st.download_button(
                label="📥 Exportar como Excel",
                data=excel_data,
                file_name=f"{file_base}_{timestamp}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        with export_col2:
            # Exportar a CSV
            csv = data.to_csv(index=include_index)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_base = file_name.replace(".pkl", "")
            st.download_button(
                label="📥 Exportar como CSV",
                data=csv,
                file_name=f"{file_base}_{timestamp}.csv",
                mime="text/csv"
            )
        
        # Opción para exportar subconjunto de columnas
        with st.expander("Exportar subconjunto de columnas"):
            selected_columns = st.multiselect(
                "Selecciona las columnas a exportar:",
                options=data.columns.tolist(),
                default=data.columns.tolist()
            )
            
            if selected_columns:
                subset_data = data[selected_columns]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Exportar a Excel (subconjunto)
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        subset_data.to_excel(writer, index=include_index, sheet_name=sheet_name if 'sheet_name' in locals() else "Datos")
                    excel_data = output.getvalue()
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    file_base = file_name.replace(".pkl", "")
                    st.download_button(
                        label="📥 Exportar subconjunto como Excel",
                        data=excel_data,
                        file_name=f"{file_base}_subset_{timestamp}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="subset_excel_button"
                    )
                
                with col2:
                    # Exportar a CSV (subconjunto)
                    csv = subset_data.to_csv(index=include_index)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    file_base = file_name.replace(".pkl", "")
                    st.download_button(
                        label="📥 Exportar subconjunto como CSV",
                        data=csv,
                        file_name=f"{file_base}_subset_{timestamp}.csv",
                        mime="text/csv",
                        key="subset_csv_button"
                    )
        
    except Exception as e:
        st.error(f"Error al procesar el archivo: {str(e)}")
        st.error("Por favor, intenta con otro archivo o contacta al administrador del sistema.")

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