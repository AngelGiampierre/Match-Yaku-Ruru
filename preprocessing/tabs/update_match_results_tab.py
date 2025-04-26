"""
Pestaña para actualizar un archivo de resultados de Match existente POR ÁREA.

Permite añadir Rurus nuevos del área correspondiente y corregir/actualizar
información de contacto basándose en un archivo de Rurus transformados actualizado.
"""
import streamlit as st
import pandas as pd
from io import BytesIO
import numpy as np # Para manejar NaN de forma más explícita

# --- Funciones Auxiliares (Incluyendo limpieza de números) ---

def clean_str_number(val):
    """Limpia números leídos de Excel, convirtiéndolos a string limpio."""
    if pd.isna(val) or val == '':
        return '' # Devolver vacío para nulos o vacíos
    try:
        # Intentar convertir a float, luego a entero, luego a string
        cleaned_val = str(int(float(str(val))))
    except (ValueError, TypeError):
        # Si falla, usar el string original limpio
        cleaned_val = str(val).strip()
    # Eliminar '.0' residual por si acaso
    if cleaned_val.endswith('.0'):
        cleaned_val = cleaned_val[:-2]
    return cleaned_val

def load_and_validate_results(uploaded_file, area_name):
    """Carga las 3 hojas esperadas del archivo de resultados del match para un área."""
    data = {}
    sheet_names = ["Asignaciones", "Yakus No Asignados", "Rurus No Asignados"]
    try:
        xls = pd.ExcelFile(uploaded_file)
        for sheet in sheet_names:
            if sheet in xls.sheet_names:
                data[sheet] = pd.read_excel(xls, sheet_name=sheet)
            else:
                st.warning(f"Advertencia: No se encontró la hoja '{sheet}' en el archivo de resultados de {area_name}. Se creará vacía si es necesario.")
                data[sheet] = pd.DataFrame() # Crear DataFrame vacío si falta la hoja
        st.success(f"Archivo de resultados para '{area_name}' cargado.")
        return data
    except Exception as e:
        st.error(f"Error al leer el archivo de resultados del Match para '{area_name}': {e}")
        return None

def load_transformed_rurus(uploaded_file):
    """Carga el archivo actualizado de Rurus transformados."""
    try:
        df = pd.read_excel(uploaded_file)
        # Validar columnas mínimas necesarias para la actualización
        required_cols = ['ID del estudiante:', 'celular', 'celular_asesoria', 'DNI', 'nombre', 'apellido', 'area']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            st.error(f"Error: El archivo de Rurus transformados no contiene las columnas necesarias: {', '.join(missing)}")
            return None
        st.success("Archivo de Rurus transformados cargado.")
        # Convertir la columna ID a string para asegurar el merge
        df['ID del estudiante:'] = df['ID del estudiante:'].astype(str)
        return df
    except Exception as e:
        st.error(f"Error al leer el archivo de Rurus transformados: {e}")
        return None

