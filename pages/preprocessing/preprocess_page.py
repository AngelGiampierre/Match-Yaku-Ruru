import streamlit as st
import pandas as pd
import numpy as np
import re
import os
import sys
import base64
from io import BytesIO

# Importamos navegación lateral
from components.sidebar import sidebar_navigation

# Importamos las funciones de utilidad
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from utils.data_processors import (
    standardize_dni, validate_email, standardize_phone_number, 
    get_duplicated_dnis, filter_by_area_and_selection
)

def preprocess_main():
    """
    Página principal para la funcionalidad de Preprocesamiento
    """
    # Configurar la navegación lateral
    sidebar_navigation()
    
    st.markdown("<h1 class='main-header'>Preprocesamiento de Datos</h1>", unsafe_allow_html=True)
    st.markdown("<p class='info-text'>Limpia y prepara tus datos antes de realizar el match</p>", unsafe_allow_html=True)
    
    # Inicializar variables de estado si no existen
    for key in ['yakus_data', 'processed_data', 'selected_data', 'export_data']:
        if key not in st.session_state:
            st.session_state[key] = None
    
    # Crear tabs para las diferentes funcionalidades
    tab1, tab2, tab3 = st.tabs([
        "1. Carga y Limpieza de Datos", 
        "2. Selección por Área", 
        "3. Exportación de Datos"
    ])
    
    with tab1:
        load_and_clean_tab()
    
    with tab2:
        selection_by_area_tab()
    
    with tab3:
        export_tab()

