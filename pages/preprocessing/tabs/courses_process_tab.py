import streamlit as st
import pandas as pd
import numpy as np
import io
import re
from datetime import datetime
import sys
import os

# Agregar la raíz del proyecto al path de Python para importaciones absolutas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from utils import load_data, save_data

def courses_process_tab():
    """
    Tab para procesar y estandarizar los datos de cursos.
    """
    st.header("Preprocesamiento de Datos de Cursos")
    st.subheader("Carga y estandariza información de cursos")
    
    # Carga de archivo
    uploaded_file = st.file_uploader(
        "Carga el archivo con datos de cursos (.xlsx, .csv)",
        type=["xlsx", "csv"],
        key="courses_file_uploader"
    )
    
    if uploaded_file is not None:
        try:
            # Determinar el tipo de archivo y leer los datos
            file_extension = uploaded_file.name.split(".")[-1].lower()
            
            if file_extension == "csv":
                df = pd.read_csv(uploaded_file)
            elif file_extension == "xlsx":
                df = pd.read_excel(uploaded_file)
            
            # Mostrar información básica del archivo
            st.success(f"✅ Archivo cargado correctamente: {uploaded_file.name}")
            st.write(f"Dimensiones del DataFrame: {df.shape[0]} filas x {df.shape[1]} columnas")
            
            # Vista previa de los datos
            with st.expander("Vista previa de los datos cargados", expanded=True):
                st.dataframe(df.head())
            
            # Mostrar estadísticas de valores faltantes
            with st.expander("Estadísticas de valores faltantes"):
                missing_data = pd.DataFrame({
                    'Columna': df.columns,
                    'Tipo de Dato': df.dtypes.values,
                    'Valores Nulos': df.isnull().sum().values,
                    'Porcentaje Nulos': (df.isnull().sum().values / len(df) * 100).round(2)
                })
                st.dataframe(missing_data.sort_values('Valores Nulos', ascending=False))
            
            # Opciones de estandarización
            st.subheader("Opciones de estandarización de cursos")
            
            # Detectar columnas de curso
            curso_cols = [col for col in df.columns if any(term in col.lower() for term in ['curso', 'materia', 'asignatura', 'taller'])]
            
            # Seleccionar columna de curso a estandarizar
            if curso_cols:
                curso_col = st.selectbox(
                    "Selecciona la columna con nombres de cursos a estandarizar:",
                    options=curso_cols
                )
                
                # Mostrar valores únicos en la columna
                unique_values = df[curso_col].dropna().unique()
                st.write(f"Valores únicos en la columna seleccionada ({len(unique_values)}):")
                st.write(", ".join([str(val) for val in unique_values[:20]]) + ("..." if len(unique_values) > 20 else ""))
                
                # Opciones de estandarización
                estandarizar = st.checkbox("Estandarizar nombres de cursos", value=True)
                
                # Procesamiento de datos
                if st.button("Procesar datos", key="process_courses_button"):
                    with st.spinner("Procesando datos de cursos..."):
                        # En el futuro, implementar la lógica de estandarización
                        processed_df = df.copy()
                        
                        if estandarizar and curso_col:
                            # Ejemplo simple de estandarización (en el futuro, implementar una lógica más compleja)
                            processed_df[curso_col] = processed_df[curso_col].str.strip().str.capitalize()
                        
                        # Guardar datos procesados
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # Opción para descargar como Excel
                            output = io.BytesIO()
                            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                                processed_df.to_excel(writer, index=False, sheet_name='Cursos')
                            excel_data = output.getvalue()
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            st.download_button(
                                label="📥 Descargar como Excel",
                                data=excel_data,
                                file_name=f"cursos_procesados_{timestamp}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                        
                        with col2:
                            # Opción para descargar como CSV
                            csv = processed_df.to_csv(index=False)
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            st.download_button(
                                label="📥 Descargar como CSV",
                                data=csv,
                                file_name=f"cursos_procesados_{timestamp}.csv",
                                mime="text/csv"
                            )
                        
                        # Guardar en la carpeta temporal del sistema
                        save_data(processed_df, "courses_processed.pkl")
                        st.success("✅ Datos procesados guardados en la memoria temporal del sistema")
                        
                        # Mostrar vista previa de los datos procesados
                        st.subheader("Vista previa de los datos procesados")
                        st.dataframe(processed_df.head())
            else:
                st.warning("No se detectaron columnas que parezcan contener nombres de cursos.")
        
        except Exception as e:
            st.error(f"Error al procesar el archivo: {str(e)}")
    else:
        st.info("Por favor, carga un archivo con datos de cursos para comenzar.") 