def generate_updated_excel(data_results, data_rurus_all, area_filter):
    """Procesa los datos para UN ÁREA específica y genera el nuevo archivo Excel."""

    if not data_results or not isinstance(data_rurus_all, pd.DataFrame):
        st.error("Faltan datos para procesar.")
        return None

    # Filtrar rurus transformados por el área seleccionada
    rurus_area_filtered = data_rurus_all[data_rurus_all['area'] == area_filter].copy()
    if rurus_area_filtered.empty:
         st.warning(f"No se encontraron Rurus para el área '{area_filter}' en el archivo de Rurus Transformados.")
         # Podríamos continuar solo para formatear los existentes o detenernos.
         # Continuaremos formateando por si acaso.

    df_asignaciones = data_results.get("Asignaciones", pd.DataFrame()).copy()
    df_yakus_no_asignados = data_results.get("Yakus No Asignados", pd.DataFrame()).copy()
    df_rurus_no_asignados_orig = data_results.get("Rurus No Asignados", pd.DataFrame()).copy()

    # --- 1. Identificar IDs existentes EN ESTE ARCHIVO DE RESULTADOS ---
    existing_ruru_ids_area = set()
    if 'ID Ruru' in df_asignaciones.columns:
        df_asignaciones['ID Ruru'] = df_asignaciones['ID Ruru'].astype(str) # Asegurar tipo
        existing_ruru_ids_area.update(df_asignaciones['ID Ruru'].unique())
    if 'ID del estudiante:' in df_rurus_no_asignados_orig.columns:
        df_rurus_no_asignados_orig['ID del estudiante:'] = df_rurus_no_asignados_orig['ID del estudiante:'].astype(str) # Asegurar tipo
        existing_ruru_ids_area.update(df_rurus_no_asignados_orig['ID del estudiante:'].unique())

    # --- 2. Identificar Rurus nuevos PARA ESTA ÁREA ---
    # Usar los rurus ya filtrados por área
    df_nuevos_rurus_area = rurus_area_filtered[~rurus_area_filtered['ID del estudiante:'].isin(existing_ruru_ids_area)].copy()
    st.info(f"Se identificaron {len(df_nuevos_rurus_area)} Rurus nuevos para añadir a '{area_filter}'.")

    # --- 3. Preparar Fuente de Contactos (Seguimos usando el DF completo de Rurus) ---
    # Es más seguro buscar por ID en la lista completa por si hay errores de tipeo en 'area' en archivos viejos
    ruru_contact_source = data_rurus_all[['ID del estudiante:', 'celular', 'celular_asesoria', 'DNI']].copy()
    ruru_contact_source['Celular Apoderado Ruru_clean'] = ruru_contact_source['celular'].apply(clean_str_number)
    ruru_contact_source['Celular Asesoria Ruru_clean'] = ruru_contact_source['celular_asesoria'].apply(clean_str_number)
    ruru_contact_source['DNI_ruru_clean'] = ruru_contact_source['DNI'].apply(clean_str_number)
    ruru_contact_source = ruru_contact_source[['ID del estudiante:', 'Celular Apoderado Ruru_clean', 'Celular Asesoria Ruru_clean', 'DNI_ruru_clean']]

    # --- 4. Corregir/Actualizar Hoja Asignaciones ---
    if not df_asignaciones.empty and 'ID Ruru' in df_asignaciones.columns:
         df_asignaciones['ID Ruru'] = df_asignaciones['ID Ruru'].astype(str) # Asegurar tipo string
         # Eliminar columnas de contacto viejas si existen para evitar duplicados en merge
         cols_to_drop = ['Celular Apoderado Ruru', 'Celular Asesoria Ruru', 'DNI Ruru']
         df_asignaciones = df_asignaciones.drop(columns=[col for col in cols_to_drop if col in df_asignaciones.columns], errors='ignore')
         # Hacer merge para obtener contactos limpios
         df_asignaciones = pd.merge(
             df_asignaciones,
             ruru_contact_source,
             left_on='ID Ruru',
             right_on='ID del estudiante:',
             how='left'
         )
         # Renombrar columnas limpias a los nombres finales
         df_asignaciones = df_asignaciones.rename(columns={
             'Celular Apoderado Ruru_clean': 'Celular Apoderado Ruru',
             'Celular Asesoria Ruru_clean': 'Celular Asesoria Ruru',
             'DNI_ruru_clean': 'DNI Ruru'
         })
         # Eliminar la columna ID extra del merge
         if 'ID del estudiante:' in df_asignaciones.columns:
             df_asignaciones = df_asignaciones.drop(columns=['ID del estudiante:'])
         # Opcional: limpiar DNI Yaku y Celular Yaku si existen
         if 'dni' in df_asignaciones.columns: # Nombre esperado post-match
             df_asignaciones['DNI Yaku'] = df_asignaciones['dni'].apply(clean_str_number)
         if 'Celular Yaku' in df_asignaciones.columns:
             df_asignaciones['Celular Yaku'] = df_asignaciones['Celular Yaku'].apply(clean_str_number)


    # --- 5. Corregir/Actualizar Hoja Rurus No Asignados (Existentes) ---
    if not df_rurus_no_asignados_orig.empty and 'ID del estudiante:' in df_rurus_no_asignados_orig.columns:
        df_rurus_no_asignados_orig['ID del estudiante:'] = df_rurus_no_asignados_orig['ID del estudiante:'].astype(str)
        # Eliminar columnas de contacto viejas
        cols_to_drop = ['Celular Apoderado Ruru', 'Celular Asesoria Ruru', 'DNI'] # DNI podría llamarse así aquí
        df_rurus_no_asignados_orig = df_rurus_no_asignados_orig.drop(columns=[col for col in cols_to_drop if col in df_rurus_no_asignados_orig.columns], errors='ignore')
        # Hacer merge
        df_rurus_no_asignados_orig = pd.merge(
            df_rurus_no_asignados_orig,
            ruru_contact_source,
            on='ID del estudiante:',
            how='left'
        )
         # Renombrar columnas limpias
        df_rurus_no_asignados_orig = df_rurus_no_asignados_orig.rename(columns={
             'Celular Apoderado Ruru_clean': 'Celular Apoderado Ruru',
             'Celular Asesoria Ruru_clean': 'Celular Asesoria Ruru',
             'DNI_ruru_clean': 'DNI' # Mantener DNI como nombre de columna aquí? Ajustar si es necesario
         })


    # --- 6. Preparar Nuevos Rurus (del área) para Concatenar ---
    df_nuevos_rurus_formated = pd.DataFrame()
    if not df_nuevos_rurus_area.empty:
        # Usar las columnas del DF de Rurus No Asignados original como plantilla
        target_cols_rurus_no_asignados = df_rurus_no_asignados_orig.columns.tolist()
        if not target_cols_rurus_no_asignados and not df_nuevos_rurus_area.empty:
            # Si la hoja original estaba vacía pero hay nuevos, inferir columnas de los nuevos
            # o usar un set predefinido. Usaremos uno básico.
            st.warning("Hoja 'Rurus No Asignados' original estaba vacía. Usando columnas básicas para nuevos Rurus.")
            target_cols_rurus_no_asignados = [
                'ID del estudiante:', 'nombre', 'apellido', 'DNI', 'area',
                'grado_original', 'quechua', 'Celular Apoderado Ruru', 'Celular Asesoria Ruru'
                # Añadir más si se sabe que deben estar
            ]

        # Mapeo (Ajustar si los nombres en df_nuevos_rurus_area son diferentes)
        column_map_new_rurus = {
            'ID del estudiante:': 'ID del estudiante:',
            'nombre': 'nombre',
            'apellido': 'apellido',
            'DNI': 'DNI',
            'area': 'area',
            'grado_original': 'grado_original',
            'quechua': 'quechua',
            'celular': 'Celular Apoderado Ruru',
            'celular_asesoria': 'Celular Asesoria Ruru',
            # Mapear horarios, opciones, etc. si están en el archivo transformado y son necesarios aquí
             'horario_lunes': 'horario_lunes',
             # ... añadir resto de horarios, asignaturas, talleres ...
        }
        # Renombrar y seleccionar columnas que existen en el mapeo y en el DF de nuevos
        cols_to_rename = {k: v for k, v in column_map_new_rurus.items() if k in df_nuevos_rurus_area.columns}
        df_nuevos_rurus_formated = df_nuevos_rurus_area.rename(columns=cols_to_rename)

        # Limpiar números en las columnas renombradas
        for col in ['Celular Apoderado Ruru', 'Celular Asesoria Ruru', 'DNI']:
             if col in df_nuevos_rurus_formated.columns:
                  df_nuevos_rurus_formated[col] = df_nuevos_rurus_formated[col].apply(clean_str_number)

        # Asegurar que solo tenemos las columnas de la hoja destino
        final_new_ruru_cols = [col for col in target_cols_rurus_no_asignados if col in df_nuevos_rurus_formated.columns]
        df_nuevos_rurus_formated = df_nuevos_rurus_formated[final_new_ruru_cols]


    # --- 7. Combinar Rurus No Asignados ---
    # Asegurar que ambas partes tengan las mismas columnas antes de concatenar
    cols_final = df_rurus_no_asignados_orig.columns.union(df_nuevos_rurus_formated.columns)
    df_rurus_no_asignados_orig = df_rurus_no_asignados_orig.reindex(columns=cols_final, fill_value='')
    df_nuevos_rurus_formated = df_nuevos_rurus_formated.reindex(columns=cols_final, fill_value='')

    df_rurus_no_asignados_final = pd.concat([df_rurus_no_asignados_orig, df_nuevos_rurus_formated], ignore_index=True)
    # Eliminar duplicados por ID por si acaso
    df_rurus_no_asignados_final = df_rurus_no_asignados_final.drop_duplicates(subset=['ID del estudiante:'], keep='first')


    # --- 8. Formatear Yakus No Asignados ---
    if not df_yakus_no_asignados.empty:
        cols_to_clean_yaku = ['dni', 'celular']
        for col in cols_to_clean_yaku:
            if col in df_yakus_no_asignados.columns:
                df_yakus_no_asignados[col] = df_yakus_no_asignados[col].apply(clean_str_number)

    # --- 9. Generar Salida Excel ---
    output_buffer = BytesIO()
    with pd.ExcelWriter(output_buffer, engine='xlsxwriter') as writer:
        df_asignaciones.to_excel(writer, sheet_name='Asignaciones', index=False)
        df_yakus_no_asignados.to_excel(writer, sheet_name='Yakus No Asignados', index=False)
        df_rurus_no_asignados_final.to_excel(writer, sheet_name='Rurus No Asignados', index=False)

    output_buffer.seek(0)
    return output_buffer

