import streamlit as st
import pandas as pd
import numpy as np
import re
import os
import sys
import io
from pages.preprocessing.components.file_handlers import export_dataframe

# Importamos las funciones de utilidad
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
from utils.data_processors import (
    standardize_dni, filter_by_area_and_selection
)

def selection_by_area_tab():
    """Tab para selección de yakus por área"""
    st.header("Selección de Yakus por Área")
    
    # Obtener la fuente de datos
    df = get_data_source()
    
    if df is None:
        st.warning("⚠️ Necesitas cargar datos procesados para continuar")
        return
    
    # Detectar columna de DNI en datos procesados
    dni_column = detect_dni_column_in_data(df)
    
    if not dni_column:
        st.error("❌ No se pudo identificar una columna de DNI válida")
        return
    
    # Convertir explícitamente a string la columna DNI de los datos procesados
    df[dni_column] = df[dni_column].astype(str)
    
    # VISUALIZACIÓN PARCIAL DE DATOS PRINCIPALES
    with st.expander("Visualización de Datos Principales", expanded=False):
        st.subheader("Archivo de Datos Principales")
        st.dataframe(df)
    
    # Cargar archivo de selección
    selection_df = load_selection_file()
    
    if selection_df is None:
        return
    
    # Detectar columna de DNI en archivo de selección
    selection_dni_col = detect_dni_column_in_selection(selection_df)
    
    if not selection_dni_col:
        st.error("❌ No se pudo identificar una columna de DNI válida en el archivo de selección")
        return
    
    # Convertir explícitamente a string la columna DNI del archivo de selección
    selection_df[selection_dni_col] = selection_df[selection_dni_col].astype(str)
    
    # Validar DNIs en la lista de seleccionados
    selection_df = validate_selection_dnis(selection_df, selection_dni_col)
    
    # Detectar columna de área
    area_column = detect_area_column(df)
    
    if not area_column:
        st.error("❌ No se pudo identificar una columna de área válida")
        return
    
    # Obtener valores únicos de área
    unique_areas = df[area_column].unique().tolist()
    
    st.subheader("Filtrado por Área")
    
    # Seleccionar área a filtrar
    selected_area = st.selectbox(
        "Selecciona el área a filtrar:", 
        options=unique_areas
    )
    
    if st.button("Filtrar por Área Seleccionada"):
        process_area_filtering(df, selection_df, area_column, selection_dni_col, selected_area, dni_column)

def get_data_source():
    """Determina la fuente de datos a utilizar."""
    st.subheader("Fuente de Datos")
    
    if st.session_state.processed_data is not None:
        # Si hay datos de la sesión actual, ofrecer usarlos como opción
        usar_datos_sesion = st.checkbox(
            "Usar datos procesados del paso anterior", 
            value=True,
            key="usar_datos_sesion"
        )
        
        if usar_datos_sesion:
            df = st.session_state.processed_data
            st.success("✅ Usando datos procesados del paso anterior")
            st.info(f"📊 Registros: {len(df)} | Columnas: {len(df.columns)}")
            return df
    
    # Siempre ofrecer la opción de cargar archivo de datos
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
            
            st.success(f"✅ Archivo de datos procesados cargado: {uploaded_processed.name}")
            st.info(f"📊 Registros: {len(df)} | Columnas: {len(df.columns)}")
            
            # Actualizar datos procesados en la sesión
            st.session_state.processed_data = df
            return df
        
        except Exception as e:
            st.error(f"❌ Error al procesar el archivo: {str(e)}")
    
    return None

def detect_dni_column_in_data(df):
    """Detecta la columna de DNI en los datos procesados."""
    if 'DNI_Validado' in df.columns:
        return 'DNI_Validado'
    
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
        return dni_column
    else:
        # Si aún no encuentra, ofrecer selección manual
        st.warning("⚠️ No se detectó automáticamente una columna de DNI en los datos principales. Por favor, selecciona la columna manualmente.")
        
        dni_column = st.selectbox(
            "Selecciona la columna que contiene los DNIs en los datos principales:",
            options=df.columns.tolist(),
            key="dni_column_main_data"
        )
        return dni_column

def load_selection_file():
    """Carga el archivo de selección de DNIs."""
    st.subheader("Archivo de DNIs Seleccionados")
    
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
            
            # VISUALIZACIÓN DEL ARCHIVO DE SELECCIÓN
            with st.expander("Visualización de Archivo de Selección", expanded=False):
                st.subheader("Archivo de DNIs Seleccionados")
                st.dataframe(selection_df)
            
            return selection_df
        
        except Exception as e:
            st.error(f"❌ Error al procesar el archivo de selección: {str(e)}")
    
    return None

def detect_dni_column_in_selection(selection_df):
    """Detecta la columna de DNI en el archivo de selección."""
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
    
    return selection_dni_col

