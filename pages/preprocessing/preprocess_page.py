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
                                    st.dataframe(duplicates[[dni_column, 'DNI_Validado']])
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
                
                # Mostrar vista previa
                st.subheader("Vista Previa de Datos Procesados")
                st.dataframe(filtered_df.head(10))
                
                # Botón para continuar
                st.success("✅ Datos procesados correctamente. Puedes continuar a la siguiente pestaña.")
        
        except Exception as e:
            st.error(f"❌ Error al procesar el archivo: {str(e)}")

def selection_by_area_tab():
    """Tab para selección de yakus por área"""
    st.header("Selección de Yakus por Área")
    
    # Verificar si hay datos procesados
    if st.session_state.processed_data is None:
        st.warning("⚠️ Primero debes cargar y procesar los datos en la pestaña anterior")
        return
    
    # Datos procesados
    df = st.session_state.processed_data
    
    # Cargar archivo de selección
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
            
            # Mostrar columnas disponibles en el archivo de selección
            st.subheader("Columna de DNI en Archivo de Selección")
            
            # Detectar columnas de DNI
            selection_dni_cols = [col for col in selection_df.columns if 'dni' in col.lower() or 'pasaporte' in col.lower()]
            
            if not selection_dni_cols:
                st.warning("⚠️ No se detectó ninguna columna de DNI o Pasaporte en el archivo de selección")
                # Mostrar todas las columnas para selección manual
                selection_dni_col = st.selectbox(
                    "Selecciona la columna que contiene los DNIs/Pasaportes",
                    options=selection_df.columns.tolist()
                )
            else:
                selection_dni_col = st.selectbox(
                    "Selecciona la columna de DNI/Pasaporte",
                    options=selection_dni_cols
                )
            
            # Convertir explícitamente a string la columna DNI del archivo de selección
            selection_df[selection_dni_col] = selection_df[selection_dni_col].astype(str)
            
            # Detectar columna de DNI en datos procesados
            dni_column = None
            if 'DNI_Validado' in df.columns:
                dni_column = 'DNI_Validado'
            else:
                # Buscar columna de DNI
                dni_cols = [col for col in df.columns if 'dni' in col.lower() or 'pasaporte' in col.lower()]
                if dni_cols:
                    dni_column = dni_cols[0]
            
            if dni_column is None:
                st.error("❌ No se encontró una columna de DNI en los datos procesados")
                return
            
            # Convertir explícitamente a string la columna DNI de los datos procesados
            df[dni_column] = df[dni_column].astype(str)
            
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
                        # Filtrar por área y selección
                        filtered_df, not_found_dnis = filter_by_area_and_selection(
                            df, 
                            selection_df, 
                            area_column, 
                            selection_dni_col, 
                            selected_area
                        )
                        
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