# --- Función Principal de la Pestaña ---

def update_match_results_tab():
    """Renderiza la pestaña para actualizar resultados del Match."""
    st.header("Actualizar Resultados del Match por Área")
    st.write("""
    Carga el archivo Excel de resultados de un área específica y un archivo
    actualizado de TODOS los Rurus (salida del tab de Transformación).
    Esta herramienta añadirá los Rurus nuevos DEL ÁREA SELECCIONADA a la lista
    de no asignados y corregirá el formato de los números de contacto en todas las hojas.
    """)

    # Estado de sesión
    if 'results_data_upd' not in st.session_state: st.session_state.results_data_upd = None
    if 'rurus_data_upd' not in st.session_state: st.session_state.rurus_data_upd = None
    if 'updated_excel_output_upd' not in st.session_state: st.session_state.updated_excel_output_upd = None
    if 'selected_area_upd' not in st.session_state: st.session_state.selected_area_upd = None

    # Selector de Área
    area_options = ["Asesoría a Colegios Nacionales", "Arte & Cultura", "Bienestar Psicológico"]
    selected_area = st.selectbox("Selecciona el Área del archivo de resultados a actualizar:", area_options, key="area_selector_upd")

    # Reiniciar si cambia el área
    if st.session_state.selected_area_upd != selected_area:
        st.session_state.results_data_upd = None # Limpiar resultados anteriores
        st.session_state.updated_excel_output_upd = None
        st.session_state.selected_area_upd = selected_area
        # No necesitamos limpiar rurus_data si es el mismo archivo siempre

    # File Uploaders
    uploaded_results = st.file_uploader(f"1. Cargar archivo Excel de Resultados del Match ({selected_area})", type=["xlsx", "xls"], key=f"update_results_upload_{selected_area}")
    uploaded_rurus = st.file_uploader("2. Cargar archivo Excel de Rurus Transformados (Completo y Actualizado)", type=["xlsx", "xls"], key="update_rurus_upload_all")

    # Cargar datos
    if uploaded_results:
        # Solo recargar si el área coincide con el archivo subido
        if st.session_state.selected_area_upd == selected_area:
             st.session_state.results_data_upd = load_and_validate_results(uploaded_results, selected_area)
    if uploaded_rurus:
         st.session_state.rurus_data_upd = load_transformed_rurus(uploaded_rurus) # Carga el archivo completo

    # Botón para procesar
    st.markdown("---")
    if st.session_state.results_data_upd is not None and st.session_state.rurus_data_upd is not None:
        st.info(f"Listo para actualizar el archivo de resultados del área: **{selected_area}**.")
        if st.button("Generar Archivo Actualizado", key="update_button"):
            with st.spinner(f"Procesando actualización para {selected_area}..."):
                st.session_state.updated_excel_output_upd = generate_updated_excel(
                    st.session_state.results_data_upd,
                    st.session_state.rurus_data_upd, # Pasar el DF completo de Rurus
                    selected_area # Pasar el área seleccionada para filtrar
                )
                if st.session_state.updated_excel_output_upd:
                    st.success(f"¡Archivo Excel para '{selected_area}' actualizado generado!")
                else:
                    st.error("No se pudo generar el archivo actualizado.")
    else:
        st.info("Carga ambos archivos (Resultados del área seleccionada y Rurus Transformados) para habilitar la actualización.")

    # Botón de descarga
    if st.session_state.updated_excel_output_upd:
        st.markdown("---")
        st.download_button(
            label=f"Descargar Resultados Actualizados ({selected_area})",
            data=st.session_state.updated_excel_output_upd.getvalue(),
            file_name=f"Resultados_Match_{selected_area.replace(' ', '_')}_Actualizados.xlsx", # Nombre incluye área
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download_updated_results"
        ) 