def validate_selection_dnis(selection_df, selection_dni_col):
    """Valida los DNIs en el archivo de selección."""
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
                selection_df = edit_invalid_dnis(selection_df, invalid_dnis_df, selection_dni_col, nombre_cols)
        else:
            st.success("✅ Todos los DNIs en la lista de seleccionados son válidos")
    
    return selection_df

def edit_invalid_dnis(selection_df, invalid_dnis_df, selection_dni_col, nombre_cols):
    """Permite editar los DNIs inválidos."""
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
                # Guardar el nuevo valor tanto en la columna original como en la validada
                new_valid_value = validated_dni if "ERROR" not in validated_dni else new_dni
                selection_df.loc[idx, selection_dni_col] = new_valid_value
                selection_df.loc[idx, 'DNI_Validado'] = new_valid_value
                st.success(f"✅ DNI actualizado en ambas columnas")
                st.rerun()
        
        st.markdown("---")
    
    if not all_fixed:
        st.warning("⚠️ Aún hay DNIs inválidos que no se han corregido")
    else:
        st.success("✅ Todos los DNIs han sido corregidos")
    
    return selection_df

def detect_area_column(df):
    """Detecta la columna de área en los datos procesados."""
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
    
    return area_column

def process_area_filtering(df, selection_df, area_column, selection_dni_col, selected_area, dni_column):
    """Procesa el filtrado por área seleccionada."""
    try:
        with st.spinner("Procesando filtrado por área..."):
            # Mostrar información de depuración
            st.info(f"Columna DNI en datos principales: '{dni_column}'")
            st.info(f"Columna DNI en archivo de selección: '{selection_dni_col}'")
            
            # Capturar salida de texto de la función
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
            
            # Asegurarse de actualizar processed_data también para mantener la coherencia
            st.session_state.processed_data = filtered_df
            
            # Mostrar resultados
            st.success(f"✅ Filtrado completado. Se conservaron {len(filtered_df)} registros")
            
            # Contar cuántas filas del área se mantuvieron y cuántas se eliminaron
            original_area_count = len(df[df[area_column] == selected_area])
            filtered_area_count = len(filtered_df[filtered_df[area_column] == selected_area])
            
            st.info(f"📊 Área '{selected_area}': {filtered_area_count} de {original_area_count} yakus conservados")
            
            # Procesar DNIs no encontrados
            if not_found_dnis:
                handle_not_found_dnis(not_found_dnis, df, selection_df, selection_dni_col, selected_area, area_column)
            
            # Mostrar vista previa
            st.subheader("Vista Previa de Datos Filtrados")
            st.dataframe(filtered_df.head(10))
    except Exception as e:
        st.error(f"❌ Error al filtrar por área: {str(e)}")

def handle_not_found_dnis(not_found_dnis, df, selection_df, selection_dni_col, selected_area, area_column):
    """Maneja los DNIs no encontrados en el área seleccionada."""
    st.warning(f"⚠️ {len(not_found_dnis)} DNIs del archivo de selección no se encontraron en el área '{selected_area}'")
    
    # Crear DataFrame con información de los DNIs no encontrados para mejor visualización
    not_found_info = []
    
    for dni in not_found_dnis:
        # Buscar información en el archivo de selección para identificar quién es
        selection_rows = selection_df[selection_df[selection_dni_col] == dni]
        
        info = {"DNI": dni}
        
        # Añadir información adicional si está disponible
        nombre_cols = [col for col in selection_df.columns if 'nombre' in col.lower() or 'apellido' in col.lower()]
        
        if not selection_rows.empty:
            if nombre_cols:
                # Concatenar nombres/apellidos
                nombres = []
                for col in nombre_cols:
                    if col in selection_rows.columns:
                        nombres.append(str(selection_rows[col].iloc[0]))
                info["Nombre"] = " ".join(nombres)
            
            # Añadir más información útil si existe
            for col_type, pattern in [
                ("Correo", ['correo', 'email']),
                ("Teléfono", ['telefono', 'teléfono', 'celular']),
                ("Curso", ['curso', 'taller', 'especialidad'])
            ]:
                cols = [col for col in selection_rows.columns if any(p in col.lower() for p in pattern)]
                if cols:
                    info[col_type] = str(selection_rows[cols[0]].iloc[0])
        
        not_found_info.append(info)
    
    # Crear DataFrame para mostrar
    not_found_df = pd.DataFrame(not_found_info)
    
    # Mostrar tabla de no encontrados
    st.subheader("Detalles de DNIs no encontrados")
    st.dataframe(not_found_df)
    
    # Sección para buscar en todas las áreas
    st.subheader("Buscar en todas las áreas")
    st.info("Verifica si estos yakus existen en otras áreas")
    
    # Permitir seleccionar un DNI para buscar
    dni_to_search = st.selectbox(
        "Selecciona un DNI para buscar en todas las áreas:",
        options=not_found_dnis,
        key="dni_to_search"
    )
    
    if st.button("Buscar en todas las áreas", key="search_all_areas"):
        search_dni_in_all_areas(dni_to_search, df, not_found_info, area_column, selected_area)

