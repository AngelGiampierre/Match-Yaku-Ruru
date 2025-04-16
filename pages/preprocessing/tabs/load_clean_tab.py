import streamlit as st
import pandas as pd
import numpy as np
import re
import sys
import os
import base64
from io import BytesIO
from datetime import datetime
import io

# Importamos componentes reutilizables
from pages.preprocessing.components.data_validators import validate_dni_column, validate_email_column
from pages.preprocessing.components.data_handlers import handle_dni_update, handle_sort_dataframe
from pages.preprocessing.components.file_handlers import export_dataframe

# Importamos las funciones de utilidad
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from utils.data_processors import (
    standardize_dni, validate_email, standardize_phone_number, 
    get_duplicated_dnis
)

# Agregar la raíz del proyecto al path de Python para importaciones absolutas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
from utils import load_data, save_data

def load_clean_tab():
    """
    Tab para cargar y limpiar datos iniciales.
    Permite cargar archivos CSV o Excel, limpiar datos básicos y exportarlos.
    """
    st.header("Carga y Limpieza de Datos")
    st.subheader("Sube, limpia y prepara tus datos para el procesamiento")
    
    # Sección de carga de archivo
    st.write("### 1. Selecciona el tipo de archivo a cargar")
    
    file_type = st.radio(
        "Tipo de datos a cargar:",
        options=["Datos de Yakus (mentores)", "Datos de Rurus (estudiantes)", "Datos de cursos/talleres"],
        horizontal=True
    )
    
    file_key = {
        "Datos de Yakus (mentores)": "yakus_file",
        "Datos de Rurus (estudiantes)": "rurus_file",
        "Datos de cursos/talleres": "courses_file"
    }[file_type]
    
    # Carga de archivo
    uploaded_file = st.file_uploader(
        f"Carga el archivo con {file_type} (.xlsx, .csv)",
        type=["xlsx", "csv"],
        key=file_key
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
            
            # Opciones de limpieza básica
            st.write("### 2. Opciones de limpieza básica")
            
            # Eliminar filas con valores nulos
            col1, col2 = st.columns(2)
            with col1:
                eliminar_nulos = st.checkbox("Eliminar filas con valores nulos en columnas clave", value=False)
                
                if eliminar_nulos:
                    columnas_clave = st.multiselect(
                        "Selecciona las columnas clave (se eliminarán filas con valores nulos en estas columnas):",
                        options=df.columns.tolist()
                    )
            
            # Convertir texto a minúsculas/mayúsculas
            with col2:
                caso_texto = st.radio(
                    "Convertir texto a:",
                    options=["No cambiar", "Minúsculas", "Mayúsculas", "Capitalizar (primera letra mayúscula)"],
                    horizontal=False,
                    index=0
                )
                
                if caso_texto != "No cambiar":
                    columnas_texto = st.multiselect(
                        "Selecciona las columnas de texto:",
                        options=[col for col in df.columns if df[col].dtype == 'object']
                    )
            
            # Ordenar datos
            ordenar_por = st.selectbox(
                "Ordenar datos por:",
                options=["No ordenar"] + df.columns.tolist()
            )
            
            if ordenar_por != "No ordenar":
                orden = st.radio(
                    "Orden:",
                    options=["Ascendente", "Descendente"],
                    horizontal=True,
                    index=0
                )
            
            # Botón para aplicar limpieza
            if st.button("Aplicar limpieza y procesar datos", key="clean_data_button"):
                with st.spinner("Procesando datos..."):
                    # Crear una copia para no modificar el original
                    processed_df = df.copy()
                    
                    # Aplicar eliminación de filas con nulos
                    if eliminar_nulos and columnas_clave:
                        initial_rows = len(processed_df)
                        processed_df = processed_df.dropna(subset=columnas_clave)
                        removed_rows = initial_rows - len(processed_df)
                        st.write(f"- Se eliminaron {removed_rows} filas con valores nulos en las columnas seleccionadas.")
                    
                    # Aplicar conversión de texto
                    if caso_texto != "No cambiar" and columnas_texto:
                        for col in columnas_texto:
                            if caso_texto == "Minúsculas":
                                processed_df[col] = processed_df[col].astype(str).str.lower()
                            elif caso_texto == "Mayúsculas":
                                processed_df[col] = processed_df[col].astype(str).str.upper()
                            elif caso_texto == "Capitalizar (primera letra mayúscula)":
                                processed_df[col] = processed_df[col].astype(str).str.title()
                        st.write(f"- Se convirtieron {len(columnas_texto)} columnas a {caso_texto.lower()}.")
                    
                    # Aplicar ordenamiento
                    if ordenar_por != "No ordenar":
                        processed_df = processed_df.sort_values(
                            by=ordenar_por,
                            ascending=(orden == "Ascendente")
                        )
                        st.write(f"- Datos ordenados por '{ordenar_por}' en orden {orden.lower()}.")
                    
                    # Guardar datos procesados
                    file_prefix = {
                        "yakus_file": "yakus_initial",
                        "rurus_file": "rurus_initial",
                        "courses_file": "courses_initial"
                    }[file_key]
                    
                    save_data(processed_df, f"{file_prefix}.pkl")
                    st.success(f"✅ Datos procesados guardados como {file_prefix}.pkl")
                    
                    # Descargar datos procesados
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Opción para descargar como Excel
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            processed_df.to_excel(writer, index=False, sheet_name='Datos')
                        excel_data = output.getvalue()
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        st.download_button(
                            label="📥 Descargar como Excel",
                            data=excel_data,
                            file_name=f"{file_prefix}_{timestamp}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    
                    with col2:
                        # Opción para descargar como CSV
                        csv = processed_df.to_csv(index=False)
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        st.download_button(
                            label="📥 Descargar como CSV",
                            data=csv,
                            file_name=f"{file_prefix}_{timestamp}.csv",
                            mime="text/csv"
                        )
                    
                    # Mostrar vista previa de los datos procesados
                    st.subheader("Vista previa de los datos procesados")
                    st.dataframe(processed_df.head())
                    
                    # Mostrar resumen del procesamiento
                    st.subheader("Resumen del procesamiento")
                    st.write(f"- Número de filas: {processed_df.shape[0]}")
                    st.write(f"- Número de columnas: {processed_df.shape[1]}")
                    
                    # Estadísticas de valores faltantes después del procesamiento
                    with st.expander("Estadísticas de valores faltantes después del procesamiento"):
                        missing_data_after = pd.DataFrame({
                            'Columna': processed_df.columns,
                            'Tipo de Dato': processed_df.dtypes.values,
                            'Valores Nulos': processed_df.isnull().sum().values,
                            'Porcentaje Nulos': (processed_df.isnull().sum().values / len(processed_df) * 100).round(2)
                        })
                        st.dataframe(missing_data_after.sort_values('Valores Nulos', ascending=False))
                    
                    # Siguiente paso
                    st.info("""
                        **Siguiente paso:** Ahora puedes proceder a la siguiente pestaña para continuar con el procesamiento específico 
                        según el tipo de datos (Yakus, Rurus o Cursos).
                    """)
            
        except Exception as e:
            st.error(f"Error al procesar el archivo: {str(e)}")
            st.error("Por favor, revisa el archivo e intenta nuevamente.")
    else:
        st.info("Por favor, carga un archivo para comenzar.")

def detect_important_columns(df):
    """Detecta automáticamente columnas importantes en el DataFrame."""
    suggested_columns = []
    for col in df.columns:
        if any(term in col.lower() for term in ['dni', 'pasaporte', 'nombre', 'correo', 'email', 'teléfono', 'área', 'area']):
            suggested_columns.append(col)
        # Columnas de disponibilidad (horarios)
        elif 'horarios' in col.lower() or 'disponib' in col.lower():
            suggested_columns.append(col)
        # Columnas de niveles, materias o áreas
        elif 'nivel' in col.lower() or 'grado' in col.lower() or 'asignaturas' in col.lower() or 'taller' in col.lower():
            suggested_columns.append(col)
        # Columna de filtro de candidatos
        elif 'filtro' in col.lower() or 'pasa' in col.lower():
            suggested_columns.append(col)
    
    # Eliminar duplicados en la lista de sugerencias
    return list(set(suggested_columns))

def detect_dni_column(columns):
    """Detecta la columna de DNI en una lista de columnas."""
    dni_columns = [col for col in columns if 'dni' in col.lower() or 'pasaporte' in col.lower()]
    
    if not dni_columns:
        st.warning("⚠️ No se detectó ninguna columna de DNI o Pasaporte. Por favor, verifica la selección de columnas.")
        return None
    else:
        return st.selectbox("Selecciona la columna de DNI/Pasaporte", dni_columns)

def detect_email_column(columns):
    """Detecta la columna de email en una lista de columnas."""
    email_columns = [col for col in columns if 'email' in col.lower() or 'correo' in col.lower()]
    
    if not email_columns:
        st.warning("⚠️ No se detectó ninguna columna de correo electrónico. Por favor, verifica la selección de columnas.")
        return None
    else:
        return st.selectbox("Selecciona la columna de correo electrónico", email_columns)

def show_filter_candidates_section(df, selected_columns):
    """Muestra la sección para filtrar candidatos."""
    st.subheader("Filtrar Candidatos")
    
    # Detectar columna de filtro
    filter_columns = [col for col in selected_columns if 'filtro' in col.lower() or 'pasa' in col.lower()]
    
    if filter_columns:
        filter_column = st.selectbox("Selecciona la columna de filtro", filter_columns)
        
        # Obtener valores únicos para mostrar opciones
        filter_values = df[filter_column].unique().tolist()
        
        # Filtrar por valor seleccionado
        filter_value = st.selectbox(
            "Filtrar por valor:", 
            options=["Todos"] + filter_values
        )
        
        if filter_value != "Todos":
            filtered_df = df[df[filter_column] == filter_value]
            st.info(f"📊 Registros después del filtro: {len(filtered_df)}")
            # Actualizar DataFrame en sesión
            st.session_state.processed_data = filtered_df

def show_sorting_section(df, selected_columns):
    """Muestra la sección para ordenar datos."""
    st.subheader("Ordenar por Área")
    
    # Buscar columnas potenciales de área
    area_columns = [col for col in df.columns if 'área' in col.lower() or 'area' in col.lower() or 'interesado' in col.lower()]
    
    if area_columns:
        # Permitir seleccionar columna de área
        sort_area_column = st.selectbox(
            "Selecciona la columna de área para ordenar:",
            options=area_columns,
            key="sort_area_column"
        )
        
        # Opción para ordenar
        if st.button("Ordenar por Área", key="sort_by_area_btn"):
            with st.spinner("Ordenando datos por área..."):
                # Usar la función específica para ordenamiento
                df = handle_sort_dataframe(
                    df, 
                    sort_column=sort_area_column, 
                    ascending=True, 
                    sort_name="área"
                )
                
                # Mostrar mensaje adicional
                st.success(f"✅ Datos ordenados por área. El ordenamiento se ha guardado en la sesión.")
                st.info("ℹ️ Este ordenamiento se mantendrá cuando exportes los datos.")
                
                # Ofrecer recargar para ver el resultado
                if st.button("Ver resultado ordenado", key="view_sorted_result"):
                    st.rerun()
    else:
        st.info("ℹ️ No se detectaron columnas de área para ordenar los datos")
    
    # Opción adicional para ordenar por cualquier columna
    st.subheader("Ordenar por Otra Columna")
    
    # Seleccionar columna para ordenar
    sort_column = st.selectbox(
        "Selecciona una columna para ordenar:",
        options=df.columns.tolist(),
        key="sort_column"
    )
    
    # Dirección del ordenamiento
    sort_direction = st.radio(
        "Dirección:",
        options=["Ascendente", "Descendente"],
        key="sort_direction"
    )
    
    if st.button("Ordenar Datos", key="sort_data_btn"):
        with st.spinner("Ordenando datos..."):
            # Determinar dirección del ordenamiento
            ascending = sort_direction == "Ascendente"
            
            # Usar la función específica para ordenamiento
            df = handle_sort_dataframe(
                df, 
                sort_column=sort_column, 
                ascending=ascending,
                sort_name=sort_direction.lower()
            )
            
            # Mostrar mensaje adicional
            st.success(f"✅ Datos ordenados por '{sort_column}' ({sort_direction.lower()}). El ordenamiento se ha guardado en la sesión.")
            st.info("ℹ️ Este ordenamiento se mantendrá cuando exportes los datos.")
            
            # Ofrecer recargar para ver el resultado
            if st.button("Ver resultado ordenado", key="view_custom_sorted"):
                st.rerun()

def show_export_section(df, dni_column=None):
    """Muestra la sección para exportar datos directamente desde el Paso 1."""
    st.subheader("Exportar Datos Procesados (Paso 1)")
    
    export_format = st.radio(
        "Formato de exportación:",
        options=["Excel (.xlsx)", "CSV (.csv)"],
        key="export_format_step1"
    )
    
    include_validation_step1 = st.checkbox(
        "Incluir columnas de validación (DNI_Validado, etc.)", 
        value=True,
        key="include_validation_step1"
    )
    
    # Crear nombre de archivo
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    default_filename = f"yakus_procesados_paso1_{timestamp}"
    export_filename_step1 = st.text_input("Nombre del archivo:", value=default_filename, key="export_filename_step1")
    
    if st.button("Exportar Datos del Paso 1"):
        # Verificar que tenemos datos procesados en la sesión
        if st.session_state.processed_data is not None:
            # Hacer una copia explícita para la exportación
            export_df = st.session_state.processed_data.copy()
            
            # Mostrar información detallada sobre los datos a exportar
            st.subheader("Verificación de Datos a Exportar")
            
            # Información sobre el estado de los datos
            st.info(f"📊 Exportando {len(export_df)} registros con todas las modificaciones aplicadas")
            
            if st.session_state.last_action:
                st.info(f"🔄 Última acción realizada: {st.session_state.last_action}")
            
            # Mostrar los 5 primeros registros para verificación
            st.write("Muestra de los datos que se exportarán:")
            st.dataframe(export_df.head(5))
            
            # Buscar columna de DNI para verificar ediciones
            if dni_column and dni_column in export_df.columns:
                st.write(f"Verificando columna de DNI '{dni_column}':")
                st.write(export_df[dni_column].head(10).tolist())
            
            # Confirmar antes de exportar
            if st.checkbox("Confirmar exportación", value=True, key="confirm_export"):
                # Usar el componente reutilizable para exportación
                if not include_validation_step1:
                    validation_cols = [col for col in export_df.columns if '_Validado' in col or '_Normalizado' in col]
                    if validation_cols:
                        export_df = export_df.drop(columns=validation_cols)
                
                # Exportar el DataFrame
                export_dataframe(export_df, export_filename_step1, export_format)
            else:
                st.warning("⚠️ Por favor confirma la exportación para descargar el archivo")
        else:
            st.error("❌ No hay datos procesados en la sesión para exportar")
            
            # Si tenemos filtered_df local pero no en la sesión
            if 'filtered_df' in locals():
                st.warning("Se encontró un DataFrame local pero no está en la sesión. Intentando recuperar...")
                
                # Intentar guardar el DataFrame local en la sesión
                st.session_state.processed_data = df.copy()
                
                st.info("DataFrame guardado en la sesión. Por favor, intenta exportar nuevamente.")
                
                if st.button("Intentar nuevamente", key="retry_export"):
                    st.rerun() 