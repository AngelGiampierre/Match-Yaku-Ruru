import streamlit as st
import pandas as pd
import numpy as np
import re
import sys
import os
import base64
from io import BytesIO

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

def load_and_clean_tab():
    """Tab para carga de datos y limpieza de DNI/Pasaporte y Email"""
    st.header("Carga y Limpieza de Datos")
    
    # Verificar el estado actual de los datos procesados
    if st.session_state.processed_data is not None:
        st.success(f"✅ Datos procesados disponibles: {len(st.session_state.processed_data)} registros")
        
        # Opción para ver el estado actual de los datos
        if st.checkbox("Mostrar estado actual de los datos procesados", key="show_current_state"):
            st.write("Primeros 5 registros de los datos procesados:")
            st.dataframe(st.session_state.processed_data.head(5))
            
            # Verificar si hay columnas validadas
            validated_cols = [col for col in st.session_state.processed_data.columns if '_Validado' in col]
            if validated_cols:
                st.info(f"Columnas validadas disponibles: {', '.join(validated_cols)}")
    
    # Cargar archivo Excel/CSV
    uploaded_file = st.file_uploader(
        "Selecciona el archivo Excel/CSV con los datos de yakus", 
        type=["xlsx", "csv"], 
        key="file_uploader_1"
    )
    
    if uploaded_file is not None:
        try:
            # Cargar datos según tipo de archivo
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # Convertir todas las columnas de texto a string para evitar problemas con PyArrow
            for col in df.select_dtypes(include=['object']).columns:
                df[col] = df[col].astype(str)
            
            # Guardar datos originales en sesión
            st.session_state.yakus_data = df.copy()
            
            # Mostrar información básica
            st.success(f"✅ Archivo cargado: {uploaded_file.name}")
            st.info(f"📊 Registros: {len(df)} | Columnas: {len(df.columns)}")
            
            # Permitir seleccionar las columnas a mantener
            st.subheader("Selección de Columnas")
            
            # Detectar automáticamente columnas críticas
            suggested_columns = detect_important_columns(df)
            
            # Permitir al usuario seleccionar columnas
            selected_columns = st.multiselect(
                "Selecciona las columnas que deseas conservar",
                options=df.columns.tolist(),
                default=suggested_columns,
                key="column_selector"
            )
            
            if selected_columns:
                # IMPORTANTE: Verificar si ya tenemos datos procesados en la sesión
                # Si es así, usamos esos datos en lugar de recrear el DataFrame
                if st.session_state.processed_data is not None:
                    # Usar los datos procesados existentes
                    filtered_df = st.session_state.processed_data.copy()
                    st.success("✅ Usando datos procesados guardados en la sesión")
                    st.info(f"Los datos ya contienen ediciones previas y ordenamiento")
                else:
                    # Crear DataFrame nuevo con columnas seleccionadas
                    filtered_df = df[selected_columns].copy()
                    
                    # Convertir todas las columnas de texto a string para evitar problemas con PyArrow
                    for col in filtered_df.select_dtypes(include=['object']).columns:
                        filtered_df[col] = filtered_df[col].astype(str)
                    
                    # Guardar en la sesión inmediatamente
                    st.session_state.processed_data = filtered_df.copy()
                    st.success("✅ Se ha creado un nuevo DataFrame procesado")
            
            # Contenedor para validación de datos
            validation_container = st.container()
            
            with validation_container:
                # Organizar las validaciones en tabs para mejor visualización
                val_tab1, val_tab2 = st.tabs(["DNI/Pasaporte", "Correo Electrónico"])
                
                # ---- VALIDACIÓN DE DNI/PASAPORTE ----
                with val_tab1:
                    # Utilizar el componente reutilizable para validación de DNI
                    if selected_columns:
                        dni_column = detect_dni_column(selected_columns)
                        if dni_column:
                            filtered_df = validate_dni_column(filtered_df, dni_column)
                
                # ---- VALIDACIÓN DE CORREO ELECTRÓNICO ----
                with val_tab2:
                    # Utilizar el componente reutilizable para validación de email
                    if selected_columns:
                        email_column = detect_email_column(selected_columns)
                        if email_column:
                            filtered_df = validate_email_column(filtered_df, email_column)
            
            # Filtrar por aprobados/rechazados
            show_filter_candidates_section(filtered_df, selected_columns)
            
            # Guardar el DataFrame procesado en la sesión
            st.session_state.processed_data = filtered_df
            
            # --- SECCIÓN DE ORDENAMIENTO ---
            show_sorting_section(filtered_df, selected_columns)
            
            # Mostrar vista previa
            st.subheader("Vista Previa de Datos Procesados")
            st.dataframe(filtered_df.head(10))
            
            # Botón para exportar datos procesados directamente desde el Paso 1
            show_export_section(filtered_df, dni_column if 'dni_column' in locals() else None)
        
        except Exception as e:
            st.error(f"❌ Error al procesar el archivo: {str(e)}")

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