def load_and_clean_tab():
    """Tab para carga de datos y limpieza de DNI/Pasaporte y Email"""
    st.header("Carga y Limpieza de Datos")
    
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
            
            # Guardar datos en sesión
            st.session_state.yakus_data = df
            
            # Mostrar información básica
            st.success(f"✅ Archivo cargado: {uploaded_file.name}")
            st.info(f"📊 Registros: {len(df)} | Columnas: {len(df.columns)}")
            
            # Permitir seleccionar las columnas a mantener
            st.subheader("Selección de Columnas")
            
            # Detectar automáticamente columnas críticas
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
            suggested_columns = list(set(suggested_columns))
            
            # Permitir al usuario seleccionar columnas
            selected_columns = st.multiselect(
                "Selecciona las columnas que deseas conservar",
                options=df.columns.tolist(),
                default=suggested_columns,
                key="column_selector"
            )
            
            if selected_columns:
                # Crear DataFrame con columnas seleccionadas
                filtered_df = df[selected_columns].copy()
                
                # Convertir todas las columnas de texto a string para evitar problemas con PyArrow
                for col in filtered_df.select_dtypes(include=['object']).columns:
                    filtered_df[col] = filtered_df[col].astype(str)
                
                # Contenedor para validación de datos
                validation_container = st.container()
                
                with validation_container:
                    # Organizar las validaciones en tabs para mejor visualización
                    val_tab1, val_tab2 = st.tabs(["DNI/Pasaporte", "Correo Electrónico"])
                    
                    # ---- VALIDACIÓN DE DNI/PASAPORTE ----
                    with val_tab1:
                        st.subheader("Limpieza de DNI/Pasaporte")
                        
                        # Detectar columna de DNI
                        dni_columns = [col for col in selected_columns if 'dni' in col.lower() or 'pasaporte' in col.lower()]
                        
                        if not dni_columns:
                            st.warning("⚠️ No se detectó ninguna columna de DNI o Pasaporte. Por favor, verifica la selección de columnas.")
                        else:
                            dni_column = st.selectbox("Selecciona la columna de DNI/Pasaporte", dni_columns)
                            
                            # Convertir explícitamente a string la columna DNI para evitar problemas con PyArrow
                            filtered_df[dni_column] = filtered_df[dni_column].astype(str)
                            
                            # Validar y estandarizar DNIs
                            with st.spinner("Procesando DNIs..."):
                                filtered_df['DNI_Validado'] = filtered_df[dni_column].apply(standardize_dni)
                                
                                # Detectar DNIs con problemas
                                invalid_dnis = filtered_df[filtered_df['DNI_Validado'].str.contains('ERROR')]
                                
                                if not invalid_dnis.empty:
                                    st.warning(f"⚠️ Se encontraron {len(invalid_dnis)} DNIs con formato incorrecto:")
                                    
                                    # Mostrar tabla de DNIs inválidos
                                    st.dataframe(invalid_dnis[[dni_column, 'DNI_Validado']])
                                    
                                    # Ofrecer opciones al usuario
                                    dni_edit_option = st.radio(
                                        "¿Qué deseas hacer con los DNIs inválidos?",
                                        options=["Editar manualmente", "Conservar valores originales (pueden ser carnets de extranjería u otros documentos válidos)"],
                                        index=1,
                                        key="dni_edit_option_main"
                                    )
                                    
                                    if dni_edit_option == "Conservar valores originales (pueden ser carnets de extranjería u otros documentos válidos)":
                                        # Conservar los valores originales para carnets de extranjería y otros documentos
                                        st.info("ℹ️ Se conservarán los valores originales de los documentos de identidad")
                                        for idx in invalid_dnis.index:
                                            # Usar el valor original del documento como valor validado
                                            original_value = filtered_df.loc[idx, dni_column]
                                            filtered_df.loc[idx, 'DNI_Validado'] = original_value
                                        st.success("✅ Todos los valores originales han sido conservados")
                                    else:
                                        # Ofrecer corrección manual
                                        st.subheader("Corrección Manual de DNI")
                                        
                                        # Seleccionar índice a corregir
                                        index_options = invalid_dnis.index.tolist()
                                        index_to_fix = st.selectbox(
                                            "Selecciona el índice a corregir:", 
                                            index_options,
                                            key="dni_index_selector"
                                        )
                                        
                                        # Valor actual y nuevo valor
                                        current_value = filtered_df.loc[index_to_fix, dni_column]
                                        new_value = st.text_input(
                                            "Nuevo valor:", 
                                            value=current_value,
                                            key="dni_value_input"
                                        )
                                        
                                        if st.button("Actualizar DNI", key="update_dni_btn"):
                                            filtered_df.loc[index_to_fix, dni_column] = new_value
                                            filtered_df.loc[index_to_fix, 'DNI_Validado'] = standardize_dni(new_value)
                                            st.success(f"✅ DNI actualizado correctamente")
                                else:
                                    st.success("✅ Todos los DNIs tienen un formato válido")
                                
                                # Verificar duplicados
                                duplicates = get_duplicated_dnis(filtered_df, dni_column)
                                
                                if not duplicates.empty:
                                    st.warning(f"⚠️ Se encontraron {len(duplicates)} DNIs duplicados:")
                                    
                                    # Detectar columnas para mejor visualización
                                    display_columns = [dni_column, 'DNI_Validado']
                                    
                                    # Añadir columnas relevantes para verificar si es la misma persona
                                    nombre_cols = [col for col in filtered_df.columns if 'nombre' in col.lower() or 'apellido' in col.lower()]
                                    if nombre_cols:
                                        display_columns.extend(nombre_cols)
                                    
                                    # Añadir columna de email si existe
                                    email_cols = [col for col in filtered_df.columns if 'email' in col.lower() or 'correo' in col.lower()]
                                    if email_cols:
                                        display_columns.extend(email_cols)
                                    
                                    # Añadir columna de área si existe
                                    area_cols = [col for col in filtered_df.columns if 'área' in col.lower() or 'area' in col.lower()]
                                    if area_cols:
                                        display_columns.extend(area_cols)
                                    
                                    # Mostrar tabla de DNIs duplicados con información ampliada
                                    st.dataframe(duplicates[display_columns])
                                    
                                    st.info("ℹ️ Verifica si los duplicados corresponden a la misma persona aplicando a diferentes áreas o si son errores de datos.")
                                else:
                                    st.success("✅ No se encontraron DNIs duplicados")
                    
                    # ---- VALIDACIÓN DE CORREO ELECTRÓNICO ----
                    with val_tab2:
                        st.subheader("Validación de Correo Electrónico")
                        
                        # Detectar columna de email
                        email_columns = [col for col in selected_columns if 'email' in col.lower() or 'correo' in col.lower()]
                        
                        if not email_columns:
                            st.warning("⚠️ No se detectó ninguna columna de correo electrónico. Por favor, verifica la selección de columnas.")
                        else:
                            email_column = st.selectbox("Selecciona la columna de correo electrónico", email_columns)
                            
                            # Validar y estandarizar emails
                            with st.spinner("Procesando correos electrónicos..."):
                                filtered_df['Email_Validado'] = filtered_df[email_column].apply(validate_email)
                                
                                # Detectar emails con problemas
                                invalid_emails = filtered_df[filtered_df['Email_Validado'].str.contains('ERROR')]
                                
                                if not invalid_emails.empty:
                                    st.warning(f"⚠️ Se encontraron {len(invalid_emails)} correos con formato incorrecto:")
                                    
                                    # Mostrar tabla de emails inválidos
                                    st.dataframe(invalid_emails[[email_column, 'Email_Validado']])
                                    
                                    # Ofrecer corrección manual
                                    st.subheader("Corrección Manual de Correo")
                                    
                                    # Seleccionar índice a corregir
                                    index_options = invalid_emails.index.tolist()
                                    index_to_fix = st.selectbox(
                                        "Selecciona el índice a corregir:", 
                                        index_options,
                                        key="email_index_selector"
                                    )
                                    
                                    # Valor actual y nuevo valor
                                    current_value = filtered_df.loc[index_to_fix, email_column]
                                    new_value = st.text_input(
                                        "Nuevo valor:", 
                                        value=current_value,
                                        key="email_value_input"
                                    )
                                    
                                    if st.button("Actualizar Correo", key="update_email_btn"):
                                        filtered_df.loc[index_to_fix, email_column] = new_value
                                        filtered_df.loc[index_to_fix, 'Email_Validado'] = validate_email(new_value)
                                        st.success(f"✅ Correo actualizado correctamente")
                                else:
                                    st.success("✅ Todos los correos tienen un formato válido")
                                
                                # Verificar duplicados
                                email_duplicates = filtered_df[filtered_df.duplicated(subset=[email_column], keep=False)]
                                
                                if not email_duplicates.empty:
                                    st.warning(f"⚠️ Se encontraron {len(email_duplicates)} correos duplicados:")
                                    st.dataframe(email_duplicates[[email_column, 'Email_Validado']])
                                else:
                                    st.success("✅ No se encontraron correos duplicados")
                
                # Filtrar por aprobados/rechazados
                st.subheader("Filtrar Candidatos")
                
                # Detectar columna de filtro
                filter_columns = [col for col in selected_columns if 'filtro' in col.lower() or 'pasa' in col.lower()]
                
                if filter_columns:
                    filter_column = st.selectbox("Selecciona la columna de filtro", filter_columns)
                    
                    # Obtener valores únicos para mostrar opciones
                    filter_values = filtered_df[filter_column].unique().tolist()
                    
                    # Filtrar por valor seleccionado
                    filter_value = st.selectbox(
                        "Filtrar por valor:", 
                        options=["Todos"] + filter_values
                    )
                    
                    if filter_value != "Todos":
                        filtered_df = filtered_df[filtered_df[filter_column] == filter_value]
                        st.info(f"📊 Registros después del filtro: {len(filtered_df)}")
                
                # Guardar el DataFrame procesado en la sesión
                st.session_state.processed_data = filtered_df
                
                # --- NUEVA SECCIÓN: ORDENAMIENTO POR ÁREA ---
                st.subheader("Ordenar por Área")
                
                # Buscar columnas potenciales de área
                area_columns = [col for col in filtered_df.columns if 'área' in col.lower() or 'area' in col.lower() or 'interesado' in col.lower()]
                
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
                            # Ordenar DataFrame
                            filtered_df = filtered_df.sort_values(by=sort_area_column)
                            
                            # Actualizar DataFrame en sesión
                            st.session_state.processed_data = filtered_df
                            
                            st.success("✅ Datos ordenados por área")
                else:
                    st.info("ℹ️ No se detectaron columnas de área para ordenar los datos")
                
                # Opción adicional para ordenar por cualquier columna
                st.subheader("Ordenar por Otra Columna")
                
                # Seleccionar columna para ordenar
                sort_column = st.selectbox(
                    "Selecciona una columna para ordenar:",
                    options=filtered_df.columns.tolist(),
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
                        # Ordenar DataFrame
                        ascending = sort_direction == "Ascendente"
                        filtered_df = filtered_df.sort_values(by=sort_column, ascending=ascending)
                        
                        # Actualizar DataFrame en sesión
                        st.session_state.processed_data = filtered_df
                        
                        st.success(f"✅ Datos ordenados por '{sort_column}' ({sort_direction.lower()})")
                
                # Mostrar vista previa
                st.subheader("Vista Previa de Datos Procesados")
                st.dataframe(filtered_df.head(10))
                
                # Botón para exportar datos procesados directamente desde el Paso 1
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
                    # Eliminar columnas de validación si no se desean incluir
                    export_df = filtered_df.copy()
                    
                    # Asegurarnos que todas las columnas de texto sean de tipo string
                    for col in export_df.select_dtypes(include=['object']).columns:
                        export_df[col] = export_df[col].astype(str)
                    
                    if not include_validation_step1:
                        validation_cols = [col for col in export_df.columns if '_Validado' in col or '_Normalizado' in col]
                        if validation_cols:
                            export_df = export_df.drop(columns=validation_cols)
                    
                    # Exportar según formato
                    if export_format == "Excel (.xlsx)":
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            export_df.to_excel(writer, sheet_name='Datos', index=False)
                        
                        output.seek(0)
                        b64 = base64.b64encode(output.read()).decode()
                        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{export_filename_step1}.xlsx">📥 Descargar archivo Excel</a>'
                        st.markdown(href, unsafe_allow_html=True)
                    
                    else:  # CSV
                        csv = export_df.to_csv(index=False)
                        b64 = base64.b64encode(csv.encode()).decode()
                        href = f'<a href="data:text/csv;base64,{b64}" download="{export_filename_step1}.csv">📥 Descargar archivo CSV</a>'
                        st.markdown(href, unsafe_allow_html=True)
                    
                    st.success(f"✅ Archivo '{export_filename_step1}' listo para descargar")
        
        except Exception as e:
            st.error(f"❌ Error al procesar el archivo: {str(e)}")

def selection_by_area_tab():
    """Tab para selección de yakus por área"""
    st.header("Selección de Yakus por Área")
    
    # Nueva sección para seleccionar la fuente de datos
    st.subheader("Fuente de Datos")
    
    # Variable para controlar si tenemos datos válidos para trabajar
    datos_validos = False
    df = None
    
    # Determinar la fuente de datos
    if st.session_state.processed_data is not None:
        # Si hay datos de la sesión actual, ofrecer usarlos como opción
        usar_datos_sesion = st.checkbox(
            "Usar datos procesados del paso anterior", 
            value=True,
            key="usar_datos_sesion"
        )
        
        if usar_datos_sesion:
            df = st.session_state.processed_data
            datos_validos = True
            st.success("✅ Usando datos procesados del paso anterior")
            st.info(f"📊 Registros: {len(df)} | Columnas: {len(df.columns)}")
    
    # Siempre ofrecer la opción de cargar archivo de datos
    if df is None or not usar_datos_sesion:
        st.subheader("Cargar Datos Procesados")
        uploaded_processed = st.file_uploader(
            "Selecciona el archivo Excel/CSV con los datos procesados", 
            type=["xlsx", "csv"],
            key="file_uploader_processed"
        )
        
        if uploaded_processed is not None:
            try:
                # Cargar datos según tipo de archivo
                if uploaded_processed.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_processed)
                else:
                    df = pd.read_excel(uploaded_processed)
                
                # Convertir todas las columnas de texto a string para evitar problemas con PyArrow
                for col in df.select_dtypes(include=['object']).columns:
                    df[col] = df[col].astype(str)
                
                datos_validos = True
                st.success(f"✅ Archivo de datos procesados cargado: {uploaded_processed.name}")
                st.info(f"📊 Registros: {len(df)} | Columnas: {len(df.columns)}")
                
                # Actualizar datos procesados en la sesión
                st.session_state.processed_data = df
            
            except Exception as e:
                st.error(f"❌ Error al procesar el archivo: {str(e)}")
    
    # Si no tenemos datos válidos todavía, no continuamos
    if not datos_validos:
        st.warning("⚠️ Necesitas cargar datos procesados para continuar")
        return
    
    # A partir de aquí, continuamos con el proceso de selección por área
    
    # Detectar columna de DNI en datos procesados - MOVER AQUÍ PARA EVITAR EL ERROR
    dni_column = None
    if 'DNI_Validado' in df.columns:
        dni_column = 'DNI_Validado'
    else:
        # Buscar columna de DNI con detección mejorada
        dni_cols = []
        for col in df.columns:
            # Normalizar nombre de columna para comparación (quitar espacios, convertir a minúsculas)
            col_norm = col.strip().lower()
            if 'dni' in col_norm or 'pasaporte' in col_norm or 'documento' in col_norm or 'doc' in col_norm:
                dni_cols.append(col)
        
        # Si encontramos columnas de DNI, usar la primera
        if dni_cols:
            dni_column = dni_cols[0]
            st.success(f"✅ Se detectó la columna de DNI en datos principales: '{dni_column}'")
        else:
            # Si aún no encuentra, ofrecer selección manual
            st.warning("⚠️ No se detectó automáticamente una columna de DNI en los datos principales. Por favor, selecciona la columna manualmente.")
            
            dni_column = st.selectbox(
                "Selecciona la columna que contiene los DNIs en los datos principales:",
                options=df.columns.tolist(),
                key="dni_column_main_data"
            )
    
    # Verificar nuevamente que la columna existe
    if dni_column not in df.columns:
        st.error(f"❌ La columna '{dni_column}' no existe en los datos procesados")
        return
    
    # Convertir explícitamente a string la columna DNI de los datos procesados
    df[dni_column] = df[dni_column].astype(str)
    
    # VISUALIZACIÓN PARCIAL DE DATOS PRINCIPALES
    with st.expander("Visualización de Datos Principales", expanded=False):
        st.subheader("Archivo de Datos Principales")
        st.dataframe(df)
    
    # Cargar archivo de selección
    st.subheader("Archivo de DNIs Seleccionados")
    
    # Inicializar selection_df como None para verificar después si se ha cargado
    selection_df = None
    
    uploaded_selection = st.file_uploader(
        "Selecciona el archivo Excel/CSV con los DNIs de yakus seleccionados", 
        type=["xlsx", "csv"],
        key="file_uploader_2"
    )
    
    if uploaded_selection is not None:
        try:
            # Cargar datos según tipo de archivo
            if uploaded_selection.name.endswith('.csv'):
                selection_df = pd.read_csv(uploaded_selection)
            else:
                selection_df = pd.read_excel(uploaded_selection)
            
            # Convertir todas las columnas de texto a string para evitar problemas con PyArrow
            for col in selection_df.select_dtypes(include=['object']).columns:
                selection_df[col] = selection_df[col].astype(str)
            
            # Guardar datos en sesión
            st.session_state.selected_data = selection_df
            
            st.success(f"✅ Archivo de selección cargado: {uploaded_selection.name}")
            st.info(f"📊 Registros: {len(selection_df)} | Columnas: {len(selection_df.columns)}")
            
            # VISUALIZACIÓN DEL ARCHIVO DE SELECCIÓN - MOVER AQUÍ DENTRO DEL BLOQUE CONDICIONAL
            with st.expander("Visualización de Archivo de Selección", expanded=False):
                st.subheader("Archivo de DNIs Seleccionados")
                st.dataframe(selection_df)
            
            # Mostrar columnas disponibles en el archivo de selección
            st.subheader("Columna de DNI en Archivo de Selección")
            
            # Detectar columnas de DNI
            selection_dni_cols = [col for col in selection_df.columns if 'dni' in col.lower() or 'pasaporte' in col.lower() or 'documento' in col.lower() or 'doc' in col.lower()]
            
            if not selection_dni_cols:
                st.warning("⚠️ No se detectó ninguna columna de DNI o Pasaporte en el archivo de selección")
                # Mostrar todas las columnas para selección manual
                selection_dni_col = st.selectbox(
                    "Selecciona la columna que contiene los DNIs/Pasaportes en el archivo de selección:",
                    options=selection_df.columns.tolist()
                )
            else:
                selection_dni_col = st.selectbox(
                    "Selecciona la columna de DNI/Pasaporte en el archivo de selección:",
                    options=selection_dni_cols
                )
            
            # Convertir explícitamente a string la columna DNI del archivo de selección
            selection_df[selection_dni_col] = selection_df[selection_dni_col].astype(str)
            
            # NUEVA SECCIÓN: Validar DNIs en la lista de seleccionados
            with st.expander("Validación de DNIs en Lista de Seleccionados", expanded=True):
                st.subheader("Validación de DNIs")
                
                # Aplicar la función de validación
                selection_df['DNI_Validado'] = selection_df[selection_dni_col].apply(standardize_dni)
                
                # Detectar DNIs inválidos
                invalid_dnis_mask = selection_df['DNI_Validado'].str.contains('ERROR', na=False)
                
                if invalid_dnis_mask.any():
                    invalid_dnis_df = selection_df[invalid_dnis_mask].copy()
                    
                    st.warning(f"⚠️ Se encontraron {len(invalid_dnis_df)} DNIs inválidos en la lista de seleccionados")
                    
                    # Buscar y añadir nombre si existe
                    nombre_cols = []
                    for col in selection_df.columns:
                        col_lower = col.lower()
                        if 'nombre' in col_lower or 'apellido' in col_lower:
                            nombre_cols.append(col)
                    
                    # Crear columnas a mostrar
                    display_cols = [selection_dni_col, 'DNI_Validado']
                    if nombre_cols:
                        display_cols.extend(nombre_cols)
                        st.info("ℹ️ Se muestran los nombres para facilitar la identificación")
                    
                    # Mostrar DNIs inválidos en una tabla
                    st.dataframe(invalid_dnis_df[display_cols])
                    
                    # Ofrecer opciones al usuario
                    edit_option = st.radio(
                        "¿Qué deseas hacer con los DNIs inválidos?",
                        options=["Editar manualmente", "Conservar valores originales (pueden ser carnets de extranjería u otros documentos válidos)"],
                        index=1
                    )
                    
                    if edit_option == "Editar manualmente":
                        st.subheader("Edición de DNIs Inválidos")
                        st.info("Edita los DNIs inválidos uno por uno:")
                        
                        # Determinar si se han corregido todos los DNIs
                        all_fixed = True
                        
                        # Editar DNIs uno por uno
                        for idx, row in invalid_dnis_df.iterrows():
                            # Crear una columna para cada DNI
                            col1, col2 = st.columns([3, 2])
                            
                            with col1:
                                # Mostrar información del registro
                                st.text(f"DNI Actual: {row[selection_dni_col]}")
                                st.text(f"Error: {row['DNI_Validado']}")
                                
                                # Mostrar nombre si está disponible
                                if nombre_cols:
                                    nombres_completos = " ".join([str(row[col]) for col in nombre_cols])
                                    st.text(f"Nombre: {nombres_completos}")
                                
                                # Permitir editar el DNI
                                new_dni = st.text_input(
                                    "Nuevo valor de DNI:",
                                    value=row[selection_dni_col],
                                    key=f"new_dni_{idx}"
                                )
                                
                                # Validar el nuevo valor de DNI
                                validated_dni = standardize_dni(new_dni)
                                
                            with col2:
                                # Mostrar resultado de la validación
                                if "ERROR" in validated_dni:
                                    st.error(f"⚠️ Aún inválido: {validated_dni}")
                                    all_fixed = False
                                else:
                                    st.success(f"✅ Válido: {validated_dni}")
                                
                                # Botón para aplicar cambio
                                if st.button("Actualizar", key=f"update_btn_{idx}"):
                                    selection_df.loc[idx, selection_dni_col] = validated_dni if "ERROR" not in validated_dni else new_dni
                                    selection_df.loc[idx, 'DNI_Validado'] = validated_dni
                                    st.success(f"✅ DNI actualizado")
                                    # Reemplazar experimental_rerun por rerun
                                    st.rerun()
                            
                            st.markdown("---")
                        
                        if not all_fixed:
                            st.warning("⚠️ Aún hay DNIs inválidos que no se han corregido")
                        else:
                            st.success("✅ Todos los DNIs han sido corregidos")
                else:
                    st.success("✅ Todos los DNIs en la lista de seleccionados son válidos")
            
            # Detectar columna de área
            area_cols = [col for col in df.columns if 'área' in col.lower() or 'area' in col.lower() or 'interesado' in col.lower()]
            
            if not area_cols:
                st.warning("⚠️ No se detectó ninguna columna de área o voluntariado")
                # Mostrar todas las columnas para selección manual
                area_column = st.selectbox(
                    "Selecciona la columna que contiene el área/voluntariado",
                    options=df.columns.tolist(),
                    key="area_column_selector"
                )
            else:
                area_column = st.selectbox(
                    "Selecciona la columna de área/voluntariado",
                    options=area_cols
                )
            
            # Obtener valores únicos de área
            unique_areas = df[area_column].unique().tolist()
            
            st.subheader("Filtrado por Área")
            
            # Seleccionar área a filtrar
            selected_area = st.selectbox(
                "Selecciona el área a filtrar:", 
                options=unique_areas
            )
            
            if st.button("Filtrar por Área Seleccionada"):
                try:
                    with st.spinner("Procesando filtrado por área..."):
                        # Mostrar información de depuración
                        st.info(f"Columna DNI en datos principales: '{dni_column}'")
                        st.info(f"Columna DNI en archivo de selección: '{selection_dni_col}'")
                        
                        # Capturar salida de texto de la función
                        import io
                        import sys
                        old_stdout = sys.stdout
                        new_stdout = io.StringIO()
                        sys.stdout = new_stdout
                        
                        # Filtrar por área y selección
                        filtered_df, not_found_dnis = filter_by_area_and_selection(
                            df, 
                            selection_df, 
                            area_column, 
                            selection_dni_col,
                            selected_area
                        )
                        
                        # Restaurar stdout y capturar el texto
                        sys.stdout = old_stdout
                        output_text = new_stdout.getvalue()
                        
                        # Mostrar mensajes importantes de la función
                        if "🎨 Procesando área de Arte y Cultura" in output_text:
                            st.info("🎨 Procesando Arte y Cultura - Se verificarán actualizaciones de cursos")
                        
                        for line in output_text.split('\n'):
                            if "Actualizando curso" in line or "DNIs inválidos" in line:
                                st.warning(line)
                        
                        # Guardar resultado en sesión
                        st.session_state.export_data = filtered_df
                        
                        # Mostrar resultados
                        st.success(f"✅ Filtrado completado. Se conservaron {len(filtered_df)} registros")
                        
                        # Contar cuántas filas del área se mantuvieron y cuántas se eliminaron
                        original_area_count = len(df[df[area_column] == selected_area])
                        filtered_area_count = len(filtered_df[filtered_df[area_column] == selected_area])
                        
                        st.info(f"📊 Área '{selected_area}': {filtered_area_count} de {original_area_count} yakus conservados")
                        
                        # Mostrar DNIs no encontrados
                        if not_found_dnis:
                            st.warning(f"⚠️ {len(not_found_dnis)} DNIs del archivo de selección no se encontraron en el área '{selected_area}':")
                            st.write(not_found_dnis)
                        
                        # Mostrar vista previa
                        st.subheader("Vista Previa de Datos Filtrados")
                        st.dataframe(filtered_df.head(10))
                        
                        # Botón para continuar
                        st.success("✅ Datos filtrados correctamente. Puedes continuar a la pestaña de exportación.")
                except Exception as e:
                    st.error(f"❌ Error al filtrar por área: {str(e)}")
        
        except Exception as e:
            st.error(f"❌ Error al procesar el archivo de selección: {str(e)}")