def search_dni_in_all_areas(dni_to_search, df, not_found_info, area_column, selected_area):
    """Busca un DNI en todas las áreas."""
    # Buscar el DNI en todo el DataFrame principal
    all_matches = []
    
    # Buscar en la columna validada si existe
    if 'DNI_Validado' in df.columns:
        matches_validated = df[df['DNI_Validado'] == dni_to_search]
        if not matches_validated.empty:
            all_matches.append(matches_validated)
    
    # Buscar en cualquier columna con "dni" en el nombre
    dni_cols = [col for col in df.columns if 'dni' in col.lower() or 'doc' in col.lower() or 'pasaporte' in col.lower()]
    for col in dni_cols:
        matches_col = df[df[col] == dni_to_search]
        if not matches_col.empty:
            # Añadir solo si no duplicamos las filas
            if not all_matches:
                all_matches.append(matches_col)
            else:
                new_indices = set(matches_col.index) - set(all_matches[0].index)
                if new_indices:
                    all_matches.append(matches_col.loc[list(new_indices)])
    
    # Buscar aproximado por si hay problemas de formato
    if not all_matches:
        # Intentar buscar sin espacios, eliminando "DNI", etc.
        clean_dni = re.sub(r'[^0-9A-Za-z]', '', dni_to_search)
        for col in dni_cols:
            for idx, row in df.iterrows():
                row_dni = str(row[col])
                row_clean = re.sub(r'[^0-9A-Za-z]', '', row_dni)
                if clean_dni in row_clean:
                    all_matches.append(df.loc[[idx]])
    
    # Combinar todos los resultados
    if all_matches:
        combined_matches = pd.concat(all_matches).drop_duplicates()
        
        st.success(f"✅ Se encontraron {len(combined_matches)} coincidencias en la base de datos")
        
        # Mostrar áreas donde se encontró
        if area_column in combined_matches.columns:
            areas_found = combined_matches[area_column].unique()
            st.info(f"📌 Áreas donde se encontró: {', '.join(areas_found)}")
        
        # Mostrar los resultados completos
        st.write("Resultados encontrados:")
        st.dataframe(combined_matches)
        
        # Opción para añadir este registro al área seleccionada
        if st.button("Añadir este registro al área seleccionada", key="add_to_area"):
            # Crear una copia del DataFrame principal
            modified_df = df.copy()
            
            # Para cada fila encontrada, cambiar el área
            for idx in combined_matches.index:
                # Cambiar el área a la seleccionada
                modified_df.loc[idx, area_column] = selected_area
            
            # Guardar el DataFrame modificado en la sesión
            st.session_state.processed_data = modified_df
            
            st.success("✅ Registro añadido al área seleccionada. Vuelve a filtrar para ver los resultados actualizados.")
            
            # Sugerir refiltrar
            if st.button("Volver a filtrar", key="refilter_btn"):
                st.rerun()
    else:
        st.warning(f"⚠️ No se encontró ninguna coincidencia para el DNI {dni_to_search} en toda la base de datos.")
        
        # Opción para buscar por nombre si tenemos esa información
        nombre_to_search = ""
        for info in not_found_info:
            if info["DNI"] == dni_to_search and "Nombre" in info:
                nombre_to_search = info["Nombre"]
                break
        
        if nombre_to_search:
            search_by_name(nombre_to_search, df)

def search_by_name(nombre_to_search, df):
    """Busca por nombre en el DataFrame principal."""
    st.subheader("Buscar por nombre")
    st.info(f"Intentaremos buscar por el nombre: {nombre_to_search}")
    
    # Separar palabras del nombre para buscar coincidencias parciales
    nombre_parts = nombre_to_search.lower().split()
    
    if st.button("Buscar por nombre", key="search_by_name"):
        # Buscar en todas las columnas de nombre
        nombre_cols = [col for col in df.columns if 'nombre' in col.lower() or 'apellido' in col.lower()]
        
        matches_by_name = []
        for col in nombre_cols:
            for part in nombre_parts:
                if len(part) > 3:  # Solo usar partes significativas
                    # Buscar coincidencias parciales
                    matches = df[df[col].str.lower().str.contains(part, na=False)]
                    if not matches.empty:
                        matches_by_name.append(matches)
        
        if matches_by_name:
            # Combinar resultados
            combined_name_matches = pd.concat(matches_by_name).drop_duplicates()
            
            st.success(f"✅ Se encontraron {len(combined_name_matches)} posibles coincidencias por nombre")
            st.dataframe(combined_name_matches)
        else:
            st.error("❌ No se encontraron coincidencias por nombre.") 