def export_tab():
    """Tab para exportación de datos procesados"""
    st.header("Exportación de Datos")
    
    # Determinar qué datos exportar (procesados o filtrados por área)
    data_to_export = None
    
    if st.session_state.export_data is not None:
        data_to_export = st.session_state.export_data
        st.success("✅ Se exportarán los datos filtrados por área")
    
    elif st.session_state.processed_data is not None:
        data_to_export = st.session_state.processed_data
        st.info("ℹ️ Se exportarán los datos procesados (sin filtrado por área)")
    
    else:
        st.warning("⚠️ No hay datos para exportar. Procesa los datos en las pestañas anteriores.")
        return
    
    # Opciones de exportación
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
        export_df = data_to_export.copy()
        
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
        
        # Exportar según formato
        if export_format == "Excel (.xlsx)":
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                export_df.to_excel(writer, sheet_name='Datos', index=False)
            
            output.seek(0)
            b64 = base64.b64encode(output.read()).decode()
            href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{export_filename}.xlsx">📥 Descargar archivo Excel</a>'
            st.markdown(href, unsafe_allow_html=True)
        
        else:  # CSV
            csv = export_df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:text/csv;base64,{b64}" download="{export_filename}.csv">📥 Descargar archivo CSV</a>'
            st.markdown(href, unsafe_allow_html=True)
        
        st.success(f"✅ Archivo '{export_filename}' listo para descargar")
        
        # Resumen de datos exportados
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